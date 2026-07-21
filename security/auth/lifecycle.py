import hashlib
import hmac
import secrets
import sqlite3
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DB = ROOT / "data" / "a1os.db"

def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def create_session(subject: str, ttl_seconds: int = 3600) -> str:
    token = secrets.token_urlsafe(48)
    token_hash = _hash_token(token)
    now = int(time.time())
    expires = now + ttl_seconds

    with sqlite3.connect(DB) as conn:
        conn.execute(
            """
            INSERT INTO auth_sessions
            (token_hash, subject, created_at, expires_at, revoked)
            VALUES (?, ?, ?, ?, 0)
            """,
            (token_hash, subject, now, expires),
        )
        conn.commit()

    return token

def validate_session(token: str) -> bool:
    token_hash = _hash_token(token)
    now = int(time.time())

    with sqlite3.connect(DB) as conn:
        row = conn.execute(
            """
            SELECT token_hash
            FROM auth_sessions
            WHERE token_hash = ?
              AND revoked = 0
              AND expires_at > ?
            """,
            (token_hash, now),
        ).fetchone()

    return bool(row and hmac.compare_digest(row[0], token_hash))

def revoke_session(token: str) -> None:
    with sqlite3.connect(DB) as conn:
        conn.execute(
            "UPDATE auth_sessions SET revoked = 1 WHERE token_hash = ?",
            (_hash_token(token),),
        )
        conn.commit()

def purge_expired_sessions() -> int:
    now = int(time.time())

    with sqlite3.connect(DB) as conn:
        cur = conn.execute(
            "DELETE FROM auth_sessions WHERE expires_at <= ?",
            (now,),
        )
        conn.commit()
        return cur.rowcount
