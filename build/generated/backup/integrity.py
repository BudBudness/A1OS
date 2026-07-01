import hashlib

class BackupIntegrityVerifier:
    @staticmethod
    def compute_sha256(data_bytes):
        return hashlib.sha256(data_bytes).hexdigest()

    @staticmethod
    def verify_integrity(snapshot_data, expected_hash):
        computed = hashlib.sha256(str(snapshot_data).encode("utf-8")).hexdigest()
        return computed == expected_hash