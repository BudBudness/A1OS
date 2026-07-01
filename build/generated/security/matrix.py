import hmac
import hashlib
import secrets

class SovereignSecurityMatrix:
    def __init__(self, signing_secret=None):
        self.secret = (signing_secret or secrets.token_hex(32)).encode('utf-8')

    def verify_webhook_signature(self, payload_bytes, incoming_signature, header_prefix="sha256="):
        """Validates payload authenticity using constant-time comparison"""
        if incoming_signature.startswith(header_prefix):
            incoming_signature = incoming_signature[len(header_prefix):]
            
        computed = hmac.new(self.secret, payload_bytes, hashlib.sha256).hexdigest()
        return hmac.compare_digest(computed, incoming_signature)