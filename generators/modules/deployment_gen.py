from generators.core.base_gen import BaseGenerator
from pathlib import Path
import json

class DeploymentGenerator(BaseGenerator):
    def __init__(self, context):
        super().__init__(context)

    def generate(self):
        output_dir = Path(self.context.get("build_dir", "build/generated")) / "deployment"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Immutable Infrastructure Release Orchestrator
        engine_code = '''import os
import shutil

class ImmutableReleaseOrchestrator:
    def __init__(self, source_dir, target_release_dir="build/releases"):
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_release_dir)

    def assemble_release(self, version_tag):
        release_path = self.target_dir / f"a1os-{version_tag}"
        if release_path.exists():
            shutil.rmtree(release_path)
            
        shutil.copytree(self.source_dir, release_path)
        print(f"[DEPLOYMENT-ENG] Immutable release bundle compiled: {release_path}")
        return release_path
'''

        # 2. Artifact Packager and Dependency Assembler
        packer_code = '''import tarfile
from pathlib import Path

class RuntimeArtifactPackager:
    def __init__(self, base_path):
        self.base_path = Path(base_path)

    def pack_runtime(self, output_archive_path):
        with tarfile.open(output_archive_path, "w:gz") as tar:
            for file_path in self.base_path.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(self.base_path.parent)
                    tar.add(file_path, arcname=arcname)
        print(f"[DEPLOYMENT-PACKER] Compressed runtime archive written to: {output_archive_path}")
        return True
'''

        # 3. Cryptographic Release Manifest Generator
        manifest_code = '''import json
import hashlib
import time
from pathlib import Path

class ReleaseManifestGenerator:
    def __init__(self, build_dir):
        self.build_dir = Path(build_dir)

    def generate_sbom(self, version):
        manifest = {
            "version": version,
            "compiled_at": time.time(),
            "components": []
        }
        
        for p in self.build_dir.rglob("*.py"):
            if p.is_file():
                with open(p, "rb") as f:
                    h = hashlib.sha256(f.read()).hexdigest()
                manifest["components"].append({
                    "path": str(p.relative_to(self.build_dir.parent)),
                    "sha256": h
                })
                
        return manifest
'''

        # 4. Immutable Release Isolation Test Suite
        test_code = '''import tempfile
import tarfile
from pathlib import Path
from .engine import ImmutableReleaseOrchestrator
from .packer import RuntimeArtifactPackager
from .manifest import ReleaseManifestGenerator

def test_deployment_subsystem():
    with tempfile.TemporaryDirectory() as tmp_src, tempfile.TemporaryDirectory() as tmp_target:
        # Create a mock file in source directory
        mock_file = Path(tmp_src) / "core_module.py"
        mock_file.write_text("print('mock_runtime_layer')")
        
        # 1. Test release bundle compilation
        orchestrator = ImmutableReleaseOrchestrator(tmp_src, tmp_target)
        bundle_path = orchestrator.assemble_release("v1.0.0")
        assert bundle_path.exists()
        
        # 2. Test artifact compression packing
        packager = RuntimeArtifactPackager(tmp_src)
        archive_path = Path(tmp_target) / "release.tar.gz"
        assert packager.pack_runtime(archive_path) is True
        assert archive_path.exists()
        
        # 3. Test cryptographic Bill of Materials manifest generation
        manifest_gen = ReleaseManifestGenerator(tmp_src)
        manifest = manifest_gen.generate_sbom("v1.0.0")
        assert manifest["version"] == "v1.0.0"
        assert len(manifest["components"]) == 1
        
    print("✅ Immutable Runtime Deployment Subsystem Integration Tests Passed.")

if __name__ == "__main__":
    test_deployment_subsystem()
'''

        # Write out the full structural deployment modules atomically
        with open(output_dir / "engine.py", "w") as f: f.write(engine_code.strip())
        with open(output_dir / "packer.py", "w") as f: f.write(packer_code.strip())
        with open(output_dir / "manifest.py", "w") as f: f.write(manifest_code.strip())
        with open(output_dir / "test_suite.py", "w") as f: f.write(test_code.strip())
        
        print(f"[GENERATOR-COMPLETE] deployment_gen.py has compiled v1 Deployment Subsystem inside {output_dir}")
