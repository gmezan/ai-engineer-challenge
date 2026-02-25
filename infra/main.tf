data "azurerm_client_config" "current" {}

data "azurerm_resource_group" "rg" {
  name = "rg-ai-engineer-challenge"
}

resource "random_pet" "aoai" {
  length = 2

}

resource "azurerm_cognitive_account" "aoai" {
  name                = "aoai${random_pet.aoai.id}"
  location            = data.azurerm_resource_group.rg.location
  resource_group_name = data.azurerm_resource_group.rg.name
  kind                = "OpenAI"
  sku_name            = "S0"
}