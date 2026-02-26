data "azurerm_client_config" "current" {}

data "azurerm_resource_group" "rg" {
  name = "rg-ai-engineer-challenge"
}

resource "random_pet" "aoai" {
  length = 2
}

resource "random_pet" "cosmos" {
  length = 2
}

resource "random_pet" "search" {
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
    capacity = 10
  }
}

resource "azurerm_cognitive_deployment" "embedding_model" {
  name                 = "text-embedding-ada-002"
  cognitive_account_id = azurerm_cognitive_account.aoai.id

  model {
    format  = "OpenAI"
    name    = "text-embedding-ada-002"
    version = "2"
  }

  sku {
    name     = "Standard"
    capacity = 1
  }
}

resource "azurerm_search_service" "aisearch" {
  name                = "aisearch-${random_pet.search.id}"
  resource_group_name = data.azurerm_resource_group.rg.name
  location            = data.azurerm_resource_group.rg.location
  sku                 = "free"

  local_authentication_enabled = true
  authentication_failure_mode  = "http403"
}

resource "azurerm_cosmosdb_account" "cosmos_account" {
  name                = "coac-${random_pet.cosmos.id}-${random_integer.ri.result}"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  offer_type          = "Standard"
  kind                = "GlobalDocumentDB"

  consistency_policy {
    consistency_level = "Session"
  }

  geo_location {
    location          = data.azurerm_resource_group.rg.location
    failover_priority = 0
  }

  free_tier_enabled = true
}

resource "azurerm_cosmosdb_sql_database" "sql_db" {
  name                = "challenge-db"
  resource_group_name = data.azurerm_resource_group.rg.name
  account_name        = azurerm_cosmosdb_account.cosmos_account.name
}

resource "azurerm_cosmosdb_sql_container" "customer_behaviors" {
  name                  = "customer_behaviors"
  resource_group_name   = azurerm_cosmosdb_account.cosmos_account.resource_group_name
  account_name          = azurerm_cosmosdb_account.cosmos_account.name
  database_name         = azurerm_cosmosdb_sql_database.sql_db.name
  partition_key_paths   = ["/customer_id"]
  partition_key_version = 1
  throughput            = 400
}

resource "azurerm_cosmosdb_sql_container" "transactions" {
  name                  = "transactions"
  resource_group_name   = azurerm_cosmosdb_account.cosmos_account.resource_group_name
  account_name          = azurerm_cosmosdb_account.cosmos_account.name
  database_name         = azurerm_cosmosdb_sql_database.sql_db.name
  partition_key_paths   = ["/customer_id"]
  partition_key_version = 1
  throughput            = 400
}

resource "azurerm_cognitive_deployment" "gpt-5-mini" {
  name                 = "gpt-5-mini"
  cognitive_account_id = azurerm_cognitive_account.aoai.id

  model {
    format  = "OpenAI"
    name    = "gpt-5-mini"
    version = "2025-08-07"
  }

  sku {
    name     = "GlobalStandard"
    capacity = 20
  }
}