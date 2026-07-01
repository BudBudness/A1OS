import tarfile
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