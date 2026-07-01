import os
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