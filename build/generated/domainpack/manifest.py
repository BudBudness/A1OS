import time

class DomainPackageManifest:
    def __init__(self, domain_id, target_version):
        self.domain_id = domain_id
        self.version = target_version
        self.compiled_at = time.time()

    def export_index(self):
        return {
            "domain": self.domain_id,
            "ver": self.version,
            "sealed": self.compiled_at
        }