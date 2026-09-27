#!/bin/bash

# Importe data/silver.csv dans la table jobs du serveur PostgreSQL Azure
cd "$(dirname "$0")/.." || exit 1
source database_building/pg_env.sh

psql -v ON_ERROR_STOP=1 -c "\copy jobs (experience_level, employment_type, job_title, employee_residence, remote_ratio, company_location, company_size, salary_in_usd) FROM 'data/silver.csv' WITH (FORMAT csv, HEADER true)"
