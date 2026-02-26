data "azurerm_client_config" "current" {}

data "azurerm_resource_group" "rg" {
  name = "rg-ai-engineer-challenge"
}

resource "random_pet" "aoai" {
  length = 2
}

resource "random_integer" "ri" {
  min = 10000
  max = 99999
}

resource "azurerm_cognitive_account" "aoai" {
  name                = "aoai-${random_pet.aoai.id}"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  kind                = "OpenAI"
  sku_name            = "S0"
}

resource "azurerm_cognitive_deployment" "model_1" {
  name                 = "gpt-4.1-mini"
  cognitive_account_id = azurerm_cognitive_account.aoai.id

  model {
    format  = "OpenAI"
    name    = "gpt-4.1-mini"
    version = "2025-04-14"
  }

  sku {
    name     = "Standard"
    capacity = 4
  }
}

resource "azurerm_search_service" "aisearch" {
  name                = "aisearch-${random_pet.aoai.id}"
  resource_group_name = data.azurerm_resource_group.rg.name
  location            = data.azurerm_resource_group.rg.location
  sku                 = "standard"

  local_authentication_enabled = true
}

resource "azurerm_cosmosdb_account" "cosmos_account" {
  name                = "coac-${random_pet.aoai.id}-${random_integer.ri.result}"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  automatic_failover_enabled = true

  consistency_policy {
    consistency_level       = "BoundedStaleness"
    max_interval_in_seconds = 300
    max_staleness_prefix    = 100000
  }

  geo_location {
    location          = data.azurerm_resource_group.rg.location
    failover_priority = 0
  }
}

resource "azurerm_cosmosdb_sql_database" "sql_db" {
  name                = "codb-${random_pet.aoai.id}-${random_integer.ri.result}"
  resource_group_name = data.azurerm_resource_group.rg.name
  account_name        = azurerm_cosmosdb_account.cosmos_account.name
  # You can optionally define throughput here at the database level
}