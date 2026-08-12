@description('Azure region.')
param location string

@description('Base name for resources.')
param baseName string

@description('Tags applied to all resources.')
param tags object

@description('Allow public network access to ACR.')
param publicNetworkAccess bool = true

@description('Azure Container Registry SKU.')
@allowed([
  'Basic'
  'Standard'
  'Premium'
])
param acrSku string = 'Basic'

var acrName = toLower(replace('${baseName}acr', '-', ''))
var publicNetworkAccessState = publicNetworkAccess ? 'Enabled' : 'Disabled'

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' = {
  name: acrName
  location: location
  sku: {
    name: acrSku
  }
  tags: tags
  properties: {
    adminUserEnabled: false
    publicNetworkAccess: publicNetworkAccessState
  }
}

output acrId string = acr.id
output acrName string = acr.name
output acrLoginServer string = acr.properties.loginServer
