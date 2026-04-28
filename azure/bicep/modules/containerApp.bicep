@description('Prefix')
param prefix string
param location string
param environmentId string
param containerImage string
param registryLoginServer string
param registryUsername string
param registryPassword string
param appInsightsInstrumentationKey string
param postgresHost string
param postgresUsername string
@secure()
param postgresPassword string // pragma: allowlist secret
param keyVaultId string

resource containerApp 'Microsoft.App/containerApps@2023-10-01' = {
  name: '${prefix}-backend-app'
  location: location
  properties: {
    managedEnvironmentId: environmentId
    configuration: {
      secrets: [
        {
          name: 'POSTGRES_PASSWORD' // pragma: allowlist secret
          value: postgresPassword
        }
      ]
      registries: [
        {
          server: registryLoginServer
          username: registryUsername
          password: registryPassword
        }
      ]
      ingress: {
        external: true
        targetPort: 8000
        transport: 'Auto'
      }
    }
    template: {
      containers: [
        {
          name: 'backend'
          image: containerImage
          env: [
            { name: 'APPINSIGHTS_INSTRUMENTATIONKEY', value: appInsightsInstrumentationKey },
            { name: 'POSTGRES_HOST', value: postgresHost },
            { name: 'POSTGRES_USER', value: postgresUsername },
            { name: 'POSTGRES_PASSWORD', secretRef: 'POSTGRES_PASSWORD' } // pragma: allowlist secret
          ]
          resources: {
            cpu: 0.5
            memory: '1Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 3
      }
    }
  }
}

output containerAppName string = containerApp.name
output containerAppUrl string = containerApp.properties.configuration.ingress.fqdn
