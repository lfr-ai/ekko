targetScope = 'resourceGroup'

@description('Azure region for all resources')
param location string = resourceGroup().location

@description('Deployment environment name')
@allowed([
  'dev'
  'test'
  'prod'
])
param environment string = 'dev'

@description('Global prefix for resource names')
@minLength(2)
@maxLength(12)
param resourcePrefix string = 'ekko'

@description('Container image tag to deploy in App Service')
param imageTag string = 'latest'

var baseName = toLower('${resourcePrefix}-${environment}')
var acrName = toLower(replace('${resourcePrefix}${environment}acr', '-', ''))
var appServicePlanName = '${baseName}-asp'
var webAppName = '${baseName}-web'

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  sku: {
    name: 'Basic'
  }
  properties: {
    adminUserEnabled: false
    publicNetworkAccess: 'Enabled'
  }
}

resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: appServicePlanName
  location: location
  sku: {
    name: 'B1'
    tier: 'Basic'
    size: 'B1'
    capacity: 1
  }
  kind: 'linux'
  properties: {
    reserved: true
  }
}

resource webApp 'Microsoft.Web/sites@2023-12-01' = {
  name: webAppName
  location: location
  kind: 'app,linux,container'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'DOCKER|${acr.properties.loginServer}/ekko:${imageTag}'
      alwaysOn: true
      minTlsVersion: '1.2'
      ftpsState: 'Disabled'
      acrUseManagedIdentityCreds: true
    }
  }
}

resource webAppAppSettings 'Microsoft.Web/sites/config@2023-12-01' = {
  name: 'appsettings'
  parent: webApp
  properties: {
    WEBSITES_ENABLE_APP_SERVICE_STORAGE: 'false'
    WEBSITES_PORT: '8000'
    DOCKER_REGISTRY_SERVER_URL: 'https://${acr.properties.loginServer}'
    EKKO_ENVIRONMENT: environment
  }
}

resource acrPullAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(acr.id, webApp.name, 'AcrPull')
  scope: acr
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalId: webApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

output appServiceName string = webApp.name
output appServiceDefaultHostname string = webApp.properties.defaultHostName
output acrLoginServer string = acr.properties.loginServer
output acrPullRoleAssignmentId string = acrPullAssignment.id
