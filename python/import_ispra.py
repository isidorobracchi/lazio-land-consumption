from pathlib import Path
import re

import pandas as pd
from sqlalchemy import create_engine


PROJECT_DIR = Path(__file__).resolve().parents[1]

INPUT_FILE = (
    PROJECT_DIR
    / "data"
    / "raw"
    / "consumo_di_suolo_estratto_dati_2025_anni_2006_2024.xlsx"
)

OUTPUT_FILE = (
    PROJECT_DIR
    / "data"
    / "processed"
    / "ispra_lazio.csv"
)

SHEET_NAME = "Comuni_2006_2024"

DATABASE_URL = (
    "postgresql+psycopg2://"
    "gis_user:gis_password@localhost:5432/lazio_gis"
)


def clean_column_name(column_name: str) -> str:
    """Converte un'intestazione in un nome adatto a PostgreSQL."""
    name = column_name.strip().lower()

    replacements = {
        "%": "percentuale",
        "[": "",
        "]": "",
        "à": "a",
        "è": "e",
        "é": "e",
        "ì": "i",
        "ò": "o",
        "ù": "u",
    }

    for old, new in replacements.items():
        name = name.replace(old, new)

    name = re.sub(r"[^a-z0-9]+", "_", name)
    return name.strip("_")


# Lettura del file originale
df = pd.read_excel(
    INPUT_FILE,
    sheet_name=SHEET_NAME
)

print(f"Righe totali lette: {len(df)}")

# Selezione dei soli comuni del Lazio
df_lazio = df.loc[df["Nome_Regione"].eq("Lazio")].copy()

print(f"Comuni del Lazio trovati: {len(df_lazio)}")

if len(df_lazio) != 378:
    raise ValueError(
        f"Attesi 378 comuni, trovati {len(df_lazio)}."
    )

# Codice comunale uniforme a sei caratteri
df_lazio["PRO_COM"] = (
    df_lazio["PRO_COM"]
    .astype("Int64")
    .astype(str)
    .str.zfill(6)
)

# Pulizia delle intestazioni
df_lazio.columns = [
    clean_column_name(column)
    for column in df_lazio.columns
]

# Rinomina esplicita dei campi principali
df_lazio = df_lazio.rename(
    columns={
        "pro_com": "codice_comune",
        "nome_comune": "nome_comune",
        "nome_regione": "nome_regione",
        "nome_provincia": "nome_provincia",
    }
)

# Controlli sui codici
if df_lazio["codice_comune"].duplicated().any():
    duplicati = df_lazio.loc[
        df_lazio["codice_comune"].duplicated(False),
        ["codice_comune", "nome_comune"],
    ]
    raise ValueError(
        f"Codici comunali duplicati:\n{duplicati}"
    )

# Salvataggio del CSV elaborato
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

df_lazio.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig",
)

print(f"CSV creato: {OUTPUT_FILE}")

# Collegamento a PostgreSQL/PostGIS
engine = create_engine(DATABASE_URL)

# Caricamento nello schema raw
df_lazio.to_sql(
    name="ispra_consumo_suolo",
    con=engine,
    schema="raw",
    if_exists="replace",
    index=False,
    chunksize=500,
    method="multi",
)

print("Tabella raw.ispra_consumo_suolo caricata correttamente.")