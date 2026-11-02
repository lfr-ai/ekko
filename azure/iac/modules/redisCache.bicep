@description('Azure region.')
param location string

@description('Base name for resources.')
param baseName string

@description('Tags applied to all resources.')
param tags object

@description('Allow public network access to Redis. No private networking (VNet/private endpoint) is wired up yet — see azure/README.md next steps.')
param publicNetworkAccess bool = true

@description('Redis SKU tier.')
@allowed([
  'Basic'
  'Standard'
  'Premium'
])
param skuName string = 'Basic'

@description('Redis SKU family (C = Basic/Standard, P = Premium).')
@allowed([
  'C'
  'P'
])
param skuFamily string = 'C'

@description('Redis SKU capacity (0-6 for family C, 1-5 for family P).')
param skuCapacity int = 0

var redisName = '${baseName}-redis'
var publicNetworkAccessState = publicNetworkAccess ? 'Enabled' : 'Disabled'

resource redis 'Microsoft.Cache/redis@2024-11-01' = {
  name: redisName
  location: location
  tags: tags
  properties: {
    sku: {
      name: skuName
      family: skuFamily
      capacity: skuCapacity
    }
    enableNonSslPort: false
    minimumTlsVersion: '1.2'
    publicNetworkAccess: publicNetworkAccessState
  }
}

output redisId string = redis.id
output redisName string = redis.name
output redisHostName string = redis.properties.hostName
output redisSslPort int = redis.properties.sslPort
