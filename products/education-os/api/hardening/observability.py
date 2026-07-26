from __future__ import annotations

import json
import logging
import time
import uuid
from datetime import datetime, timezone

logger = logging.getLogger("little_oaks")


def structured_event(event: str, **fields):
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **fields,
    }
    logger.info(json.dumps(payload, default=str))


def request_id() -> str:
    return str(uuid.uuid4())


def elapsed_ms(start: float) -> int:
    return int((time.perf_counter() - start) * 1000)
