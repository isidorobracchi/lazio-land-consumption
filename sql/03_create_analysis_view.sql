DROP VIEW IF EXISTS analysis.v_consumo_suolo_comuni;

CREATE VIEW analysis.v_consumo_suolo_comuni AS
WITH base AS (
    SELECT
        c.codice_comune,
        c.nome_comune,
        i.nome_provincia,
        c.superficie_km2,

        i.incremento_netto_2006_2012_ettari,
        i.incremento_netto_2012_2015_ettari,
        i.incremento_netto_2015_2016_ettari,
        i.incremento_netto_2016_2017_ettari,
        i.incremento_netto_2017_2018_ettari,
        i.incremento_netto_2018_2019_ettari,
        i.incremento_netto_2019_2020_ettari,
        i.incremento_netto_2020_2021_ettari,
        i.incremento_netto_2021_2022_ettari,
        i.incremento_netto_2022_2023_ettari,
        i.incremento_netto_2023_2024_ettari,

        i.suolo_consumato_2024_ettari,
        i.suolo_consumato_2024_percentuale,

        (
            COALESCE(i.incremento_netto_2006_2012_ettari, 0) +
            COALESCE(i.incremento_netto_2012_2015_ettari, 0) +
            COALESCE(i.incremento_netto_2015_2016_ettari, 0) +
            COALESCE(i.incremento_netto_2016_2017_ettari, 0) +
            COALESCE(i.incremento_netto_2017_2018_ettari, 0) +
            COALESCE(i.incremento_netto_2018_2019_ettari, 0) +
            COALESCE(i.incremento_netto_2019_2020_ettari, 0) +
            COALESCE(i.incremento_netto_2020_2021_ettari, 0) +
            COALESCE(i.incremento_netto_2021_2022_ettari, 0) +
            COALESCE(i.incremento_netto_2022_2023_ettari, 0) +
            COALESCE(i.incremento_netto_2023_2024_ettari, 0)
        ) AS incremento_netto_2006_2024_ettari,

        c.geom

    FROM processed.comuni_lazio_2026 AS c

    INNER JOIN raw.ispra_consumo_suolo AS i
        ON c.codice_comune = i.codice_comune
)

SELECT
    codice_comune,
    nome_comune,
    nome_provincia,
    superficie_km2,

    suolo_consumato_2024_ettari,
    suolo_consumato_2024_percentuale,

    incremento_netto_2006_2024_ettari,

    incremento_netto_2006_2024_ettari / 18.0
        AS incremento_medio_annuo_ettari,

    incremento_netto_2006_2024_ettari
        / NULLIF(superficie_km2, 0)
        AS incremento_ettari_per_km2,

    incremento_netto_2006_2024_ettari
        / NULLIF(superficie_km2 * 100.0, 0)
        * 100.0
        AS incremento_percentuale_superficie,

    suolo_consumato_2024_ettari
        / NULLIF(superficie_km2, 0)
        AS suolo_consumato_ettari_per_km2,

    incremento_netto_2006_2012_ettari,
    incremento_netto_2012_2015_ettari,
    incremento_netto_2015_2016_ettari,
    incremento_netto_2016_2017_ettari,
    incremento_netto_2017_2018_ettari,
    incremento_netto_2018_2019_ettari,
    incremento_netto_2019_2020_ettari,
    incremento_netto_2020_2021_ettari,
    incremento_netto_2021_2022_ettari,
    incremento_netto_2022_2023_ettari,
    incremento_netto_2023_2024_ettari,

    geom

FROM base;