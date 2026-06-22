targetScope = 'resourceGroup'

@description('Primary Azure region for shared observability resources.')
param location string = resourceGroup().location

@description('Deployment environment short name. Allowed: dev, test, prod.')
@allowed([
  'dev'
  'test'
  'prod'
])
param environment string = 'dev'

@description('Prefix used when naming resources. Should be globally unique when required by Azure resource types.')
@minLength(2)
@maxLength(12)
param resourcePrefix string = 'ekko'

@description('Log Analytics retention in days. Use higher values in production environments.')
@minValue(30)
@maxValue(730)
param logAnalyticsRetentionInDays int = environment == 'prod' ? 90 : 30

@description('Allow public network access for Log Analytics ingestion/query. Prefer Disabled for production deployments.')
param logAnalyticsPublicNetworkAccess bool = environment == 'prod' ? false : true

@description('Tags applied to all resources in this template.')
param tags object = {
  workload: 'ekko'
  environment: environment
  managedBy: 'bicep'
}

var baseName = '${resourcePrefix}-${environment}'
var logAnalyticsPublicNetworkAccessState = logAnalyticsPublicNetworkAccess ? 'Enabled' : 'Disabled'

resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2023-09-01' = {
  name: '${baseName}-law'
  location: location
  tags: tags
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: logAnalyticsRetentionInDays
    publicNetworkAccessForIngestion: logAnalyticsPublicNetworkAccessState
    publicNetworkAccessForQuery: logAnalyticsPublicNetworkAccessState
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

output logAnalyticsWorkspaceId string = logAnalytics.id
output applicationInsightsConnectionString string = appInsights.properties.ConnectionString
