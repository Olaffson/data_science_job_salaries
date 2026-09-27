terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.101"
    }
  }
}

provider "azurerm" {
  features {}
}

# Mot de passe administrateur : à fournir via TF_VAR_db_admin_password (jamais en clair dans le code)
variable "db_admin_password" {
  type      = string
  sensitive = true
}

# Adresse IP autorisée à se connecter à la base (ex : TF_VAR_client_ip=$(curl -s ifconfig.me))
variable "client_ip" {
  type = string
}

# Création d'un groupe de ressources
resource "azurerm_resource_group" "projet-rg" {
  name     = "projet-ok-prod-rg"
  location = "francecentral"
}

# Création d'un serveur PostgreSQL (Flexible Server : Single Server a été retiré par Azure en mars 2025)
resource "azurerm_postgresql_flexible_server" "projet-postgres" {
  name                = "projet-ok-prod-postgres"
  location            = azurerm_resource_group.projet-rg.location
  resource_group_name = azurerm_resource_group.projet-rg.name

  sku_name   = "B_Standard_B1ms" # Niveau Burstable, le moins cher
  version    = "16"
  storage_mb = 32768 # 32 Go est le minimum

  backup_retention_days        = 7
  geo_redundant_backup_enabled = false

  administrator_login    = "adminuser"
  administrator_password = var.db_admin_password

  # Sans intégration VNet, l'accès est public mais limité par la règle de pare-feu ci-dessous

  lifecycle {
    ignore_changes = [zone]
  }
}

# Création d'une base de données PostgreSQL
resource "azurerm_postgresql_flexible_server_database" "projet-postgres-db" {
  name      = "projet-ok-prod-database"
  server_id = azurerm_postgresql_flexible_server.projet-postgres.id
  charset   = "UTF8"
  collation = "en_US.utf8"
}

# Règle de pare-feu pour permettre l'accès depuis une adresse IP spécifique
resource "azurerm_postgresql_flexible_server_firewall_rule" "allow_client_ip" {
  name             = "AllowClientIP"
  server_id        = azurerm_postgresql_flexible_server.projet-postgres.id
  start_ip_address = var.client_ip
  end_ip_address   = var.client_ip
}

output "postgres_host" {
  value = azurerm_postgresql_flexible_server.projet-postgres.fqdn
}
