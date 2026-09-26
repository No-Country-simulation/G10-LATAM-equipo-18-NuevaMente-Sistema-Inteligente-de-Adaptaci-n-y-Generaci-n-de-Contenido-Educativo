from typing import Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr

router = APIRouter()

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

def extract_name(email: str, provided_name: Optional[str] = None) -> str:
    if provided_name and provided_name.trim() if hasattr(provided_name, 'trim') else provided_name:
        return provided_name.strip()
    if not email:
        return "Usuario Registrado"
    parts = email.split('@')[0].replace('.', ' ').replace('_', ' ').replace('-', ' ')
    return parts.title() if parts else "Usuario Registrado"

@router.post("/auth/login")
def login_user(request: LoginRequest):
    if not request.email:
        raise HTTPException(status_code=400, detail="El correo electrónico es requerido.")
    
    user_name = extract_name(request.email, request.name)
    avatar_char = user_name[0].upper() if user_name else "U"

    return {
        "status": "exito",
        "message": f"Bienvenido de nuevo, {user_name}",
        "access_token": f"bearer_token_{Date_mock()}",
        "user": {
            "name": user_name,
            "email": request.email.strip(),
            "avatarLetter": avatar_char,
            "isLoggedIn": True
        }
    }

@router.post("/auth/register")
def register_user(request: RegisterRequest):
    if not request.email or not request.name:
        raise HTTPException(status_code=400, detail="El nombre y correo son requeridos para el registro.")
    
    user_name = request.name.strip()
    avatar_char = user_name[0].upper() if user_name else "U"

    return {
        "status": "exito",
        "message": f"Cuenta creada exitosamente para {user_name}",
        "access_token": f"bearer_token_{Date_mock()}",
        "user": {
            "name": user_name,
            "email": request.email.strip(),
            "avatarLetter": avatar_char,
            "isLoggedIn": True
        }
    }

@router.post("/auth/google")
def google_auth(request: GoogleAuthRequest):
    email = request.email.strip() if request.email else "usuario.google@gmail.com"
    name = request.name.strip() if request.name else extract_name(email)
    avatar_char = name[0].upper() if name else "G"

    return {
        "status": "exito",
        "message": f"Autenticado correctamente con Google como {name}",
        "access_token": f"bearer_google_token_{Date_mock()}",
        "user": {
            "name": name,
            "email": email,
            "avatarLetter": avatar_char,
            "isLoggedIn": True
        }
    }

def Date_mock():
    import time
    return int(time.time())
