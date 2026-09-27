#!/bin/bash

# Ce script supprime les ressources Azure du projet
# Variables requises : TF_VAR_db_admin_password et TF_VAR_client_ip

set -e
cd "$(dirname "$0")/terraform"

terraform destroy --auto-approve
