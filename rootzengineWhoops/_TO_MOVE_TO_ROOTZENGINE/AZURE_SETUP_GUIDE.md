# 🔵 Azure Setup Guide for RootzEngine

## Overview
This guide will walk you through setting up Azure services for RootzEngine's cloud capabilities including storage, processing, and monitoring.

## 📋 Prerequisites
- Azure account with active subscription
- Azure CLI installed: `az --version`
- Basic understanding of Azure Resource Groups

---

## 🎯 Phase 1: Core Azure Services Setup

### Step 1: Login and Set Subscription

```bash
# Login to Azure
az login

# List subscriptions
az account list --output table

# Set your subscription (replace with your subscription ID)
az account set --subscription "your-subscription-id"
```

### Step 2: Create Resource Group

```bash
# Create resource group (choose your preferred location)
az group create \
  --name "rootzengine-rg" \
  --location "eastus"
```

### Step 3: Create Storage Account

```bash
# Create storage account for audio files and results
az storage account create \
  --name "rootzenginestorage" \
  --resource-group "rootzengine-rg" \
  --location "eastus" \
  --sku "Standard_LRS" \
  --kind "StorageV2" \
  --access-tier "Hot"

# Get storage account key
az storage account keys list \
  --resource-group "rootzengine-rg" \
  --account-name "rootzenginestorage" \
  --output table
```

**📝 Save the following information:**
- Storage Account Name: `rootzenginestorage`
- Storage Account Key: (from command output)

### Step 4: Create Storage Containers

```bash
# Set storage account key as environment variable
export AZURE_STORAGE_KEY="your-storage-key-here"
export AZURE_STORAGE_ACCOUNT="rootzenginestorage"

# Create containers for different data types
az storage container create --name "audio-input" --public-access off
az storage container create --name "audio-processed" --public-access off
az storage container create --name "midi-output" --public-access off
az storage container create --name "analysis-results" --public-access off
az storage container create --name "models" --public-access off
```

### Step 5: Create Key Vault

```bash
# Create Key Vault for secure credential storage
az keyvault create \
  --name "rootzengine-vault" \
  --resource-group "rootzengine-rg" \
  --location "eastus"

# Store storage connection string
az keyvault secret set \
  --vault-name "rootzengine-vault" \
  --name "storage-connection-string" \
  --value "DefaultEndpointsProtocol=https;AccountName=rootzenginestorage;AccountKey=YOUR-KEY-HERE;EndpointSuffix=core.windows.net"
```

---

## 🚀 Phase 2: Container Processing Setup

### Step 6: Create Container Registry (Optional)

```bash
# Create Azure Container Registry for custom images
az acr create \
  --resource-group "rootzengine-rg" \
  --name "rootzengineregistry" \
  --sku "Basic" \
  --admin-enabled true

# Get registry credentials
az acr credential show \
  --name "rootzengineregistry" \
  --resource-group "rootzengine-rg"
```

### Step 7: Create Container Instance for Processing

```bash
# Create container instance for batch processing
az container create \
  --resource-group "rootzengine-rg" \
  --name "rootzengine-processor" \
  --image "rootzengine:latest" \
  --cpu 2 \
  --memory 4 \
  --restart-policy Never \
  --environment-variables \
    ROOTZ_AZURE_STORAGE_ACCOUNT="rootzenginestorage" \
    ROOTZ_AZURE_CONTAINER_NAME="audio-input" \
  --secure-environment-variables \
    ROOTZ_AZURE_CONNECTION_STRING="@Microsoft.KeyVault(SecretUri=https://rootzengine-vault.vault.azure.net/secrets/storage-connection-string/)"
```

---

## 📊 Phase 3: Monitoring & Analytics

### Step 8: Create Application Insights

```bash
# Create Application Insights for monitoring
az monitor app-insights component create \
  --app "rootzengine-insights" \
  --location "eastus" \
  --resource-group "rootzengine-rg" \
  --kind "web"

# Get instrumentation key
az monitor app-insights component show \
  --app "rootzengine-insights" \
  --resource-group "rootzengine-rg" \
  --query instrumentationKey \
  --output tsv
```

### Step 9: Store Application Insights Key

```bash
# Store instrumentation key in Key Vault
az keyvault secret set \
  --vault-name "rootzengine-vault" \
  --name "appinsights-key" \
  --value "your-instrumentation-key-here"
```

---

## 🗄️ Phase 4: Database Setup (Optional)

### Step 10: Create PostgreSQL Database

```bash
# Create PostgreSQL server for metadata storage
az postgres server create \
  --resource-group "rootzengine-rg" \
  --name "rootzengine-db" \
  --location "eastus" \
  --admin-user "rootzadmin" \
  --admin-password "YourSecurePassword123!" \
  --sku-name "B_Gen5_1" \
  --version "13"

# Create database
az postgres db create \
  --resource-group "rootzengine-rg" \
  --server-name "rootzengine-db" \
  --name "rootzengine"

# Configure firewall (allow Azure services)
az postgres server firewall-rule create \
  --resource-group "rootzengine-rg" \
  --server "rootzengine-db" \
  --name "AllowAzureServices" \
  --start-ip-address "0.0.0.0" \
  --end-ip-address "0.0.0.0"
```

---

## 🔐 Phase 5: Security & Access Control

### Step 11: Create Service Principal

```bash
# Create service principal for application authentication
az ad sp create-for-rbac \
  --name "rootzengine-sp" \
  --role "Contributor" \
  --scopes "/subscriptions/YOUR-SUBSCRIPTION-ID/resourceGroups/rootzengine-rg"

# Note: Save the output - you'll need these values:
# - appId (client_id)
# - password (client_secret)  
# - tenant
```

### Step 12: Grant Key Vault Access

