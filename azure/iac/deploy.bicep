targetScope = 'subscription'

@description('Project name used for resource naming.')
@minLength(2)
@maxLength(12)
param projectName string = 'ekko'

@description('Deployment environment.')
@allowed([
  'dev'
  'prod'
])
param environment string = 'dev'

@description('Azure region for all resources.')
param location string = 'swedencentral'

@description('Optional resource group name override. Defaults to {project}-{env}-rg.')
param resourceGroupName string = ''

@description('Container image tag to deploy.')
param imageTag string = 'latest'

@description('Container image name inside ACR repository.')
param imageName string = 'ekko'

var rgName = empty(resourceGroupName) ? '${toLower(projectName)}-${environment}-rg' : resourceGroupName

resource rg 'Microsoft.Resources/resourceGroups@2024-03-01' = {
  name: rgName
  location: location
  tags: {
    project: projectName
    environment: environment
    managedBy: 'bicep'
  }
}

module main 'main.bicep' = {
  name: 'deploy-main-${environment}'
  scope: resourceGroup(rg.name)
  params: {
    location: location
    environment: environment
    resourcePrefix: projectName
    imageTag: imageTag
    imageName: imageName
  }
}

output resourceGroupName string = rg.name
output logAnalyticsWorkspaceId string = main.outputs.logAnalyticsWorkspaceId
output applicationInsightsConnectionString string = main.outputs.applicationInsightsConnectionString
output containerAppsEnvironmentId string = main.outputs.containerAppsEnvironmentId
output containerAppName string = main.outputs.containerAppName
output containerAppFqdn string = main.outputs.containerAppFqdn
output acrLoginServer string = main.outputs.acrLoginServer
