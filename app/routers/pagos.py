from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.estudiante import Estudiante
from app.schemas.pago import PagoCreate, PagoResponse
from app.auth import get_current_user
from app.crud import pago as crud_pago
from app.exceptions import (
    PagoNotFoundError,
    EstudianteNotFoundError,
    InsufficientPermissionsError,
    BaseCustomException,
    map_exception_to_http
)
from app.config.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/pagos", tags=["Pagos"])

@router.post("/", response_model=PagoResponse, status_code=status.HTTP_201_CREATED)
def create_pago(
    pago: PagoCreate, 
    db: Session = Depends(get_db),
    current_user: Estudiante = Depends(get_current_user)
):
    """
    Crear un nuevo pago.
    
    Args:
        pago: Datos del pago a crear
        db: Sesión de base de datos
        current_user: Usuario autenticado actual
        
    Returns:
        Pago creado
        
    Raises:
        HTTPException: Si no tiene permisos, estudiante no existe o ocurre un error
    """
    try:
        logger.info(f"Creando pago para estudiante: {pago.registro_academico} por usuario: {current_user.registro_academico}")
        
        # Solo puede crear pagos para sí mismo (o implementar roles admin)
        if current_user.registro_academico != pago.registro_academico:
            logger.warning(f"Usuario {current_user.registro_academico} intentó crear pago para {pago.registro_academico}")
            raise InsufficientPermissionsError("crear pago para otro estudiante")
        
        # Crear pago usando CRUD que maneja las validaciones
        db_pago = crud_pago.create_pago(db, pago)
        
        logger.info(f"Pago creado exitosamente: {db_pago.codigo_pago}")
        return db_pago
        
    except BaseCustomException as e:
        logger.warning(f"Error controlado al crear pago: {e.message}")
        raise map_exception_to_http(e)
    except Exception as e:
        logger.error(f"Error inesperado al crear pago: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/estudiante/{registro_academico}", response_model=List[PagoResponse])
def read_pagos_estudiante(
    registro_academico: str, 
    db: Session = Depends(get_db)
):
    """
    Obtener todos los pagos de un estudiante específico.
    
    Args:
        registro_academico: Registro académico del estudiante
        db: Sesión de base de datos
        
    Returns:
        Lista de pagos del estudiante
        
    Raises:
        HTTPException: Si ocurre un error al obtener los pagos
    """
    try:
        logger.info(f"Obteniendo pagos del estudiante: {registro_academico}")
        
        # Endpoint público, sin autenticación
        pagos = crud_pago.get_pagos_by_estudiante(db, registro_academico)
        
        logger.info(f"Se encontraron {len(pagos)} pagos para el estudiante {registro_academico}")
        return pagos
        
    except BaseCustomException as e:
        logger.warning(f"Error controlado al obtener pagos del estudiante: {e.message}")
        raise map_exception_to_http(e)
    except Exception as e:
        logger.error(f"Error inesperado al obtener pagos del estudiante: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/{codigo_pago}", response_model=PagoResponse)
def read_pago(
    codigo_pago: str, 
    db: Session = Depends(get_db),
    current_user: Estudiante = Depends(get_current_user)
):
    """
    Obtener un pago específico por su código.
    
    Args:
        codigo_pago: Código único del pago
        db: Sesión de base de datos
        current_user: Usuario autenticado actual
        
    Returns:
        Información del pago
        
    Raises:
        HTTPException: Si no se encuentra el pago, no tiene permisos o ocurre un error
    """
    try:
        logger.info(f"Obteniendo pago: {codigo_pago} por usuario: {current_user.registro_academico}")
        
        db_pago = crud_pago.get_pago(db, codigo_pago)
        if not db_pago:
            logger.warning(f"Pago no encontrado: {codigo_pago}")
            raise PagoNotFoundError(pago_id=None)
        
        # Solo puede ver sus propios pagos (o implementar roles admin)
        if current_user.registro_academico != db_pago.registro_academico:
            logger.warning(f"Usuario {current_user.registro_academico} intentó acceder al pago {codigo_pago} de otro estudiante")
            raise InsufficientPermissionsError("ver pago de otro estudiante")
        
        logger.info(f"Pago obtenido exitosamente: {codigo_pago}")
        return db_pago
        
    except BaseCustomException as e:
        logger.warning(f"Error controlado al obtener pago: {e.message}")
        raise map_exception_to_http(e)
    except Exception as e:
        logger.error(f"Error inesperado al obtener pago: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/", response_model=List[PagoResponse])
def read_pagos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtener lista de pagos con paginación.
    
    Args:
        skip: Número de registros a omitir
        limit: Máximo número de registros a retornar
        db: Sesión de base de datos
        
    Returns:
        Lista de pagos
        
    Raises:
        HTTPException: Si ocurre un error al obtener los pagos
    """
    try:
        logger.info(f"Obteniendo lista de pagos con skip={skip}, limit={limit}")
        
        # Endpoint para administradores - por ahora público
        pagos = crud_pago.get_pagos(db, skip, limit)
        
        logger.info(f"Se obtuvieron {len(pagos)} pagos")
        return pagos
        
    except BaseCustomException as e:
        logger.warning(f"Error controlado al obtener pagos: {e.message}")
        raise map_exception_to_http(e)
    except Exception as e:
        logger.error(f"Error inesperado al obtener pagos: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )