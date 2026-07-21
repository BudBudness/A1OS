import os
class LocalFileProvider:
    def write_file(self, path, content, approved=False):
        if not approved: raise PermissionError("Manual approval required.")
        with open(path, 'w') as f: f.write(content)
        return f"SUCCESS: {path} updated."
