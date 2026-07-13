from pathlib import Path
import pandas as pd

# Cartella del progetto
PROJECT_DIR = Path(__file__).resolve().parents[1]

# File Excel ISPRA
INPUT_FILE = PROJECT_DIR / "data" / "raw" / "consumo_di_suolo_estratto_dati_2025_anni_2006_2024.xlsx"

# Cartella di output
OUTPUT_FILE = PROJECT_DIR / "data" / "processed" / "ispra_lazio.csv"

# ----------------------------
# Lettura dati
# ----------------------------

df = pd.read_excel(INPUT_FILE)

print(f"Righe lette: {len(df):,}")

# ----------------------------
# Solo Lazio
# ----------------------------

df_lazio = df[df["Nome_Regione"] == "Lazio"].copy()

print(f"Comuni Lazio: {len(df_lazio)}")

# ----------------------------
# Controllo
# ----------------------------

assert len(df_lazio) == 378, "Numero di comuni inatteso!"

# ----------------------------
# Salvataggio
# ----------------------------

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

df_lazio.to_csv(
    OUTPUT_FILE,
    index=False,
    encoding="utf-8-sig"
)

print()
print("CSV creato correttamente:")
print(OUTPUT_FILE)