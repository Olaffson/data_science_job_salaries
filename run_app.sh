#!/bin/bash

# Activer l'environnement virtuel (si utilisé)
# source venv/bin/activate

# Démarrer l'API FastAPI en arrière-plan
echo "Démarrage de l'API FastAPI..."
uvicorn api.api:app --reload &

# Démarrer l'application Streamlit
echo "Démarrage de l'application Streamlit..."
streamlit run app/app.py
