# import streamlit as st
# import pandas as pd
# import sqlite3
# import requests

# # Fonction pour générer un token JWT


# def authenticate(username, password):
#     url = "http://localhost:8000/token"
#     response = requests.post(
#         url,
#         data={
#             "username": username,
#             "password": password})
#     if response.status_code == 200:
#         return response.json()["access_token"]
#     else:
#         st.error("Nom d'utilisateur ou mot de passe incorrect")
#         return None

# # Page d'authentification


# def login():
#     st.title("Page de connexion")
#     username = st.text_input("Nom d'utilisateur")
#     password = st.text_input("Mot de passe", type="password")
#     if st.button("Se connecter"):
#         token = authenticate(username, password)
#         if token:
#             st.session_state["token"] = token
#             st.success("Connexion réussie")
#             st.experimental_rerun()

# # Page principale


# def main():
#     # Connexion à la base de données SQLite
#     conn = sqlite3.connect("./database_building/sqlite/silver.db")

#     # Lire les données de la table 'jobs' dans un DataFrame
#     df = pd.read_sql_query("SELECT * FROM jobs", conn)

#     # Sélectionner une ligne aléatoire sans la colonne 'salary_in_usd'
#     random_row = df.drop(columns=['salary_in_usd']).sample(n=1)

#     # Ajouter un titre à la page Streamlit
#     st.title("Affichage d'une ligne aléatoire de la base de données")

#     # Afficher chaque donnée indépendamment
#     st.write("Ligne aléatoire de la base de données :")
#     for column, value in random_row.iloc[0].items():
#         st.write(f"**{column}**: {value}")

#     # Ajouter un bouton 'Estimation'
#     if st.button('Estimation'):
#         # Préparer les données pour l'API
#         input_data = random_row.iloc[0].to_dict()

#         # Convertir les valeurs des colonnes au type approprié
#         input_data['remote_ratio'] = str(
#             input_data['remote_ratio'])  # Convertir remote_ratio en float

#         # Imprimer les données d'entrée pour le débogage
#         # st.write("Données envoyées à l'API :", input_data)

#         # Appeler l'API pour obtenir la prédiction
#         token = st.session_state.get("token")
#         if token:
#             headers = {"Authorization": f"Bearer {token}"}
#             response = requests.post(
#                 "http://localhost:8000/predict",
#                 json=input_data,
#                 headers=headers)

#             try:
#                 response.raise_for_status()
#                 result = response.json()
#                 # Formater la prédiction
#                 prediction_value = result['prediction']
#                 prediction_formatted = f"{round(prediction_value / 1000)} K usd"
#                 st.write(
#                     f"Le salaire annuel est estimé à {prediction_formatted}")
#             except requests.exceptions.HTTPError as http_err:
#                 st.error(f"Erreur HTTP : {http_err}")
#                 st.error(response.text)
#             except Exception as err:
#                 st.error(f"Autre erreur : {err}")
#         else:
#             st.error("Vous devez vous connecter pour faire une estimation")

#     # Fermer la connexion
#     conn.close()


# # Application principale
# if "token" not in st.session_state:
#     login()
# else:
#     main()

##################################################################################################################
    
import streamlit as st
import pandas as pd
import sqlite3
import requests

# Fonction pour générer un token JWT
def authenticate(username, password):
    url = "http://localhost:8000/token"
    response = requests.post(url, data={"username": username, "password": password})
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
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
            st.experimental_rerun()

# Page principale
def main():
    st.title("Estimation de salaire")
    
    # Connexion à la base de données SQLite
    conn = sqlite3.connect("./database_building/sqlite/silver.db")

    # Lire les données de la table 'jobs' dans un DataFrame
    df = pd.read_sql_query("SELECT * FROM jobs", conn)

    # Sélectionner une ligne aléatoire sans la colonne 'salary_in_usd'
    random_row = df.drop(columns=['salary_in_usd']).sample(n=1)

    # Afficher chaque donnée indépendamment
    st.write("Ligne aléatoire de la base de données :")
    for column, value in random_row.iloc[0].items():
        st.write(f"**{column}**: {value}")

    # Ajouter un bouton 'Estimation'
    if st.button('Estimation'):
        # Préparer les données pour l'API
        input_data = random_row.iloc[0].to_dict()

        # Convertir les valeurs des colonnes au type approprié
        input_data['remote_ratio'] = str(input_data['remote_ratio'])  # Convertir remote_ratio en float

        # Imprimer les données d'entrée pour le débogage
        # st.write("Données envoyées à l'API :", input_data)

        # Appeler l'API pour obtenir la prédiction
        token = st.session_state.get("token")
        if token:
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.post("http://localhost:8000/predict", json=input_data, headers=headers)

            try:
                response.raise_for_status()
                result = response.json()
                # Formater la prédiction
                prediction_value = result['prediction']
                prediction_formatted = f"{round(prediction_value / 1000)} K"
                st.write(f"Le salaire annuel est estimé à {prediction_formatted}")
            except requests.exceptions.HTTPError as http_err:
                st.error(f"Erreur HTTP : {http_err}")
                st.error(response.text)
            except Exception as err:
                st.error(f"Autre erreur : {err}")
        else:
            st.error("Vous devez vous connecter pour faire une estimation")

    # Fermer la connexion
    conn.close()

# Application principale
if "authenticated" not in st.session_state or not st.session_state["authenticated"]:
    login()
else:
    main()
