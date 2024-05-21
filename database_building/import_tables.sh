#!/bin/bash

# Azure SQL Server credentials
server="projet-ok-prod-sqlserver.database.windows.net"
database="projet-ok-prod-database"
username="adminuser"
password="yourStrongPassword123!"

# Path to your CSV file
csvFile="/home/utilisateur/Documents/Projets/data_science_job_salaries/data/silver.csv"

# Import data
bcp salaries in $csvFile -S $server -d $database -U $username -P $password -q -c -t ","

