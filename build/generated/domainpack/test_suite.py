from .resolver import DomainContextResolver
from .validator import DomainSignatureVerifier
from .manifest import DomainPackageManifest

def test_domainpack_subsystem():
    # 1. Domain context isolation resolution
    resolver = DomainContextResolver()
    assert resolver.register_context("sys_domain", "kernel_space") is True
    assert resolver.resolve_boundary("sys_domain") == "kernel_space"
    
    # 2. Cryptographic assembly signature verification
    verifier = DomainSignatureVerifier(b"super_secret_master_key")
    payload = b"sovereign_runtime_bytecode_blob"
    sig = verifier.sign_package(payload)
    assert verifier.verify_package(payload, sig) is True
    
    # 3. Manifest indexing structure
    manifest = DomainPackageManifest("sys_domain", "v1.0.0")
    index = manifest.export_index()
    assert index["domain"] == "sys_domain"
    assert index["ver"] == "v1.0.0"
    
    print("✅ Domain Package Resolution & Context Isolation Integration Tests Passed.")

if __name__ == "__main__":
    test_domainpack_subsystem()