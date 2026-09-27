import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]

# Lire le fichier CSV nettoyé (produit par analyse/analyse.ipynb)
df = pd.read_csv(ROOT / "data" / "silver.csv")

# Insérer les données dans la table 'jobs' de la base SQLite utilisée par l'application
with closing(sqlite3.connect(ROOT / "database_building" / "sqlite" / "silver.db")) as conn:
    df.to_sql("jobs", conn, if_exists="replace", index=False)

print(f"{len(df)} lignes importées dans database_building/sqlite/silver.db")
