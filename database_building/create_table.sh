#!/bin/bash

# Azure SQL Server credentials
server="projet-ok-prod-sqlserver.database.windows.net"
database="projet-ok-prod-database"
username="adminuser"
password="yourStrongPassword123!"

# Path to your SQL script file
sqlScript="/home/utilisateur/Documents/Projets/data_science_job_salaries/database_building/create_table.sql"

# Connect to Azure SQL Server and execute the SQL script
sqlcmd -S $server -d $database -U $username -P $password -i "$sqlScript"
