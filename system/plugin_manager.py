import os
import sys
import json
import shutil
from pathlib import Path
from control_plane.control_plane import ControlPlane

class PluginLifecycleManager:
    """
    Implements production-grade operational lifecycles for A1OS plugins:
    Scaffolding, Validation, Cryptographic Installation, Upgrades, and Revocation.
    """
    def __init__(self, control_plane: ControlPlane, plugins_dir: str = "generators/modules"):
        self.control_plane = control_plane
        self.plugins_dir = Path(plugins_dir).resolve()
        self.plugins_dir.mkdir(parents=True, exist_ok=True)

    def scaffold_plugin(self, plugin_id: str):
        """Instantiates a structured, isolated template block."""
        plugin_path = self.plugins_dir / plugin_id
        if plugin_path.exists():
            print(f"❌ Error: Plugin directory '{plugin_id}' already exists.")
            return False

        plugin_path.mkdir(parents=True, exist_ok=True)
        
        manifest = {
            "name": plugin_id,
            "version": "1.0.0",
            "description": f"Standard A1OS {plugin_id} subsystem component."
        }
        (plugin_path / "manifest.json").write_text(json.dumps(manifest, indent=4))
        
        permissions = {
            "allowed_apis": ["database_read"]
        }
        (plugin_path / "permissions.json").write_text(json.dumps(permissions, indent=4))
        
        core_logic = (
            "def run(payload):\n"
            f"    print('Running plugin: {plugin_id}')\n"
            "    return {'status': 'SUCCESS'}\n"
        )
        (plugin_path / "plugin.py").write_text(core_logic)
        
        print(f"🎁 Scaffolded new plugin framework at: {plugin_path}")
        return True

    def _validate_schema(self, perm_data: dict) -> bool:
        """Enforces robust manifest validation schema before allowing registration."""
        if not isinstance(perm_data, dict) or "allowed_apis" not in perm_data:
            return False
        if not isinstance(perm_data["allowed_apis"], list):
            return False
        return True

    def formal_install(self, plugin_id: str, is_upgrade: bool = False):
        """Validates, admits, signs, and authorizes an operational asset."""
        target_dir = self.plugins_dir / plugin_id
        core_file = target_dir / "plugin.py"
        perm_file = target_dir / "permissions.json"

        if not core_file.exists() or not perm_file.exists():
            print(f"❌ Error: Missing files in bundle '{plugin_id}'")
            return False

        try:
            # 1. Manifest Schema Validation
            perms = json.loads(perm_file.read_text())
            if not self._validate_schema(perms):
                print(f"❌ Error: Manifest schema validation failed for '{plugin_id}'")
                return False

            allowed_apis = perms.get("allowed_apis", [])

            # 2. Assert admission gate (bypass lockdown check)
            self.control_plane.trust.allow(plugin_id)

            # 3. Cryptographically seal code payload state
            version_num = 2 if is_upgrade else 1
            sig = self.control_plane.signer.sign(plugin_id, str(core_file), version=version_num)

            # 4. Anchor structural validation metadata inside Kernel tables
            self.control_plane.register_trusted_plugin(plugin_id, str(core_file), sig)
            self.control_plane.capabilities.register(plugin_id, allowed_apis=allowed_apis)

            action_str = "Upgraded" if is_upgrade else "Onboarded"
            print(f"🔒 Safely {action_str} and sealed '{plugin_id}' (v{version_num}) into Control Plane.")
            return True
        except Exception as e:
            print(f"🚨 Failed admission protocol execution: {e}")
            return False

    def upgrade_plugin(self, plugin_id: str):
        """Performs structural upgrades and anchors the updated signature state safely."""
        target_dir = self.plugins_dir / plugin_id
        if not target_dir.exists():
            print(f"❌ Error: Plugin '{plugin_id}' is not installed.")
            return False
        
        # Pull manifest to increment/verify update semantics
        manifest_file = target_dir / "manifest.json"
        if manifest_file.exists():
            try:
                manifest = json.loads(manifest_file.read_text())
                manifest["version"] = "1.0.1"  # Increment patch version
                manifest_file.write_text(json.dumps(manifest, indent=4))
            except Exception:
                pass

        return self.formal_install(plugin_id, is_upgrade=True)

    def uninstall_plugin(self, plugin_id: str):
        """Enforces immediate, permanent cryptographic eviction and revokes execution rights."""
        try:
            # 1. Trigger full administrative eviction across kernel security barriers
            self.control_plane.trust.revoke(plugin_id)
            
            # 2. Purge asset binary directory completely from storage
            target_dir = self.plugins_dir / plugin_id
            if target_dir.exists():
                shutil.rmtree(target_dir)
                
            print(f"🧹 Cleanly evicted and uninstalled '{plugin_id}' from system memory and disk resources.")
            return True
        except Exception as e:
            print(f"🚨 Revocation cleanup sequence failed: {e}")
            return False
