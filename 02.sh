#!/bin/bash

# ce fichier crée les ressources azure nécessaires pour le projet

# Fonction pour afficher un message INFO
print_info() {
    echo -e "\e[32mINFO:\e[0m \e[97m$1\e[0m"
}

# Fonction pour l'initialisation Terraform
terraform_create() {
    cd terraform
    terraform init
    terraform plan
    terraform apply --auto-approve
}

# Appel des fonctions
terraform_create


# # Azure SQL Server credentials
# server="projet-ok-prod-postgres.database.windows.net"
# database="projet-ok-prod-database"
# username="adminuser"
# password="yourStrongPassword123!"

# # Path to your SQL script file
# sqlScript="/home/utilisateur/Documents/Projets/data_science_job_salaries/database_building/create_table.sql"

# # Connect to Azure SQL Server and execute the SQL script
# sqlcmd -S $server -d $database -U $username -P $password -i "$sqlScript"
# if [ $? -eq 0 ]; then
#     print_info "La table a été créée avec succès."
# else
#     print_info "Échec de la création de la table."
# fi

# # Path to your CSV file
# csvFile="./data/bronze.csv"

# # Import data
# bcp dbo.salaries in $csvFile -S $server -d $database -U $username -P $password -q -c -t ','
# if [ $? -eq 0 ]; then
#     print_info "Les données ont été importées avec succès."
# else
#     print_info "Échec de l'importation des données."
# fi