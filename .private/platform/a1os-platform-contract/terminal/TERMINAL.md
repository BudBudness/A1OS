# Terminal Control Contract

The terminal is a managed A1OS resource.

Managed domains:

- system
- processes
- services
- storage
- files
- network
- deployments
- diagnostics

Terminal operations must be deterministic workflows.

No arbitrary AI-generated command is authoritative.

Every mutating operation must have:

- declared operation
- policy check
- consequence classification
- approval when required
- execution
- verification
- audit evidence
