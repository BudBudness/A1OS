# A1OS Engineering Capability Layer

This directory is the canonical engineering capability/control layer for A1OS.

## Contract

`CAPABILITY -> WORKFLOW -> EXECUTOR -> VERIFIER -> STATE -> EVIDENCE`

A capability describes what A1OS can operate. A workflow describes an operation. An executor performs it. A verifier proves the result. State and evidence make the operation auditable and recoverable.

## Initial capability set

- databases/postgresql
- caching/redis
- networking/nginx
- infrastructure/docker
- infrastructure/terraform
- infrastructure/ansible
- observability/core
- security/secrets
- messaging/kafka
- infrastructure/kubernetes

All workflows default to `dry_run` unless explicitly executed by a trusted integration. Destructive operations require policy approval.

## Runtime

The lightweight reference runtime in `runtime/` validates manifests, resolves capability/workflow dependencies, plans execution, records state, and runs deterministic verifiers. Provider-specific executors are adapters; A1OS remains the control plane.
