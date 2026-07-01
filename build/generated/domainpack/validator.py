import hmac
import hashlib

class DomainSignatureVerifier:
    def __init__(self, secret_key: bytes):
        self.secret = secret_key

    def sign_package(self, package_bytes: bytes) -> bytes:
        return hmac.new(self.secret, package_bytes, hashlib.sha256).digest()

    def verify_package(self, package_bytes: bytes, signature: bytes) -> bool:
        expected = hmac.new(self.secret, package_bytes, hashlib.sha256).digest()
        return hmac.compare_digest(expected, signature)