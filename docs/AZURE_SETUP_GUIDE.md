# Azure Setup Guide

This guide provides instructions for setting up Azure resources for the RootzEngine project.

## Prerequisites
- Azure account
- Azure CLI installed

## Steps
1. Create a resource group:
   ```bash
   az group create --name RootzEngineGroup --location eastus
   ```

2. Create a storage account:
   ```bash
   az storage account create --name rootzenginestorage --resource-group RootzEngineGroup --location eastus --sku Standard_LRS
   ```

3. Configure environment variables:
   ```bash
   export AZURE_STORAGE_ACCOUNT=rootzenginestorage
   export AZURE_STORAGE_KEY=$(az storage account keys list --account-name rootzenginestorage --query [0].value -o tsv)
   ```

4. Verify setup:
   ```bash
   az storage account show --name rootzenginestorage
   ```

## Additional Resources
- [Azure CLI Documentation](https://learn.microsoft.com/en-us/cli/azure/)
- [Azure Storage Documentation](https://learn.microsoft.com/en-us/azure/storage/)
