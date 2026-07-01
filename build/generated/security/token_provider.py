import hmac
import hashlib
import time

class SecurityTokenProvider:
    def __init__(self, secret_bytes):
        self.secret = secret_bytes

    def generate_token(self, identity, ttl_seconds=3600):
        expires = int(time.time()) + ttl_seconds
        payload = f"{identity}:{expires}"
        sig = hmac.new(self.secret, payload.encode('utf-8'), hashlib.sha256).hexdigest()
        return f"{payload}:{sig}"

    def validate_token(self, token_string):
        try:
            identity, expires_str, incoming_sig = token_string.split(":")
            expires = int(expires_str)
            
            if time.time() > expires:
                return False, "expired"
                
            re_payload = f"{identity}:{expires}"
            expected_sig = hmac.new(self.secret, re_payload.encode('utf-8'), hashlib.sha256).hexdigest()
            
            if hmac.compare_digest(expected_sig, incoming_sig):
                return True, identity
        except (ValueError, AttributeError):
            pass
        return False, "invalid"