from .manager import RecoverySnapshotManager
from .integrity import BackupIntegrityVerifier
from .retention import SnapshotRetentionPolicy
import time

def test_backup_subsystem():
    # 1. Create and retrieve point-in-time state recovery checkpoints
    manager = RecoverySnapshotManager()
    assert manager.create_snapshot("snap_01", {"system_state": "online"}) is True
    snap = manager.retrieve_snapshot("snap_01")
    assert snap is not None
    assert snap["status"] == "sealed"
    
    # 2. Cryptographic backup verification assertion
    payload = {"frozen_ledger_index": 42}
    expected_hash = BackupIntegrityVerifier.compute_sha256(str(payload).encode("utf-8"))
    assert BackupIntegrityVerifier.verify_integrity(payload, expected_hash) is True
    
    # 3. Retention policy pruning checks
    policy = SnapshotRetentionPolicy(ttl_seconds=0.1)
    manager.create_snapshot("snap_expired", {"state": "stale"})
    time.sleep(0.2)
    policy.prune_expired(manager.snapshots)
    assert manager.retrieve_snapshot("snap_expired") is None
    
    print("✅ Disaster Recovery Snapshot & Retention Subsystem Integration Tests Passed.")

if __name__ == "__main__":
    test_backup_subsystem()