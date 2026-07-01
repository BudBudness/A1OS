import tempfile
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