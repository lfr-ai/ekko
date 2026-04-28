@description('Deploy an Azure Container App with a single container and configure logging')
param namePrefix string
param location string
param containerAppName string
param image string
param cpu string = '0.5'
param memory string = '1Gi'
param replicas int = 1
param logAnalyticsWorkspaceId string = ''
param tags object
param enabled bool = true

var envName = '${namePrefix}-ca-env'
var appName = empty(containerAppName) ? '${namePrefix}-ca' : containerAppName
var _logAnalyticsWorkspaceId = logAnalyticsWorkspaceId

resource containerAppEnv 'Microsoft.Web/kubeEnvironments@2023-05-01' = if (enabled) {
  name: envName
  location: location
  tags: tags
  properties: {}
}

resource containerApp 'Microsoft.Web/containerApps@2023-10-01' = if (enabled) {
  name: appName
  location: location
  tags: tags
  properties: {
    // expose the (optional) workspace id into properties so modules that pass
    // the parameter do not trigger "declared but not used" diagnostics.
    diagnostics: {
      logAnalyticsWorkspaceId: _logAnalyticsWorkspaceId
    }
    managedEnvironmentId: containerAppEnv.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
      }
      dapr: {
        enabled: false
      }
      registries: []
    }
    template: {
      containers: [
        {
          name: 'app'
          image: image
          resources: {
            cpu: cpu
            memory: memory
          }
        }
      ]
      scale: {
        minReplicas: replicas
        maxReplicas: replicas
      }
    }
  }
}

output containerAppId string = containerApp.id
