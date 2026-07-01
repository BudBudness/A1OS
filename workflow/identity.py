import hashlib
class IdentityManager:
    @staticmethod
    def sign_request(secret, task_id):
        return hashlib.sha256(f"{secret}:{task_id}".encode()).hexdigest()
    @staticmethod
    def verify_identity(signature, secret, task_id):
        return signature == IdentityManager.sign_request(secret, task_id)
