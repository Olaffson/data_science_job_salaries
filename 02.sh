#!/bin/bash

# Ce script crée les ressources Azure du projet (serveur et base PostgreSQL)
# Variables requises : TF_VAR_db_admin_password et TF_VAR_client_ip

set -e
cd "$(dirname "$0")/terraform"

terraform init
terraform plan
terraform apply --auto-approve
