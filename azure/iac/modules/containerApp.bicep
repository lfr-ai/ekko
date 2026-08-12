@description('Azure region.')
param location string

@description('Base name for resources.')
param baseName string

@description('Deployment environment.')
param environment string

@description('Container Apps environment resource ID.')
param environmentId string

@description('Azure Container Registry resource ID.')
param acrId string

@description('Azure Container Registry name.')
param acrName string

@description('Azure Container Registry login server.')
param acrLoginServer string

@description('Container image name inside ACR repository.')
param imageName string = 'ekko'

@description('Container image tag to deploy.')
param imageTag string = 'latest'

@description('Container app ingress target port.')
param targetPort int = 8000

@description('Minimum replica count.')
param minReplicas int = 0

@description('Maximum replica count.')
param maxReplicas int = 3

@description('CPU allocation per replica.')
param cpuCores int = 1

@description('Memory allocation per replica (Gi).')
param memoryGi string = '2Gi'

@description('Application Insights connection string used by application-level telemetry.')
param appInsightsConnectionString string

var containerAppName = '${baseName}-ca'
var imageRef = '${acrLoginServer}/${imageName}:${imageTag}'

resource acr 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: acrName
}

resource containerApp 'Microsoft.App/containerApps@2024-03-01' = {
  name: containerAppName
  location: location
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    environmentId: environmentId
    configuration: {
      activeRevisionsMode: 'Single'
      ingress: {
        external: true
        targetPort: targetPort
        allowInsecure: false
        clientCertificateMode: 'Ignore'
        transport: 'auto'
      }
      registries: [
        {
          server: acrLoginServer
          identity: 'system'
        }
      ]
    }
    template: {
      containers: [
        {
          name: 'ekko'
          image: imageRef
          env: [
            {
              name: 'EKKO_ENVIRONMENT'
              value: environment
            }
            {
              name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
              value: appInsightsConnectionString
            }
          ]
          resources: {
            cpu: cpuCores
            memory: memoryGi
          }
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/health'
                port: targetPort
              }
              initialDelaySeconds: 15
              periodSeconds: 30
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/health'
                port: targetPort
              }
              initialDelaySeconds: 10
              periodSeconds: 15
            }
          ]
        }
      ]
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: [
          {
            name: 'http-concurrency'
            http: {
              metadata: {
                concurrentRequests: '50'
              }
            }
          }
        ]
      }
    }
  }
}

resource acrPullAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: acr
  name: guid(acrId, containerApp.name, 'AcrPull')
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalId: containerApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

output containerAppName string = containerApp.name
output containerAppFqdn string = containerApp.properties.configuration.ingress.fqdn
output acrPullRoleAssignmentId string = acrPullAssignment.id
