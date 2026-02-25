data "azurerm_client_config" "current" {}

data "azurerm_resource_group" "rg" {
  name = "rg-ai-engineer-challenge"
}

resource "random_pet" "aoai" {
  length = 2
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