output "resource_group_name" {
  value = azurerm_resource_group.rg.name
  description = "The name of the resource group"
}

output "storage_account_name" {
  value = azurerm_storage_account.storage.name
  description = "The name of the storage account"
}

output "storage_account_id" {
  value = azurerm_storage_account.storage.id
  description = "The ID of the storage account"
}

output "data_lake_filesystem_name" {
  value = azurerm_storage_data_lake_gen2_filesystem.container.name
  description = "The name of the Data Lake Gen2 filesystem"
}

output "synapse_workspace_name" {
  value = azurerm_synapse_workspace.synapse.name
  description = "The name of the Synapse workspace"
}

output "synapse_spark_pool_name" {
  value = azurerm_synapse_spark_pool.spark_pool.name
  description = "The name of the Synapse Spark pool"
}

output "synapse_workspace_endpoint" {
  value = azurerm_synapse_workspace.synapse.connectivity_endpoints
  description = "The connectivity endpoints for the Synapse workspace"
}