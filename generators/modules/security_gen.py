from generators.core.base_gen import BaseGenerator
from pathlib import Path

class SecurityGenerator(BaseGenerator):
    def __init__(self, context):
        super().__init__(context)

    def generate(self):
        output_dir = Path(self.context.get("build_dir", "build/generated")) / "security"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 1. Primary Cryptographic Operational Gateway Matrix
        matrix_code = '''import hmac
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
'''

        # 2. Cryptographically Signed Timed Token Engine
        token_code = '''import hmac
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
'''

        # 3. Input String Validation and Boundary Sanitizer
        sanitizer_code = '''import re

class InputSanitizer:
    def __init__(self):
        # Strict alphanumeric character restriction matchers
        self.clean_pattern = re.compile(r'[^a-zA-Z0-9_=\-,. ]')

    def sanitize_command(self, raw_string):
        if not raw_string:
            return ""
        return self.clean_pattern.sub("", raw_string).strip()
'''

        # 4. Cryptographic Domain Isolation Test Suite
        test_code = '''import hmac
import hashlib
import time
from .matrix import SovereignSecurityMatrix
from .token_provider import SecurityTokenProvider
from .sanitizer import InputSanitizer

def test_security_subsystem():
    secret = b"test_secret_vector_999"
    matrix = SovereignSecurityMatrix("test_secret_vector_999")
    
    # 1. Signature validation assertion
    data = b"payload_bytes"
    sig = hmac.new(secret, data, hashlib.sha256).hexdigest()
    assert matrix.verify_webhook_signature(data, sig)
    
    # 2. Token generation/verification lifecycle check
    provider = SecurityTokenProvider(secret)
    token = provider.generate_token("admin_node", ttl_seconds=10)
    valid, identity = provider.validate_token(token)
    assert valid and identity == "admin_node"
    
    # 3. Injection protection filter test
    sanitizer = InputSanitizer()
    bad_string = "PING; DROP TABLE system_state; --"
    assert "DROP" not in sanitizer.sanitize_command(bad_string)
    
    print("✅ Cryptographic Security Subsystem Integration Tests Passed.")

if __name__ == "__main__":
    test_security_subsystem()
'''

        # Atomically write out the full security subsystem modules
        with open(output_dir / "matrix.py", "w") as f: f.write(matrix_code.strip())
        with open(output_dir / "token_provider.py", "w") as f: f.write(token_code.strip())
        with open(output_dir / "sanitizer.py", "w") as f: f.write(sanitizer_code.strip())
        with open(output_dir / "test_suite.py", "w") as f: f.write(test_code.strip())
        
        print(f"[GENERATOR-COMPLETE] security_gen.py has compiled v1 Security Subsystem inside {output_dir}")
