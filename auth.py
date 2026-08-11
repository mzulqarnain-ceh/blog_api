from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta, timezone
from config import SECRET_KEY
from flask import jsonify, request
from functools import wraps
def hash_password(password):
    hash=generate_password_hash(password)
    return hash
def verify_password(password, password_hash):
    check_password=check_password_hash(password_hash,password)
    return check_password
def generate_token(user_id):
    payload={"user_id": user_id,"exp":datetime.now(timezone.utc) + timedelta(hours=1)}
    token=jwt.encode(payload, SECRET_KEY, algorithm="HS256")
    return token
def verify_token(token):
    try:
        decode=jwt.decode(token,SECRET_KEY,algorithms=["HS256"])
        return decode["user_id"]
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None
# decorator fuction
def token_required(f):
    # wraper function
    @wraps(f)
    def decorate(*args, **kwargs):
        header=request.headers.get("Authorization")
        if not header:
            return jsonify({"error":"Header is missing"}),401
        parts=header.split(" ")
        if len(parts) !=2 or parts[0].lower() != "bearer":
            return jsonify({"error":"Invalid token format. Must be 'Bearer <token>'"}),401
        token=parts[1]
        user_id=verify_token(token)
        if user_id is None:
            return jsonify({"error":"Ivalid or Expired token"}),401
        return f(user_id,*args,**kwargs)
    return decorate