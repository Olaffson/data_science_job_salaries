#!/bin/bash

# Lance l'API FastAPI et l'application Streamlit
# Variables requises : SECRET_KEY et ADMIN_PASSWORD (ou un fichier .env à la racine)

cd "$(dirname "$0")"

# Activer l'environnement virtuel s'il existe
if [ -d venv ]; then
    source venv/bin/activate
fi

# Démarrer l'API FastAPI en arrière-plan et l'arrêter à la sortie du script
echo "Démarrage de l'API FastAPI..."
uvicorn api.api:app --reload &
API_PID=$!
trap 'kill $API_PID' EXIT

# Démarrer l'application Streamlit
echo "Démarrage de l'application Streamlit..."
streamlit run app/app.py
