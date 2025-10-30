from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.estudiante import Estudiante
from app.schemas.bloqueo import BloqueoCreate, BloqueoResponse, BloqueoUpdate
from app.auth import get_current_user
from app.crud import bloqueo as crud_bloqueo
from app.exceptions import (
    BloqueoNotFoundError,
    EstudianteNotFoundError,
    BaseCustomException,
    map_exception_to_http
)
from app.config.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/bloqueos", tags=["Bloqueos"])

@router.post("/", response_model=BloqueoResponse, status_code=status.HTTP_201_CREATED)
def create_bloqueo(bloqueo: BloqueoCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo bloqueo.
    
    Args:
        bloqueo: Datos del bloqueo a crear
        db: Sesión de base de datos
        
    Returns:
        Bloqueo creado
        
    Raises:
        HTTPException: Si el estudiante no existe o ocurre un error
        
    Note:
        Este endpoint debería estar protegido para administradores.
        Por ahora está público para pruebas.
    """
    try:
        logger.info(f"Creando bloqueo para estudiante: {bloqueo.registro_academico}")
        
        # Crear bloqueo usando CRUD que maneja las validaciones
        db_bloqueo = crud_bloqueo.create_bloqueo(db, bloqueo)
        
        logger.info(f"Bloqueo creado exitosamente: {db_bloqueo.codigo_bloqueo}")
        return db_bloqueo
        
    except BaseCustomException as e:
        logger.warning(f"Error controlado al crear bloqueo: {e.message}")
        raise map_exception_to_http(e)
    except Exception as e:
        logger.error(f"Error inesperado al crear bloqueo: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/estudiante/{registro_academico}", response_model=List[BloqueoResponse])
def read_bloqueos_estudiante(
    registro_academico: str, 
    db: Session = Depends(get_db)
):
    """
    Obtener todos los bloqueos de un estudiante específico.
    
    Args:
        registro_academico: Registro académico del estudiante
        db: Sesión de base de datos
        
    Returns:
        Lista de bloqueos del estudiante
        
    Raises:
        HTTPException: Si ocurre un error al obtener los bloqueos
    """
    try:
        logger.info(f"Obteniendo bloqueos del estudiante: {registro_academico}")
        
        # Endpoint público, sin autenticación
        bloqueos = crud_bloqueo.get_bloqueos_by_estudiante(db, registro_academico)
        
        logger.info(f"Se encontraron {len(bloqueos)} bloqueos para el estudiante {registro_academico}")
        return bloqueos
        
    except BaseCustomException as e:
        logger.warning(f"Error controlado al obtener bloqueos del estudiante: {e.message}")
        raise map_exception_to_http(e)
    except Exception as e:
        logger.error(f"Error inesperado al obtener bloqueos del estudiante: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/{codigo_bloqueo}", response_model=BloqueoResponse)
def read_bloqueo(
    codigo_bloqueo: str, 
    db: Session = Depends(get_db),
):
    """
    Obtener un bloqueo específico por su código.
    
    Args:
        codigo_bloqueo: Código único del bloqueo
        db: Sesión de base de datos
        
    Returns:
        Información del bloqueo
        
    Raises:
        HTTPException: Si no se encuentra el bloqueo o ocurre un error
    """
    try:
        logger.info(f"Obteniendo bloqueo: {codigo_bloqueo}")
        
        db_bloqueo = crud_bloqueo.get_bloqueo(db, codigo_bloqueo)
        if not db_bloqueo:
            logger.warning(f"Bloqueo no encontrado: {codigo_bloqueo}")
            raise BloqueoNotFoundError(bloqueo_id=None)
        
        logger.info(f"Bloqueo obtenido exitosamente: {codigo_bloqueo}")
        return db_bloqueo
        
    except BaseCustomException as e:
        logger.warning(f"Error controlado al obtener bloqueo: {e.message}")
        raise map_exception_to_http(e)
    except Exception as e:
        logger.error(f"Error inesperado al obtener bloqueo: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.put("/{codigo_bloqueo}", response_model=BloqueoResponse)
def update_bloqueo(
    codigo_bloqueo: str, 
    bloqueo_update: BloqueoUpdate, 
    db: Session = Depends(get_db)
):
    """
    Actualizar un bloqueo existente.
    
    Args:
        codigo_bloqueo: Código único del bloqueo
        bloqueo_update: Datos a actualizar
        db: Sesión de base de datos
        
    Returns:
        Bloqueo actualizado
        
    Raises:
        HTTPException: Si no se encuentra el bloqueo o ocurre un error
        
    Note:
        Este endpoint debería estar protegido para administradores.
    """
    try:
        logger.info(f"Actualizando bloqueo: {codigo_bloqueo}")
        
        # Usar CRUD que maneja las validaciones
        db_bloqueo = crud_bloqueo.update_bloqueo(db, codigo_bloqueo, bloqueo_update)
        
        logger.info(f"Bloqueo actualizado exitosamente: {codigo_bloqueo}")
        return db_bloqueo
        
    except BaseCustomException as e:
        logger.warning(f"Error controlado al actualizar bloqueo: {e.message}")
        raise map_exception_to_http(e)
    except Exception as e:
        logger.error(f"Error inesperado al actualizar bloqueo: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/", response_model=List[BloqueoResponse])
def read_bloqueos(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtener lista de bloqueos con paginación.
    
    Args:
        skip: Número de registros a omitir
        limit: Máximo número de registros a retornar
        db: Sesión de base de datos
        
    Returns:
        Lista de bloqueos
        
    Raises:
        HTTPException: Si ocurre un error al obtener los bloqueos
        
    Note:
        Endpoint para administradores - por ahora público.
    """
    try:
        logger.info(f"Obteniendo lista de bloqueos con skip={skip}, limit={limit}")
        
        bloqueos = crud_bloqueo.get_bloqueos(db, skip, limit)
        
        logger.info(f"Se obtuvieron {len(bloqueos)} bloqueos")
        return bloqueos
        
    except BaseCustomException as e:
        logger.warning(f"Error controlado al obtener bloqueos: {e.message}")
        raise map_exception_to_http(e)
    except Exception as e:
        logger.error(f"Error inesperado al obtener bloqueos: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )