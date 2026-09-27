import os
import sqlite3
from contextlib import closing
from pathlib import Path

import pandas as pd
import requests
import streamlit as st

# URL de l'API FastAPI (modifiable via la variable d'environnement API_URL)
API_URL = os.environ.get("API_URL", "http://localhost:8000")

# Base SQLite créée par database_building/sqlite/bdd.py
DB_PATH = Path(__file__).resolve().parents[1] / "database_building" / "sqlite" / "silver.db"


# Authentification auprès de l'API pour obtenir un jeton JWT
def authenticate(username, password):
    try:
        response = requests.post(f"{API_URL}/token", data={"username": username, "password": password}, timeout=10)
    except requests.exceptions.RequestException as err:
        st.error(f"API injoignable ({API_URL}) : {err}")
        return None
    if response.status_code == 200:
        return response.json()["access_token"]
    st.error("Nom d'utilisateur ou mot de passe incorrect")
    return None


# Page d'authentification
def login():
    st.title("Estimation de salaire")
    username = st.text_input("Nom d'utilisateur")
    password = st.text_input("Mot de passe", type="password")
    if st.button("Se connecter"):
        token = authenticate(username, password)
        if token:
            st.session_state["token"] = token
            st.session_state["authenticated"] = True
            st.rerun()


# Page principale
def main():
    st.title("Estimation de salaire")

    if not DB_PATH.exists():
        st.error(f"Base de données introuvable : {DB_PATH}. Lancer d'abord ./01.sh")
        return

    # Lire les données de la table 'jobs' dans un DataFrame
    with closing(sqlite3.connect(DB_PATH)) as conn:
        df = pd.read_sql_query("SELECT * FROM jobs", conn)

    # Conserver la même ligne aléatoire entre deux interactions (sinon elle change au clic sur 'Estimation')
    if st.button("Nouvelle ligne") or "row" not in st.session_state:
        st.session_state["row"] = df.sample(n=1).iloc[0]
    row = st.session_state["row"]

    # Afficher chaque donnée (sans la colonne 'salary_in_usd', qui est la valeur à estimer)
    st.write("Ligne aléatoire de la base de données :")
    input_data = row.drop(labels=["salary_in_usd"]).to_dict()
    for column, value in input_data.items():
        st.write(f"**{column}**: {value}")

    if st.button("Estimation"):
        # L'API attend remote_ratio sous forme de chaîne de caractères
        input_data["remote_ratio"] = str(input_data["remote_ratio"])

        headers = {"Authorization": f"Bearer {st.session_state['token']}"}
        try:
            response = requests.post(f"{API_URL}/predict", json=input_data, headers=headers, timeout=10)
            if response.status_code == 401:
                # Jeton expiré : revenir à la page de connexion
                st.session_state["authenticated"] = False
                st.warning("Session expirée, veuillez vous reconnecter")
                return
            response.raise_for_status()
            prediction_value = response.json()["prediction"]
            st.write(f"Le salaire annuel est estimé à {round(prediction_value / 1000)} K USD")
            st.write(f"Salaire réel : {round(row['salary_in_usd'] / 1000)} K USD")
        except requests.exceptions.HTTPError as http_err:
            st.error(f"Erreur HTTP : {http_err}")
            st.error(response.text)
        except requests.exceptions.RequestException as err:
            st.error(f"API injoignable ({API_URL}) : {err}")


# Application principale
if not st.session_state.get("authenticated"):
    login()
else:
    main()
