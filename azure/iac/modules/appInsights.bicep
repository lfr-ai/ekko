param namePrefix string
param location string
param workspaceResourceId string
param kind string = 'web'
param applicationType string = 'web'
// retentionInDays removed (unused) — keep this module minimal and explicit
param tags object
param enabled bool = true

var appInsightsName = '${namePrefix}-ai'

resource appInsights 'Microsoft.Insights/components@2020-02-02' = if (enabled) {
  name: appInsightsName
  location: location
  tags: tags
  kind: kind
  properties: {
    Application_Type: applicationType
    WorkspaceResourceId: workspaceResourceId
  }
}

// Use null-coalescing operator to avoid null access when the resource is not
// fully provisioned yet during the ARM evaluation phase.
output appInsightsInstrumentationKey string = appInsights.properties.InstrumentationKey ?? ''
