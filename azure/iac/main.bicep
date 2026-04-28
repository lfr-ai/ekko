targetScope = 'resourceGroup'

@description('Main deployment for voice-bot: ACR, App Service (container), Storage, Log Analytics and Cognitive Services (OpenAI)')
param location string = resourceGroup().location
param environment string = 'dev'
param acrName string = 'voiceacr${uniqueString(resourceGroup().id)}'
param webAppName string = 'voice-backend-${environment}'
param containerImage string
// Note: Key Vault integration removed per repository policy (secrets handled via env configs)
param storageAccountName string = toLower('voice${uniqueString(resourceGroup().id)}')
param cognitiveName string = 'voice-openai-${uniqueString(resourceGroup().id)}'

// Log Analytics
module logAnalytics 'modules/logAnalytics.bicep' = {
  name: 'logAnalytics'
  params: {
    name: '${environment}-la-${uniqueString(resourceGroup().id)}'
    location: location
  }
}

// Container Registry
module acr 'modules/acr.bicep' = {
  name: 'acr'
  params: {
    name: acrName
    location: location
    sku: 'Basic'
  }
}

module plan 'modules/appServicePlan.bicep' = {
  name: 'appPlan'
  params: {
    name: '${environment}-plan'
    location: location
    skuName: 'P1v2'
    skuTier: 'PremiumV2'
  }
}
// Web App (as single-container Linux Web App)
module webApp 'modules/webApp.bicep' = {
  name: 'webApp'
  params: {
    name: webAppName
    location: location
    image: containerImage
    acrLoginServer: acr.outputs.loginServer
    planId: plan.outputs.planId
  }
}

// Key Vault module removed

// Storage
module storage 'modules/storage.bicep' = {
  name: 'storage'
  params: {
    name: storageAccountName
    location: location
  }
}

// Cognitive Services (Azure OpenAI)
module cognitive 'modules/cognitiveServices.bicep' = {
  name: 'cognitive'
  params: {
    name: cognitiveName
    location: location
    kind: 'CognitiveServices'
    skuName: 'S0'
  }
}

// outputs
output webAppUrl string = webApp.outputs.defaultHostName
output acrLoginServer string = acr.outputs.loginServer
// keyVaultId output removed because Key Vault is not used
output cognitiveResourceId string = cognitive.outputs.resourceId
