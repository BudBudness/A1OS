from core.persistence.engine import StateManager

# Initialize and persist test data
manager = StateManager()
manager.save_state("task_001", {"status": "pending", "payload": "verified"})

# Retrieve and confirm
state = manager.get_state("task_001")
print(f"Verified State: {state}")


def test_checkpoint_save_and_latest(tmp_path):
    from core.recovery.checkpoints import CheckpointStore

    db = tmp_path / "recovery.db"
    store = CheckpointStore(str(db))

    state = {
        "execution_id": "persistence-gate",
        "status": "completed",
        "result": {"x": 42},
    }

    checkpoint_id = store.save("persistence_gate", state)

    assert checkpoint_id

    restored = store.latest("persistence_gate")

    assert restored is not None
    assert restored["checkpoint_id"] == checkpoint_id
    assert restored["component"] == "persistence_gate"
    assert restored["state"] == state
