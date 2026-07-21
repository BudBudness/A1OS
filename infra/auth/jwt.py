import jwt
import datetime

SECRET = "CHANGE_ME_SUPER_SECRET"

def issue_token(user_id: str):
    return jwt.encode({
        "sub": user_id,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }, SECRET, algorithm="HS256")

def verify_token(token: str):
    return jwt.decode(token, SECRET, algorithms=["HS256"])
