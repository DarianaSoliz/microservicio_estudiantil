from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import Token, UserLogin
from app.auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_current_user
from app.exceptions import (
    InvalidCredentialsError,
    BaseCustomException,
    map_exception_to_http
)
from app.config.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=Token, summary="Login con registro académico")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login de estudiante usando registro académico y contraseña.
    
    - **username**: Registro académico del estudiante (ej: 201812345)
    - **password**: Contraseña del estudiante
    
    Retorna un token JWT para autenticación.
    """
    try:
        logger.info(f"Intento de login para usuario: {form_data.username}")
        
        user = authenticate_user(db, form_data.username, form_data.password)
        if not user:
            logger.warning(f"Login fallido para usuario: {form_data.username}")
            raise InvalidCredentialsError()
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.registro_academico}, expires_delta=access_token_expires
        )
        
        logger.info(f"Login exitoso para usuario: {form_data.username}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except BaseCustomException as e:
        logger.warning(f"Error controlado en login: {e.message}")
        raise map_exception_to_http(e)
    except Exception as e:
        logger.error(f"Error inesperado en login: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.post("/login-estudiante", response_model=Token, summary="Login específico para estudiantes")
def login_estudiante(user_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login específico para estudiantes con registro académico.
    
    - **registro_academico**: Registro académico del estudiante (ej: 201812345)
    - **contrasena**: Contraseña del estudiante
    
    Retorna un token JWT para autenticación.
    """
    try:
        logger.info(f"Intento de login estudiante para: {user_data.registro_academico}")
        
        user = authenticate_user(db, user_data.registro_academico, user_data.contrasena)
        if not user:
            logger.warning(f"Login estudiante fallido para: {user_data.registro_academico}")
            raise InvalidCredentialsError()
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.registro_academico}, expires_delta=access_token_expires
        )
        
        logger.info(f"Login estudiante exitoso para: {user_data.registro_academico}")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except BaseCustomException as e:
        logger.warning(f"Error controlado en login estudiante: {e.message}")
        raise map_exception_to_http(e)
    except Exception as e:
        logger.error(f"Error inesperado en login estudiante: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/me", summary="Obtener información del usuario autenticado")
def get_current_user_info(current_user = Depends(get_current_user)):
    """
    Obtiene la información del estudiante autenticado actualmente.
    
    ## Cómo usar:
    1. Primero haz login en `/auth/login-estudiante`
    2. Copia el `access_token` de la respuesta
    3. Haz clic en 🔒 "Authorize" arriba a la derecha
    4. Pega el token en el campo (sin "Bearer")
    5. Haz clic en "Authorize"
    6. Ahora puedes usar este endpoint
    """
    try:
        logger.info(f"Obteniendo información del usuario autenticado: {current_user.registro_academico}")
        
        user_info = {
            "registro_academico": current_user.registro_academico,
            "nombre": f"{current_user.nombre} {current_user.apellido}",
            "correo": current_user.correo,
            "estado_academico": current_user.estado_academico,
            "codigo_carrera": current_user.codigo_carrera
        }
        
        logger.debug(f"Información del usuario obtenida exitosamente: {current_user.registro_academico}")
        return user_info
        
    except Exception as e:
        logger.error(f"Error al obtener información del usuario autenticado: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )