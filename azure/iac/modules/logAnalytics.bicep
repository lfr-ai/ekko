@description('Azure region.')
param location string

@description('Base name for resources.')
param baseName string

@description('Log Analytics retention in days.')
param retentionInDays int = 30

@description('Allow public network access.')
param publicNetworkAccess bool = true

@description('Tags applied to all resources.')
param tags object

var publicNetworkAccessState = publicNetworkAccess ? 'Enabled' : 'Disabled'

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${baseName}-law'
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: retentionInDays
    publicNetworkAccessForIngestion: publicNetworkAccessState
    publicNetworkAccessForQuery: publicNetworkAccessState
    workspaceCapping: {
      dailyQuotaGb: -1
    }
  }
}

resource appInsights 'Microsoft.Insights/components@2020-02-02' = {
  name: '${baseName}-appi'
  location: location
  kind: 'web'
  tags: tags
  properties: {
    Application_Type: 'web'
    WorkspaceResourceId: logAnalytics.id
    IngestionMode: 'LogAnalytics'
  }
}

output workspaceId string = logAnalytics.id
output workspaceCustomerId string = logAnalytics.properties.customerId
@secure()
output workspaceSharedKey string = logAnalytics.listKeys().primarySharedKey
output connectionString string = appInsights.properties.ConnectionString
