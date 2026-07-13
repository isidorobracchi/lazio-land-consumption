DROP TABLE IF EXISTS processed.comuni_lazio_2026;

CREATE TABLE processed.comuni_lazio_2026 AS
SELECT
    pro_com_t::text AS codice_comune,
    comune AS nome_comune,
    cod_reg::integer AS codice_regione,
    cod_uts::integer AS codice_provincia,
    ST_Multi(ST_MakeValid(geom))::geometry(MultiPolygon, 32632) AS geom,
    ST_Area(geom) / 1000000.0 AS superficie_km2
FROM raw.comuni_istat_2026;

ALTER TABLE processed.comuni_lazio_2026
ADD CONSTRAINT comuni_lazio_2026_pk
PRIMARY KEY (codice_comune);

CREATE INDEX comuni_lazio_2026_geom_idx
ON processed.comuni_lazio_2026
USING GIST (geom);