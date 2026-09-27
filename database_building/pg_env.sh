#!/bin/bash

# Paramètres de connexion au serveur PostgreSQL Azure créé par Terraform (02.sh)
# DB_ADMIN_PASSWORD doit être défini (même valeur que TF_VAR_db_admin_password)
export PGHOST="${PGHOST:-projet-ok-prod-postgres.postgres.database.azure.com}"
export PGDATABASE="${PGDATABASE:-projet-ok-prod-database}"
export PGUSER="${PGUSER:-adminuser}"
export PGPASSWORD="${DB_ADMIN_PASSWORD:?La variable DB_ADMIN_PASSWORD doit être définie}"
export PGSSLMODE="${PGSSLMODE:-require}"
