import time

class SnapshotRetentionPolicy:
    def __init__(self, ttl_seconds=3600):
        self.ttl = ttl_seconds

    def prune_expired(self, snapshot_registry):
        now = time.time()
        pruned = []
        for sid, meta in list(snapshot_registry.items()):
            if now - meta["created_at"] > self.ttl:
                del snapshot_registry[sid]
                pruned.append(sid)
        if pruned:
            print(f"[BACKUP-RETENTION] Pruned expired recovery snapshots: {pruned}")
        return pruned