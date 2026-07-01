import hmac
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