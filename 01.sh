#!/bin/bash

# Ce script prépare l'environnement local et les données :
# téléchargement du jeu de données (bronze.csv), nettoyage (silver.csv) et base SQLite (silver.db)

set -e
cd "$(dirname "$0")"

# Fonction pour afficher un message INFO
print_info() {
    echo -e "\e[32mINFO:\e[0m \e[97m$1\e[0m"
}

# Création de l'environnement virtuel
if [ ! -d venv ]; then
    print_info "Création de l'environnement virtuel..."
    python3 -m venv venv
fi

# Activation de l'environnement virtuel
print_info "Activation de l'environnement virtuel..."
source venv/bin/activate

# Installation des dépendances (application + notebooks)
print_info "Installation des dépendances..."
pip install -r requirements.txt -r model/requirements.txt

# Téléchargement du jeu de données s'il n'est pas déjà présent
if [ ! -f "data/bronze.csv" ]; then
    # Vérifier si kaggle.json se trouve dans ~/.kaggle/ ou dans Téléchargements
    mkdir -p ~/.kaggle
    if [ ! -f ~/.kaggle/kaggle.json ] && [ -f ~/Téléchargements/kaggle.json ]; then
        print_info "Déplacement de kaggle.json vers ~/.kaggle/..."
        mv ~/Téléchargements/kaggle.json ~/.kaggle/
    fi
    if [ ! -f ~/.kaggle/kaggle.json ]; then
        echo "ERREUR : kaggle.json introuvable (ni dans ~/.kaggle/ ni dans ~/Téléchargements/)." >&2
        exit 1
    fi
    chmod 600 ~/.kaggle/kaggle.json

    print_info "Téléchargement du jeu de données..."
    kaggle datasets download -d saurabhbadole/latest-data-science-job-salaries-2024 -p data
    unzip -o data/latest-data-science-job-salaries-2024.zip -d data
    rm data/latest-data-science-job-salaries-2024.zip

    # Renommer DataScience_salaries_2024.csv en bronze.csv
    mv data/DataScience_salaries_2024.csv data/bronze.csv
    print_info "Le jeu de données a été enregistré dans data/bronze.csv."
else
    print_info "Le fichier data/bronze.csv existe déjà. Aucun téléchargement nécessaire."
fi

# Nettoyage des données : bronze.csv -> silver.csv
print_info "Nettoyage des données (analyse/analyse.ipynb)..."
jupyter nbconvert --to notebook --execute --stdout analyse/analyse.ipynb > /dev/null

# Création de la base SQLite utilisée par l'application : silver.csv -> silver.db
print_info "Création de la base SQLite..."
python database_building/sqlite/bdd.py

print_info "Données prêtes. Lancer l'application avec ./run_app.sh"
