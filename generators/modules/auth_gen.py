from generators.core.base_gen import BaseGenerator
from pathlib import Path

class AuthGenerator(BaseGenerator):
    def __init__(self, context):
        super().__init__(context)

    def generate(self):
        output_dir = Path(self.context.get("build_dir", "build/generated")) / "auth"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Identity and Capability Grant Manager
        manager_code = '''class SystemIdentityManager:
    def __init__(self):
        self.grants = {}

    def provision_identity(self, identity_id, capabilities):
        self.grants[identity_id] = set(capabilities)
        print(f"[AUTH-MGR] Provisioned capabilities for identity: {identity_id}")
        return True

    def has_capability(self, identity_id, required_capability):
        if identity_id not in self.grants:
            return False
        return required_capability in self.grants[identity_id]
'''

        # 2. Role-Based Access Control Engine
        rbac_code = '''class RoleBasedAccessControl:
    def __init__(self):
        self.role_permissions = {
            "admin": {"read", "write", "execute", "administer"},
            "operator": {"read", "write"},
            "viewer": {"read"}
        }

    def evaluate_access(self, assigned_role, required_permission):
        permissions = self.role_permissions.get(assigned_role, set())
        return required_permission in permissions
'''

        # 3. Cryptographic Key Vault Utility
        key_vault_code = '''class CryptographicKeyVault:
    def __init__(self):
        self._keys = {}

    def store_public_key(self, key_id, pem_bytes):
        self._keys[key_id] = pem_bytes
        print(f"[KEY-VAULT] Public key registered for identity anchor: {key_id}")

    def retrieve_public_key(self, key_id):
        return self._keys.get(key_id)
'''

        # 4. Authorization Capability Verification Test Suite
        test_code = '''from .manager import SystemIdentityManager
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
    mock_key = b"-----BEGIN PUBLIC KEY-----\nMOCK_KEY_BYTES\n-----END PUBLIC KEY-----"
    vault.store_public_key("cert_01", mock_key)
    assert vault.retrieve_public_key("cert_01") == mock_key
    
    print("✅ Cryptographic Authorization & RBAC Subsystem Integration Tests Passed.")

if __name__ == "__main__":
    test_auth_subsystem()
'''

        # Write out the full structural auth modules atomically
        with open(output_dir / "manager.py", "w") as f: f.write(manager_code.strip())
        with open(output_dir / "rbac.py", "w") as f: f.write(rbac_code.strip())
        with open(output_dir / "key_vault.py", "w") as f: f.write(key_vault_code.strip())
        with open(output_dir / "test_suite.py", "w") as f: f.write(test_code.strip())
        
        print(f"[GENERATOR-COMPLETE] auth_gen.py has compiled v1 Auth Subsystem inside {output_dir}")
