output "resource_group_name" {
  value = data.azurerm_resource_group.current.name
}

output "resource_group_location" {
  value = data.azurerm_resource_group.current.location
}