```bash
# Grant service principal access to Key Vault
az keyvault set-policy \
  --name "rootzengine-vault" \
  --spn "your-app-id-here" \
  --secret-permissions get list
```

---

## 🔧 Phase 6: Environment Configuration

### Step 13: Create Configuration File

Create `configs/azure.yaml`:

```yaml
azure:
  # Storage settings
  storage_account: "rootzenginestorage"
  container_name: "audio-input"
  connection_string: "@Microsoft.KeyVault(SecretUri=https://rootzengine-vault.vault.azure.net/secrets/storage-connection-string/)"
  
  # Processing settings
  container_registry: "rootzengineregistry.azurecr.io"
  resource_group: "rootzengine-rg"
  
  # Monitoring
  application_insights_key: "@Microsoft.KeyVault(SecretUri=https://rootzengine-vault.vault.azure.net/secrets/appinsights-key/)"
  
  # Database (optional)
  database_host: "rootzengine-db.postgres.database.azure.com"
  database_name: "rootzengine"
  database_user: "rootzadmin"
  
  # Processing options
  gpu_enabled: false
  batch_size: 4
  max_concurrency: 10
```

### Step 14: Set Environment Variables

```bash
# Set these in your deployment environment
export AZURE_CLIENT_ID="your-app-id"
export AZURE_CLIENT_SECRET="your-app-password"
export AZURE_TENANT_ID="your-tenant-id"
export AZURE_SUBSCRIPTION_ID="your-subscription-id"

# For local development, create .env file:
cat > .env << EOF
AZURE_CLIENT_ID=your-app-id
AZURE_CLIENT_SECRET=your-app-password
AZURE_TENANT_ID=your-tenant-id
AZURE_SUBSCRIPTION_ID=your-subscription-id
ROOTZ_AZURE_STORAGE_ACCOUNT=rootzenginestorage
ROOTZ_AZURE_CONTAINER_NAME=audio-input
EOF
```

---

## 🧪 Phase 7: Testing Your Setup

### Step 15: Test Storage Connection

```bash
# Upload a test file
echo "Test audio file" > test.wav
az storage blob upload \
  --account-name "rootzenginestorage" \
  --container-name "audio-input" \
  --name "test.wav" \
  --file "test.wav"

# List blobs to verify
az storage blob list \
  --account-name "rootzenginestorage" \
  --container-name "audio-input" \
  --output table
```

### Step 16: Test Key Vault Access

```bash
# Retrieve secret to test access
az keyvault secret show \
  --vault-name "rootzengine-vault" \
  --name "storage-connection-string" \
  --query value \
  --output tsv
```

---

## 💰 Phase 8: Cost Optimization

### Step 17: Set Up Budget Alerts

```bash
# Create budget to monitor costs
az consumption budget create \
  --resource-group "rootzengine-rg" \
  --budget-name "rootzengine-budget" \
  --amount 100 \
  --time-grain Monthly \
  --time-period start-date="2024-01-01" \
  --notifications \
    enabled=true \
    operator=GreaterThan \
    threshold=80 \
    contact-emails="your-email@domain.com"
```

### Step 18: Configure Lifecycle Policies

```bash
# Create lifecycle management policy for storage
cat > lifecycle-policy.json << 'EOF'
{
  "rules": [
    {
      "enabled": true,
      "name": "ArchiveOldAudio",
      "type": "Lifecycle",
      "definition": {
        "filters": {
          "blobTypes": ["blockBlob"],
          "prefixMatch": ["audio-input/"]
        },
        "actions": {
          "baseBlob": {
            "tierToCool": {"daysAfterModificationGreaterThan": 30},
            "tierToArchive": {"daysAfterModificationGreaterThan": 90},
            "delete": {"daysAfterModificationGreaterThan": 365}
          }
        }
      }
    }
  ]
}
EOF

# Apply lifecycle policy
az storage account management-policy create \
  --account-name "rootzenginestorage" \
  --resource-group "rootzengine-rg" \
  --policy @lifecycle-policy.json
```

---

## 📋 Final Checklist

Mark each item as complete:

- [ ] ✅ Resource group created
- [ ] ✅ Storage account with containers created  
- [ ] ✅ Key Vault with secrets configured
- [ ] ✅ Application Insights for monitoring
- [ ] ✅ Service principal with proper permissions
- [ ] ✅ Environment variables configured
- [ ] ✅ Budget alerts set up
- [ ] ✅ Lifecycle policies configured
- [ ] ✅ Storage connection tested
- [ ] ✅ Key Vault access verified

## 🔍 Resource Summary

After completion, you'll have:

| Resource Type | Name | Purpose |
|---------------|------|---------|
| Resource Group | `rootzengine-rg` | Container for all resources |
| Storage Account | `rootzenginestorage` | Audio files and results |
| Key Vault | `rootzengine-vault` | Secure credential storage |
| App Insights | `rootzengine-insights` | Monitoring and analytics |
| Service Principal | `rootzengine-sp` | Application authentication |
| PostgreSQL | `rootzengine-db` | Metadata storage (optional) |

## 💡 Next Steps

1. **Test RootzEngine with Azure**: Use the configured services in your application
2. **Set up CI/CD**: Configure GitHub Actions for deployment
3. **Monitor Usage**: Check Application Insights dashboard
4. **Scale as Needed**: Adjust storage tiers and compute resources based on usage

## 🚨 Security Reminders

- **Never commit secrets** to version control
- **Use Key Vault** for all sensitive configuration
- **Enable MFA** on your Azure account
- **Review permissions** regularly
- **Monitor costs** to avoid surprises

---

**🎉 Your Azure environment is now ready for RootzEngine!**

For support, check the [Azure documentation](https://docs.microsoft.com/azure/) or create an issue in the RootzEngine repository.