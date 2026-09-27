# provider "azurerm" {
#   features {}
# }

# # Création d'un groupe de ressource
# resource "azurerm_resource_group" "projet-rg" {
#   name     = "projet-ok-prod-rg"
#   location = "francecentral"
# }

# # Création d'un plan de service
# resource "azurerm_app_service_plan" "projet-pas" {
#   name                = "projet-ok-prod-pas"
#   location            = azurerm_resource_group.projet-rg.location
#   resource_group_name = azurerm_resource_group.projet-rg.name

#   sku {
#     tier = "Free"
#     size = "F1"
#   }
# }

# # # Création d'un registre de conteneur
# # resource "azurerm_container_registry" "projet_acr" {
# #   name                     = "projet-ok-prod-container"
# #   resource_group_name      = azurerm_resource_group.projet-rg.name
# #   location                 = azurerm_resource_group.projet-rg.location
# #   sku                      = "Basic"
# #   admin_enabled            = false
# #   public_network_access_enabled = true
# #   zone_redundancy_enabled  = false
# # }

# # Création d'un serveur SQL
# resource "azurerm_sql_server" "projet-sqlserveur" {
#   name                         = "projet-ok-prod-sqlserver"
#   resource_group_name          = azurerm_resource_group.projet-rg.name
#   location                     = azurerm_resource_group.projet-rg.location
#   version                      = "12.0"
#   administrator_login          = "adminlogin"
#   administrator_login_password = var.db_admin_password
# }

# # Création d'une base de données sur le serveur SQL
# resource "azurerm_sql_database" "projet-database" {
#   name                = "projet-ok-prod-database"
#   resource_group_name = azurerm_resource_group.projet-rg.name
#   location            = azurerm_resource_group.projet-rg.location
#   server_name         = azurerm_sql_server.projet-sqlserveur.name
#   edition             = "Basic"
#   collation           = "SQL_Latin1_General_CP1_CI_AS"
#   max_size_gb         = 1
# }

# resource "azurerm_sql_firewall_rule" "allow_client_ip" {
#   name                = "AllowClientIP"
#   resource_group_name = azurerm_resource_group.projet-rg.name
#   server_name         = azurerm_sql_server.projet-sqlserveur.name
#   start_ip_address    = "212.114.17.77"
#   end_ip_address      = "212.114.17.77"
# }

#################################################################################

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

# Création d'un serveur PostgreSQL
resource "azurerm_postgresql_server" "projet-postgres" {
  name                = "projet-ok-prod-postgres"
  location            = azurerm_resource_group.projet-rg.location
  resource_group_name = azurerm_resource_group.projet-rg.name

  sku_name = "GP_Gen5_2"  # Utilisation d'un niveau de performance de base avec 2 vCores
  version = "11"
  
  storage_mb = 5120  # 5 GB est le minimum
  backup_retention_days = 7
  auto_grow_enabled = false
  geo_redundant_backup_enabled = false

  administrator_login = "adminuser"
  administrator_login_password = var.db_admin_password

  ssl_enforcement_enabled = true
  public_network_access_enabled = true  # Accès limité à client_ip par la règle de pare-feu ci-dessous
}

# Création d'une base de données PostgreSQL
resource "azurerm_postgresql_database" "projet-postgres-db" {
  name                = "projet-ok-prod-database"
  resource_group_name = azurerm_resource_group.projet-rg.name
  server_name         = azurerm_postgresql_server.projet-postgres.name
  charset             = "UTF8"
  collation           = "English_United States.1252"
}

# Règle de pare-feu pour permettre l'accès depuis une adresse IP spécifique
resource "azurerm_postgresql_firewall_rule" "allow_client_ip" {
  name                = "AllowClientIP"
  resource_group_name = azurerm_resource_group.projet-rg.name
  server_name         = azurerm_postgresql_server.projet-postgres.name
  start_ip_address    = var.client_ip
  end_ip_address      = var.client_ip
}
