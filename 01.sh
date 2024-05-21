#!/bin/bash

# ce fichier télécharge les données, les nettoie et les enregistre en silver.csv

# Fonction pour afficher un message INFO
print_info() {
    echo -e "\e[32mINFO:\e[0m \e[97m$1\e[0m"
}


# Vérifier si kaggle.json se trouve déjà dans ~/.kaggle/
if [ -f ~/.kaggle/kaggle.json ]; then
    print_info "Le fichier kaggle.json est présent dans ~/.kaggle/."
    chmod 600 ~/.kaggle/kaggle.json
    print_info "Les permissions de kaggle.json ont été ajustées."
else
    # Vérifier si kaggle.json se trouve dans Téléchargements
    if [ -f ~/Téléchargements/kaggle.json ]; then
        print_info "Déplacement de kaggle.json vers ~/.kaggle/..."
        mv ~/Téléchargements/kaggle.json ~/.kaggle/
        chmod 600 ~/.kaggle/kaggle.json
        print_info "Le fichier kaggle.json a été déplacé avec succès vers ~/.kaggle/"
    else
        print_info "Le fichier kaggle.json ne se trouve pas dans le dossier Téléchargements."
    fi
fi

# Création de l'environnement virtuel
print_info "Création de l'environnement virtuel..."
python3 -m venv venv

# Activation de l'environnement virtuel
print_info "Activation de l'environnement virtuel..."
source venv/bin/activate

# Installation des dépendances à partir du fichier requirements.txt
print_info "Installation des dépendances à partir du fichier requirements.txt..."
pip install -r requirements.txt

# Vérifier si bronze.csv existe déjà
if [ ! -f "data/bronze.csv" ]; then
    # Vérifier si le fichier ZIP n'existe pas avant de le télécharger
    if [ ! -f "data/latest-data-science-job-salaries-2024.zip" ]; then
        print_info "Téléchargement du fichier ZIP..."
        kaggle datasets download -d saurabhbadole/latest-data-science-job-salaries-2024 -p data
        print_info "Le fichier ZIP a été téléchargé avec succès."
    fi

    # Vérifier si le fichier ZIP a été décompressé
    if [ ! -d "data/DataScience_salaries_2024" ]; then
        print_info "Décompression du fichier ZIP..."
        unzip data/latest-data-science-job-salaries-2024.zip -d data
        print_info "Le fichier ZIP a été décompressé avec succès."
    fi

    # Suppression du fichier ZIP si nécessaire
    if [ -f "data/latest-data-science-job-salaries-2024.zip" ]; then
        rm data/latest-data-science-job-salaries-2024.zip
    fi

    # Renommer NY-House-Dataset.csv en bronze.csv
    print_info "Renommage de DataScience_salaries_2024.csv en bronze.csv..."
    mv data/DataScience_salaries_2024.csv data/bronze.csv
    print_info "DataScience_salaries_2024.csv a été renommé en bronze.csv avec succès."
else
    print_info "Le fichier bronze.csv existe déjà. Aucune action nécessaire."
fi

# # Création de la base de données et de la structure de la table
# print_info "Création de la base de données et de la structure de la table..."
# sqlite3 dsjs.db < database_building/create_table.sql

# # Vérification si la création de la table a réussi
# if [ $? -eq 0 ]; then
#     print_info "La base de données et la structure de la table ont été créées avec succès."
# else
#     print_info "Erreur lors de la création de la base de données ou de la structure de la table."
#     exit 1
# fi

# # Importation des données depuis le fichier CSV dans la table
# print_info "Importation des données depuis le fichier CSV dans la table..."
# sqlite3 dsjs.db < database_building/import_table.sql 2>/dev/null

# # Vérification si l'importation des données a réussi
# if [ $? -eq 0 ]; then
#     print_info "Les données ont été importées avec succès dans la table."
# else
#     print_info "Erreur lors de l'importation des données dans la table."
#     exit 1
# fi

# # Démarrer l'API FastAPI
# print_info "Démarrage de l'API FastAPI..."
# python3 api/main.py --reload