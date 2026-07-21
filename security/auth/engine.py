import hmac, hashlib, json
class AuthEngine:
    def __init__(self): self.secret_key = b"a1os_secure_kernel_token_2026_secret"
    def verify_signature(self, b: bytes, s: str) -> bool:
        if not s: return False
        return hmac.compare_digest(hmac.new(self.secret_key, b, hashlib.sha256).hexdigest(), s)
    def generate_signature(self, p: dict) -> str:
        return hmac.new(self.secret_key, json.dumps(p, sort_keys=True).encode("utf-8"), hashlib.sha256).hexdigest()
