
from marketplace.registry.core import ServiceRegistry
from marketplace.installer.resolver import DependencyResolver

class ServiceInstaller:
    def __init__(self, registry: ServiceRegistry, resolver: DependencyResolver):
        self.registry = registry
        self.resolver = resolver
        
    def install(self, service_id: str, manifest: Dict):
        dependencies = self.resolver.resolve(service_id)
        # Proceed with installation if dependencies are met
        self.registry.register(service_id, manifest)

