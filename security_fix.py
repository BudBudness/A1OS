from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import re

def validate_input(text):
    return re.sub(r'[^\w\s\-.,?!:;()]', '', text)

limiter = Limiter(key_func=get_remote_address, default_limits=["100 per hour", "10 per minute"])
