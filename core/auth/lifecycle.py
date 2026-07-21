import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from core.persistence.database import Database

class AuthLifecycle:
    @staticmethod
    def hash_token(token):
        return hashlib.sha256(token.encode()).hexdigest()

    @classmethod
    def create_session(cls, subject, ttl_hours=24):
        token = secrets.token_urlsafe(48)
        token_hash = cls.hash_token(token)
        session_id = secrets.token_hex(16)
        expires = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)

        Database.execute(
            """
            INSERT INTO auth_sessions
            (session_id,subject,token_hash,expires_at)
            VALUES (?,?,?,?)
            """,
            (session_id, subject, token_hash, expires.isoformat())
        )
        return session_id, token

    @classmethod
    def validate(cls, token):
        token_hash = cls.hash_token(token)
        row = Database.fetchone(
            """
            SELECT * FROM auth_sessions
            WHERE token_hash=?
            AND revoked=0
            AND expires_at > CURRENT_TIMESTAMP
            """,
            (token_hash,)
        )
        return row

    @classmethod
    def revoke(cls, token):
        Database.execute(
            "UPDATE auth_sessions SET revoked=1 WHERE token_hash=?",
            (cls.hash_token(token),)
        )
