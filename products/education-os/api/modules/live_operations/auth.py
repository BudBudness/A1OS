
from fastapi import APIRouter
import sqlite3, hashlib, secrets

router=APIRouter(prefix="/v1/auth",tags=["auth"])

DB="deployments/little-oaks/data/education.db"

@router.post("/login")
def login(email:str,password:str):

    conn=sqlite3.connect(DB)

    h=hashlib.sha256(password.encode()).hexdigest()

    user=conn.execute(
    "SELECT id,name,role_id FROM users WHERE email=? AND password_hash=?",
    (email,h)
    ).fetchone()

    if not user:
        return {"error":"invalid credentials"}

    token=secrets.token_hex(32)

    conn.execute(
    "INSERT INTO auth_tokens(user_id,token) VALUES(?,?)",
    (user[0],token)
    )

    conn.commit()
    conn.close()

    return {
    "token":token,
    "user_id":user[0],
    "name":user[1]
    }
