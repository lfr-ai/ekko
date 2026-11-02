# Terraform for Azure

This is a native HCL/AzureRM alternative to the Bicep topology under
[`../`](../). Bicep remains the deployment authority; this change adds
Terraform source and non-deploying validation only.

## Toolchain

- Terraform `1.9.x` (constraint: `>= 1.9.0, < 2.0.0`)
- AzureRM provider `4.x`, locked by `.terraform.lock.hcl`
- TFLint `0.52.0`, with the AzureRM ruleset pinned in `.tflint.hcl`

## Validate

From the repository root:

```shell
task terraform:check
```

The checks run `terraform fmt`, backend-free `terraform init` and `validate`,
then TFLint. They do not authenticate to Azure, create a plan, or apply changes.

## Environments

The example variable files are in [`environments/`](./environments/). Replace
the subscription and tenant placeholders before use. Production requires a
valid immutable `sha256:` image digest; the committed placeholder is
intentionally invalid.

## Remote state

Azure Blob state is operator-managed and isolated by environment. Copy
[`backend.dev.hcl.example`](./backend.dev.hcl.example) or
[`backend.prod.hcl.example`](./backend.prod.hcl.example) to the corresponding
untracked `.hcl` file, then replace its non-secret backend identifiers. Authenticate
with an Entra federated identity using `ARM_USE_OIDC`, `ARM_CLIENT_ID`,
`ARM_TENANT_ID`, `ARM_SUBSCRIPTION_ID`, and `ARM_OIDC_TOKEN`; do not put
credentials in backend files.

Initialize with the selected backend file:

```shell
cd azure/iac/terraform
terraform init -backend-config=backend.dev.hcl
```

State can contain resolved secrets, including Redis credentials. Restrict state
access with Azure RBAC and do not commit state, backend files, or plan output.
The remote state storage and any resource import/adoption plan must exist and be
reviewed before an operator considers a Terraform deployment.

## Parity

See the [Bicep-to-Terraform parity matrix](./PARITY_MATRIX.md) for resource and
environment comparisons. Terraform validation does not change or deploy Bicep
resources.
