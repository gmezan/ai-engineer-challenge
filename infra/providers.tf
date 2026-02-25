terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=4.1.0"
    }
  }

  backend "azurerm" {
    resource_group_name  = ""
    storage_account_name = ""
    container_name       = "ai-engineer-challenge"
    key                  = "terraform.tfstate"
    use_oidc             = true
  }
}

# Configure the Microsoft Azure Provider
provider "azurerm" {
  resource_provider_registrations = "none" # This is only required when the User, Service Principal, or Identity running Terraform lacks the permissions to register Azure Resource Providers.
  features {}
}