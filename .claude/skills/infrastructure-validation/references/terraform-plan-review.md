# Reading a Terraform plan for destructive changes

`terraform validate` and a linter only check syntax/style — they never tell
you a plan will destroy a production database. Always read the plan itself
before approving an apply.

## Fast path: the bundled script

```shell
terraform plan -out=tfplan.binary
terraform show -json tfplan.binary > plan.json
uv run python scripts/check_terraform_plan.py plan.json
```

Exit `0` means no `delete` action appears in the plan. Exit `1` lists every
resource address whose action includes deletion (a pure destroy, or a
replace, which Terraform represents as delete-then-create).

## Manual fallback (no script available)

```shell
terraform show -json tfplan.binary | jq -r \
  '.resource_changes[] | select(.change.actions | index("delete")) | .address'
```

Human-readable plan output also marks replacement with `-/+` and pure destroy
with `-` in the left-hand column — do not rely on scrolling past a long plan
by eye alone on anything touching stateful resources (databases, storage,
identity).

## What counts as acceptable vs. a stop-and-ask signal

| Situation | Verdict |
| --- | --- |
| Replacing a stateless compute resource (container revision, function app slot) | Usually fine — confirm zero-downtime rollout is configured |
| Any `delete` on a database, storage account, key vault, or their child resources (keys, secrets, containers) | Stop and ask — verify a backup/export exists and the deletion is intended |
| Replace forced by an immutable property change (e.g. a Bicep/ARM resource `name`) | Confirm whether the immutable field change was intentional; consider `lifecycle { create_before_destroy = true }` if downtime is unacceptable |
| Provider-only or output-only changes (`no-op`, `read`) | Not destructive — no action needed |

## Related

- `infrastructure-validation` `SKILL.md` Terraform section — pinning,
  backends, `sensitive` outputs, and the required validation sequence.
- `scripts/check_terraform_plan.py` — automates the "fast path" above.
