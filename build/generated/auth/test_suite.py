from .manager import SystemIdentityManager
from .rbac import RoleBasedAccessControl
from .key_vault import CryptographicKeyVault

def test_auth_subsystem():
    # 1. Verify capability provisioning and checks
    manager = SystemIdentityManager()
    assert manager.provision_identity("node_zero", ["reboot", "sync"]) is True
    assert manager.has_capability("node_zero", "reboot") is True
    assert manager.has_capability("node_zero", "format") is False
    
    # 2. Role-based access control evaluation
    rbac = RoleBasedAccessControl()
    assert rbac.evaluate_access("admin", "execute") is True
    assert rbac.evaluate_access("viewer", "write") is False
    
    # 3. Cryptographic Key Vault storage and retrieval
    vault = CryptographicKeyVault()
    mock_key = b"-----BEGIN PUBLIC KEY-----
MOCK_KEY_BYTES
-----END PUBLIC KEY-----"
    vault.store_public_key("cert_01", mock_key)
    assert vault.retrieve_public_key("cert_01") == mock_key
    
    print("✅ Cryptographic Authorization & RBAC Subsystem Integration Tests Passed.")

if __name__ == "__main__":
    test_auth_subsystem()