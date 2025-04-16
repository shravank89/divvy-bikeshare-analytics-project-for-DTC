# main.tf
provider "azurerm" {
  features {}
  subscription_id = var.subscription_id
  client_id       = var.client_id
  client_secret   = var.client_secret
  tenant_id       = var.tenant_id
  resource_provider_registrations = "none"
}

resource "azurerm_resource_group" "rg" {
  name     = "butterincode_group"
  location = "eastus"
}

resource "azurerm_storage_account" "storage" {
  name                     = "bikesharesynapse"
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true
}

resource "azurerm_storage_data_lake_gen2_filesystem" "container" {
  name               = "bikeshare"
  storage_account_id = azurerm_storage_account.storage.id
}

resource "azurerm_synapse_workspace" "synapse" {
  name                                 = "bikeshare-analytics"
  resource_group_name                  = azurerm_resource_group.rg.name
  location                            = azurerm_resource_group.rg.location
  storage_data_lake_gen2_filesystem_id = azurerm_storage_data_lake_gen2_filesystem.container.id
  sql_administrator_login             = "sqladminuser"
  sql_administrator_login_password     = "H@Sh1CoR3!"

  identity {
    type = "SystemAssigned"
  }
}


resource "azurerm_synapse_spark_pool" "spark_pool" {
  name                 = "pyspark"
  synapse_workspace_id = azurerm_synapse_workspace.synapse.id
  node_size_family     = "MemoryOptimized"
  node_size            = "Small"
  node_count           = 3
  spark_version        = "3.3"
  
  auto_pause {
    delay_in_minutes = 15
  }
}

