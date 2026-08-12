@description('Azure region.')
param location string

@description('Base name for resources.')
param baseName string

@description('Log Analytics workspace customer ID.')
param logAnalyticsWorkspaceCustomerId string

@description('Log Analytics workspace shared key.')
@secure()
param logAnalyticsWorkspaceSharedKey string

@description('Tags applied to all resources.')
param tags object

resource containerEnvironment 'Microsoft.App/managedEnvironments@2024-03-01' = {
  name: '${baseName}-cae'
  location: location
  tags: tags
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalyticsWorkspaceCustomerId
        sharedKey: logAnalyticsWorkspaceSharedKey
      }
    }
  }
}

output environmentId string = containerEnvironment.id
output environmentName string = containerEnvironment.name
