import hashlib
import time
from typing import Optional, Dict, Any
import jwt
from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()

# JWT Settings
JWT_SECRET = getattr(settings, "JWT_SECRET", "nuevamente_secret_key_2026_jwt_token_auth_secure")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_SECONDS = 60 * 60 * 24 * 7  # 7 days

# User In-Memory Persistent Store
USER_DB: Dict[str, Dict[str, Any]] = {
    "ana.martinez@empresa.com": {
        "email": "ana.martinez@empresa.com",
        "name": "Ana Martínez",
        "password_hash": hashlib.sha256("password123nuevamente_salt".encode()).hexdigest(),
        "created_at": time.time()
    },
    "fernando.garcia@empresa.com": {
        "email": "fernando.garcia@empresa.com",
        "name": "Fernando García",
        "password_hash": hashlib.sha256("securepasswordnuevamente_salt".encode()).hexdigest(),
        "created_at": time.time()
    }
}

class LoginRequest(BaseModel):
    email: str
    password: str
    name: Optional[str] = None

class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str

class GoogleAuthRequest(BaseModel):
    email: Optional[str] = None
    name: Optional[str] = None

def hash_password(password: str) -> str:
    salt = "nuevamente_salt"
    return hashlib.sha256((password + salt).encode("utf-8")).hexdigest()

def create_jwt_token(email: str, name: str) -> str:
    now = int(time.time())
    payload = {
        "sub": email,
        "name": name,
        "iat": now,
        "exp": now + JWT_EXPIRE_SECONDS,
        "iss": "nuevamente-auth-api"
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def decode_jwt_token(token: str) -> Dict[str, Any]:
    try:
        if token.startswith("Bearer "):
            token = token.split(" ", 1)[1]
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token de autenticación ha expirado.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Token de autenticación inválido.")

def extract_name(email: str, provided_name: Optional[str] = None) -> str:
    if provided_name and provided_name.strip():
        return provided_name.strip()
    if not email:
        return "Usuario Registrado"
    parts = email.split('@')[0].replace('.', ' ').replace('_', ' ').replace('-', ' ')
    return parts.title() if parts else "Usuario Registrado"

@router.post("/auth/register")
def register_user(request: RegisterRequest):
    email = request.email.strip().lower()
    name = request.name.strip()
    password = request.password.strip()

    if not email or not name or not password:
        raise HTTPException(status_code=400, detail="Nombre, correo electrónico y contraseña son requeridos.")
    
    if len(password) < 4:
        raise HTTPException(status_code=400, detail="La contraseña debe tener al menos 4 caracteres.")

    hashed = hash_password(password)
    USER_DB[email] = {
        "email": email,
        "name": name,
        "password_hash": hashed,
        "created_at": time.time()
    }

    token = create_jwt_token(email, name)
    avatar_char = name[0].upper() if name else "U"

    return {
        "status": "exito",
        "message": f"Cuenta creada exitosamente para {name}",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "name": name,
            "email": email,
            "avatarLetter": avatar_char,
            "isLoggedIn": True
        }
    }

@router.post("/auth/login")
def login_user(request: LoginRequest):
    email = request.email.strip().lower()
    password = request.password.strip()

    if not email or not password:
        raise HTTPException(status_code=400, detail="El correo electrónico y la contraseña son requeridos.")

    user_record = USER_DB.get(email)
    if user_record:
        if user_record["password_hash"] != hash_password(password):
            raise HTTPException(status_code=401, detail="Contraseña incorrecta. Por favor verifica tus credenciales.")
        user_name = user_record["name"]
    else:
        user_name = extract_name(email, request.name)
        USER_DB[email] = {
            "email": email,
            "name": user_name,
            "password_hash": hash_password(password),
            "created_at": time.time()
        }

    token = create_jwt_token(email, user_name)
    avatar_char = user_name[0].upper() if user_name else "U"

    return {
        "status": "exito",
        "message": f"Bienvenido de nuevo, {user_name}",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "name": user_name,
            "email": email,
            "avatarLetter": avatar_char,
            "isLoggedIn": True
        }
    }

@router.post("/auth/google")
def google_auth(request: GoogleAuthRequest):
    email = (request.email.strip().lower()) if request.email else "usuario.google@gmail.com"
    name = request.name.strip() if request.name else extract_name(email)

    if email not in USER_DB:
        USER_DB[email] = {
            "email": email,
            "name": name,
            "password_hash": hash_password("google_sso_pass"),
            "created_at": time.time()
        }

    token = create_jwt_token(email, name)
    avatar_char = name[0].upper() if name else "G"

    return {
        "status": "exito",
        "message": f"Autenticado correctamente con Google como {name}",
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "name": name,
            "email": email,
            "avatarLetter": avatar_char,
            "isLoggedIn": True
        }
    }

@router.get("/auth/me")
def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Header Authorization con token Bearer es requerido.")
    payload = decode_jwt_token(authorization)
    email = payload.get("sub", "")
    name = payload.get("name", "")
    avatar_char = name[0].upper() if name else "U"

    return {
        "status": "exito",
        "user": {
            "name": name,
            "email": email,
            "avatarLetter": avatar_char,
            "isLoggedIn": True
        }
    }
