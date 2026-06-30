import hashlib
class PluginSigner:
    def sign(self, name, path):
        try:
            with open(path, "rb") as f: data = f.read()
        except: return ""
        return hashlib.sha256(data + name.encode()).hexdigest()
    def verify(self, name, path, signature): return self.sign(name, path) == signature
