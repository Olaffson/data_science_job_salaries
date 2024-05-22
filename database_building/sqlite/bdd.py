import pandas as pd
import sqlite3

# Lire le fichier CSV
df = pd.read_csv("data/silver.csv")

# Créer une connexion à la base de données SQLite
conn = sqlite3.connect("database_building/sqlite/silver.db")

# Insérer les données dans une table appelée 'jobs'
df.to_sql("jobs", conn, if_exists="replace", index=False)

# # Fermer la connexion
# conn.close()
