from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.estudiante import Estudiante
from app.schemas.auth import TokenData
import os
from dotenv import load_dotenv

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer()

def verify_password(plain_password, hashed_password):
    try:
        import bcrypt
        # Usar bcrypt directamente para evitar problemas con passlib
        password_bytes = plain_password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        
        return bcrypt.checkpw(password_bytes, hashed_password.encode('utf-8'))
    except Exception as e:
        print(f"Error verificando contraseña: {e}")
        return False

def get_password_hash(password):
    try:
        import bcrypt
        # Usar bcrypt directamente para evitar problemas con passlib
        password_bytes = password.encode('utf-8')
        if len(password_bytes) > 72:
            password_bytes = password_bytes[:72]
        
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password_bytes, salt)
        return hashed.decode('utf-8')
    except Exception as e:
        print(f"Error hasheando contraseña: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Error en el formato de la contraseña"
        )

def authenticate_user(db: Session, registro_academico: str, password: str):
    try:
        user = db.query(Estudiante).filter(Estudiante.registro_academico == registro_academico).first()
        if not user:
            return False
        if not user.contrasena:
            print(f"Usuario {registro_academico} no tiene contraseña configurada")
            return False
        if not verify_password(password, user.contrasena):
            return False
        return user
    except Exception as e:
        print(f"Error en authenticate_user: {e}")
        return False

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Extraer el token de las credenciales
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        registro_academico: str = payload.get("sub")
        if registro_academico is None:
            raise credentials_exception
        token_data = TokenData(registro_academico=registro_academico)
    except JWTError:
        raise credentials_exception
    
    user = db.query(Estudiante).filter(Estudiante.registro_academico == token_data.registro_academico).first()
    if user is None:
        raise credentials_exception
    return user