#!/bin/bash

# Crée la table jobs sur le serveur PostgreSQL Azure
cd "$(dirname "$0")/.." || exit 1
source database_building/pg_env.sh

psql -v ON_ERROR_STOP=1 -f database_building/create_table.sql
