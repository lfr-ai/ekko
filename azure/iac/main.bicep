targetScope = 'resourceGroup'

@description('Primary Azure region for all resources.')
param location string = resourceGroup().location

@description('Deployment environment short name.')
@allowed([
  'dev'
  'test'
  'prod'
])
param environment string = 'dev'

@description('Prefix used when naming resources.')
@minLength(2)
@maxLength(12)
param resourcePrefix string = 'ekko'

@description('Container image tag to deploy.')
param imageTag string = 'latest'

@description('Container image name inside ACR repository.')
param imageName string = 'ekko'

var baseName = '${resourcePrefix}-${environment}'
var minReplicas = environment == 'prod' ? 1 : 0
var maxReplicas = environment == 'prod' ? 5 : 3
var acrSku = environment == 'prod' ? 'Standard' : 'Basic'
var tags = {
  workload: 'ekko'
  environment: environment
  managedBy: 'bicep'
}

module observability 'modules/logAnalytics.bicep' = {
  name: 'deploy-observability'
  params: {
    location: location
    baseName: baseName
    retentionInDays: environment == 'prod' ? 90 : 30
    publicNetworkAccess: environment != 'prod'
    tags: tags
  }
}

module registry 'modules/containerRegistry.bicep' = {
  name: 'deploy-acr'
  params: {
    location: location
    baseName: baseName
    tags: tags
    publicNetworkAccess: environment != 'prod'
    acrSku: acrSku
  }
}

module containerEnvironment 'modules/containerEnvironment.bicep' = {
  name: 'deploy-container-environment'
  params: {
    location: location
    baseName: baseName
    logAnalyticsWorkspaceCustomerId: observability.outputs.workspaceCustomerId
    logAnalyticsWorkspaceSharedKey: observability.outputs.workspaceSharedKey
    tags: tags
  }
}

module containerApp 'modules/containerApp.bicep' = {
  name: 'deploy-container-app'
  params: {
    location: location
    baseName: baseName
    environment: environment
    environmentId: containerEnvironment.outputs.environmentId
    acrId: registry.outputs.acrId
    acrName: registry.outputs.acrName
    acrLoginServer: registry.outputs.acrLoginServer
    imageName: imageName
    imageTag: imageTag
    minReplicas: minReplicas
    maxReplicas: maxReplicas
    appInsightsConnectionString: observability.outputs.connectionString
  }
}

output logAnalyticsWorkspaceId string = observability.outputs.workspaceId
output applicationInsightsConnectionString string = observability.outputs.connectionString
output containerAppsEnvironmentId string = containerEnvironment.outputs.environmentId
output containerAppName string = containerApp.outputs.containerAppName
output containerAppFqdn string = containerApp.outputs.containerAppFqdn
output acrLoginServer string = registry.outputs.acrLoginServer
