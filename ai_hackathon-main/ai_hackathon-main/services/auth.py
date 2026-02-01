"""
Auth service: JWT-based authentication for commercial deployment.
Set AUTH_ENABLED=true and JWT_SECRET in env to protect upload/status/download.
"""
import os
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

# Config from env
JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production-use-openssl-rand-hex-32")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "60"))
AUTH_ENABLED = os.getenv("AUTH_ENABLED", "false").lower() == "true"

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
http_bearer = HTTPBearer(auto_error=False)


# --- In-memory user store (MVP). Replace with DB for production. ---
_users_db: dict = {}  # email -> { "email", "hashed_password", "name", "created_at" }


def _load_users():
    """Load users from JSON file if AUTH_USERS_FILE is set (e.g. for Render)."""
    path = os.getenv("AUTH_USERS_FILE")
    if not path or not os.path.isfile(path):
        return
    import json
    try:
        with open(path, "r") as f:
            data = json.load(f)
        _users_db.clear()
        for u in data.get("users", []):
            _users_db[u["email"].lower()] = u
    except Exception:
        pass


def _save_users():
    path = os.getenv("AUTH_USERS_FILE")
    if not path:
        return
    import json
    try:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w") as f:
            json.dump({"users": list(_users_db.values())}, f, indent=2)
    except Exception:
        pass


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))
    to_encode["exp"] = expire
    to_encode["iat"] = datetime.utcnow()
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> Optional[dict]:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except JWTError:
        return None


# --- Pydantic models ---
class UserCreate(BaseModel):
    email: str
    password: str
    name: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class UserOut(BaseModel):
    email: str
    name: Optional[str] = None


def get_user_by_email(email: str) -> Optional[dict]:
    _load_users()
    return _users_db.get(email.lower())


def create_user(email: str, password: str, name: Optional[str] = None) -> dict:
    _load_users()
    email = email.lower().strip()
    if email in _users_db:
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed = hash_password(password)
    user = {
        "email": email,
        "hashed_password": hashed,
        "name": name or email.split("@")[0],
        "created_at": datetime.utcnow().isoformat(),
    }
    _users_db[email] = user
    _save_users()
    return user


def authenticate_user(email: str, password: str) -> Optional[dict]:
    _load_users()
    user = _users_db.get(email.lower())
    if not user or not verify_password(password, user["hashed_password"]):
        return None
    return user


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(http_bearer),
) -> Optional[dict]:
    """If AUTH_ENABLED, require valid JWT; else return None (anonymous allowed)."""
    if not AUTH_ENABLED:
        return None
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_token(credentials.credentials)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    user = get_user_by_email(payload["sub"])
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user
