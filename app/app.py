import streamlit as st
import pandas as pd
import sqlite3
import random

# Connexion à la base de données SQLite
conn = sqlite3.connect("../database_building/sqlite/silver.db")

# Lire les données de la table 'jobs' dans un DataFrame
df = pd.read_sql_query("SELECT * FROM jobs", conn)

# Sélectionner une ligne aléatoire sans la colonne 'salary_in_usd'
random_row = df.drop(columns=['salary_in_usd']).sample(n=1)

# Ajouter un titre à la page Streamlit
st.title("Estimation de salaire")

# # Afficher la ligne aléatoire dans Streamlit
# st.write("Ligne aléatoire de la base de données :")
# st.table(random_row)

# Afficher chaque donnée indépendamment
st.write("Ligne aléatoire de la base de données :")
for column, value in random_row.iloc[0].items():
    st.write(f"**{column}**: {value}")

# Ajouter un bouton 'Estimation'
if st.button('Estimation'):
    st.write("estimation du salaire en usd : 0")
    # Vous pouvez ajouter ici le code pour effectuer une estimation ou d'autres opérations

# Fermer la connexion
conn.close()
