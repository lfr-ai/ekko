# Delta: Azure Terraform deployment

## ADDED Requirements

### Requirement: Terraform provisions an equivalent Azure workload

The repository MUST provide a Terraform deployment option that provisions the
same Azure workload resources and environment-dependent behavior as the current
Bicep deployment.

#### Scenario: Development deployment settings retain their behavior

- GIVEN the development environment parameters
- WHEN a Terraform deployment plan is generated
- THEN it describes the development resource topology and settings
- AND the Bicep development deployment remains unchanged

#### Scenario: Production deployment settings retain their behavior

- GIVEN the production environment parameters
- WHEN a Terraform deployment plan is generated
- THEN it describes the production resource topology and settings
- AND the production image reference must be immutable
- AND the Bicep production deployment remains unchanged

### Requirement: Infrastructure validation does not deploy resources

Automated Terraform validation MUST check configuration and provider-specific
static rules without applying changes to Azure.

#### Scenario: Terraform validation runs in continuous integration

- GIVEN a change to Terraform infrastructure files
- WHEN the infrastructure CI validation runs
- THEN formatting, configuration validation, and lint checks are performed
- AND no Terraform apply operation is run
- AND a Terraform-only change does not trigger the Bicep deployment workflow

### Requirement: Terraform state is isolated by environment

Terraform state MUST be stored remotely and separately for each deployment
environment, and state credentials MUST NOT be committed.

#### Scenario: Environment state does not overlap

- GIVEN development and production Terraform configurations
- WHEN each configuration is initialized
- THEN it uses a distinct remote state key
- AND backend authentication uses the approved Entra/OIDC identity
- AND concurrent state writes are protected by backend locking

