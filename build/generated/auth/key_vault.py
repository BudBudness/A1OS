class CryptographicKeyVault:
    def __init__(self):
        self._keys = {}

    def store_public_key(self, key_id, pem_bytes):
        self._keys[key_id] = pem_bytes
        print(f"[KEY-VAULT] Public key registered for identity anchor: {key_id}")

    def retrieve_public_key(self, key_id):
        return self._keys.get(key_id)