class DomainContextResolver:
    def __init__(self):
        self._isolated_contexts = {}

    def register_context(self, domain_id, entry_point_module):
        self._isolated_contexts[domain_id] = entry_point_module
        print(f"[DOMAIN-PACK] Provisioned isolated domain execution context: {domain_id}")
        return True

    def resolve_boundary(self, domain_id):
        return self._isolated_contexts.get(domain_id, None)