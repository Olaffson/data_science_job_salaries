#!/bin/bash

# ce fichier permet de supprimer les ressources azure

# Fonction pour la destruction Terraform
terraform_destroy() {
    cd terraform
    terraform destroy --auto-approve
}

# Appel des fonctions dans l'ordre souhaité
terraform_destroy
