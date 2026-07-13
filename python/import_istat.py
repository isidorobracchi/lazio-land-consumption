from pathlib import Path

import geopandas as gpd
from sqlalchemy import create_engine, text


PROJECT_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "Com01012026_g"
    / "Com01012026_g_WGS84.shp"
)

DATABASE_URL = (
    "postgresql+psycopg2://"
    "gis_user:gis_password@localhost:5432/lazio_gis"
)

RAW_SCHEMA = "raw"
RAW_TABLE = "comuni_istat_2026"

PROCESSED_SCHEMA = "processed"
PROCESSED_TABLE = "comuni_lazio_2026"


def main() -> None:
    if not INPUT_FILE.exists():
        raise FileNotFoundError(
            f"Shapefile non trovato:\n{INPUT_FILE}"
        )

    print(f"Lettura del file:\n{INPUT_FILE}")

    comuni = gpd.read_file(INPUT_FILE)

    print(f"Comuni italiani letti: {len(comuni)}")
    print(f"CRS originale: {comuni.crs}")

    # Manteniamo separata la colonna geometrica
    geometry_column = comuni.geometry.name

    # Convertiamo in minuscolo solo i campi attributo
    comuni = comuni.rename(
        columns={
            column: column.lower()
            for column in comuni.columns
            if column != geometry_column
        }
    )

    # Rinominiamo la geometria e la manteniamo attiva
    comuni = comuni.rename_geometry("geom")

    if "cod_reg" not in comuni.columns:
        raise KeyError(
            "Il campo 'cod_reg' non è presente nel file ISTAT."
        )

    # Selezione del Lazio
    lazio = comuni.loc[
        comuni["cod_reg"]
        .astype(str)
        .str.strip()
        .eq("12")
    ].copy()

    print(f"Comuni del Lazio trovati: {len(lazio)}")

    if len(lazio) != 378:
        raise ValueError(
            f"Attesi 378 comuni del Lazio, trovati {len(lazio)}."
        )

    if lazio.crs is None:
        raise ValueError(
            "Il file ISTAT non ha un CRS definito."
        )

    if lazio.crs.to_epsg() != 32632:
        print("Conversione del CRS in EPSG:32632...")
        lazio = lazio.to_crs(epsg=32632)

    # Rimuove un eventuale id artificiale
    lazio = lazio.drop(
        columns=["id"],
        errors="ignore",
    )

    engine = create_engine(DATABASE_URL)

    print(
        f"Caricamento in "
        f"{RAW_SCHEMA}.{RAW_TABLE}..."
    )

    lazio.to_postgis(
        name=RAW_TABLE,
        con=engine,
        schema=RAW_SCHEMA,
        if_exists="replace",
        index=False,
        chunksize=500,
    )

    processing_sql = f"""
    DROP TABLE IF EXISTS
        {PROCESSED_SCHEMA}.{PROCESSED_TABLE};

    CREATE TABLE
        {PROCESSED_SCHEMA}.{PROCESSED_TABLE} AS
    SELECT
        pro_com_t::text AS codice_comune,
        comune AS nome_comune,
        cod_reg::integer AS codice_regione,
        cod_uts::integer AS codice_provincia,
        ST_Multi(
            ST_MakeValid(geom)
        )::geometry(MultiPolygon, 32632) AS geom,
        ST_Area(geom) / 1000000.0 AS superficie_km2
    FROM {RAW_SCHEMA}.{RAW_TABLE};

    ALTER TABLE
        {PROCESSED_SCHEMA}.{PROCESSED_TABLE}
    ADD CONSTRAINT
        comuni_lazio_2026_pk
    PRIMARY KEY (codice_comune);

    CREATE INDEX
        comuni_lazio_2026_geom_idx
    ON {PROCESSED_SCHEMA}.{PROCESSED_TABLE}
    USING GIST (geom);
    """

    print(
        f"Creazione di "
        f"{PROCESSED_SCHEMA}.{PROCESSED_TABLE}..."
    )

    with engine.begin() as connection:
        connection.execute(text(processing_sql))

    print(
        "Importazione ISTAT e creazione della "
        "tabella processed completate."
    )


if __name__ == "__main__":
    main()