from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.estudiante import EstudianteCreate, EstudianteResponse, EstudianteUpdate
from app.models.estudiante import Estudiante
from app.auth import get_current_user
from app.crud import estudiante as crud_estudiante
from app.exceptions import (
    EstudianteNotFoundError,
    EstudianteAlreadyExistsError,
    InsufficientPermissionsError,
    BaseCustomException,
    map_exception_to_http
)
from app.config.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/estudiantes", tags=["Estudiantes"])

@router.post("/", response_model=EstudianteResponse, status_code=status.HTTP_201_CREATED)
def create_estudiante(estudiante: EstudianteCreate, db: Session = Depends(get_db)):
    """
    Crear un nuevo estudiante.
    
    Args:
        estudiante: Datos del estudiante a crear
        db: Sesión de base de datos
        
    Returns:
        Estudiante creado
        
    Raises:
        HTTPException: Si ocurre algún error durante la creación
    """
    try:
        logger.info(f"Creando estudiante: {estudiante.registro_academico}")
        
        # Crear estudiante usando el CRUD que ya maneja las validaciones
        db_estudiante = crud_estudiante.create_estudiante(db, estudiante)
        
        logger.info(f"Estudiante creado exitosamente: {estudiante.registro_academico}")
        return db_estudiante
        
    except BaseCustomException as e:
        logger.warning(f"Error controlado al crear estudiante: {e.message}")
        raise map_exception_to_http(e)
    except Exception as e:
        logger.error(f"Error inesperado al crear estudiante: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/me", response_model=EstudianteResponse)
def read_estudiante_me(current_user: Estudiante = Depends(get_current_user)):
    """
    Obtener información del estudiante autenticado.
    
    Args:
        current_user: Usuario autenticado actual
        
    Returns:
        Información del estudiante autenticado
    """
    try:
        logger.info(f"Obteniendo información del estudiante autenticado: {current_user.registro_academico}")
        return current_user
        
    except Exception as e:
        logger.error(f"Error al obtener información del estudiante autenticado: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/{registro_academico}", response_model=EstudianteResponse)
def read_estudiante(registro_academico: str, db: Session = Depends(get_db)):
    """
    Obtener un estudiante por su registro académico.
    
    Args:
        registro_academico: Registro académico del estudiante
        db: Sesión de base de datos
        
    Returns:
        Información del estudiante
        
    Raises:
        HTTPException: Si no se encuentra el estudiante o ocurre un error
    """
    try:
        logger.info(f"Obteniendo estudiante: {registro_academico}")
        
        db_estudiante = crud_estudiante.get_estudiante(db, registro_academico)
        if not db_estudiante:
            logger.warning(f"Estudiante no encontrado: {registro_academico}")
            raise EstudianteNotFoundError(registro_academico=registro_academico)
        
        logger.info(f"Estudiante encontrado: {registro_academico}")
        return db_estudiante
        
    except BaseCustomException as e:
        logger.warning(f"Error controlado al obtener estudiante: {e.message}")
        raise map_exception_to_http(e)
    except Exception as e:
        logger.error(f"Error inesperado al obtener estudiante: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.get("/", response_model=List[EstudianteResponse])
def read_estudiantes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Obtener lista de estudiantes con paginación.
    
    Args:
        skip: Número de registros a omitir
        limit: Máximo número de registros a retornar
        db: Sesión de base de datos
        
    Returns:
        Lista de estudiantes
        
    Raises:
        HTTPException: Si ocurre un error al obtener los estudiantes
    """
    try:
        logger.info(f"Obteniendo lista de estudiantes con skip={skip}, limit={limit}")
        
        estudiantes = crud_estudiante.get_estudiantes(db, skip, limit)
        
        logger.info(f"Se obtuvieron {len(estudiantes)} estudiantes")
        return estudiantes
        
    except BaseCustomException as e:
        logger.warning(f"Error controlado al obtener estudiantes: {e.message}")
        raise map_exception_to_http(e)
    except Exception as e:
        logger.error(f"Error inesperado al obtener estudiantes: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.put("/{registro_academico}", response_model=EstudianteResponse)
def update_estudiante(
    registro_academico: str, 
    estudiante_update: EstudianteUpdate, 
    db: Session = Depends(get_db),
    current_user: Estudiante = Depends(get_current_user)
):
    """
    Actualizar información de un estudiante.
    
    Args:
        registro_academico: Registro académico del estudiante a actualizar
        estudiante_update: Datos a actualizar
        db: Sesión de base de datos
        current_user: Usuario autenticado actual
        
    Returns:
        Estudiante actualizado
        
    Raises:
        HTTPException: Si no se encuentra el estudiante, no tiene permisos o ocurre un error
    """
    try:
        logger.info(f"Actualizando estudiante: {registro_academico} por usuario: {current_user.registro_academico}")
        
        # Solo el propio estudiante puede actualizar sus datos
        if current_user.registro_academico != registro_academico:
            logger.warning(f"Usuario {current_user.registro_academico} intentó actualizar estudiante {registro_academico}")
            raise InsufficientPermissionsError("actualizar datos de otro estudiante")
        
        db_estudiante = crud_estudiante.update_estudiante(db, registro_academico, estudiante_update)
        
        logger.info(f"Estudiante actualizado exitosamente: {registro_academico}")
        return db_estudiante
        
    except BaseCustomException as e:
        logger.warning(f"Error controlado al actualizar estudiante: {e.message}")
        raise map_exception_to_http(e)
    except Exception as e:
        logger.error(f"Error inesperado al actualizar estudiante: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )

@router.delete("/{registro_academico}")
def delete_estudiante(
    registro_academico: str, 
    db: Session = Depends(get_db),
    current_user: Estudiante = Depends(get_current_user)
):
    """
    Eliminar un estudiante.
    
    Args:
        registro_academico: Registro académico del estudiante a eliminar
        db: Sesión de base de datos
        current_user: Usuario autenticado actual
        
    Returns:
        Mensaje de confirmación
        
    Raises:
        HTTPException: Si no se encuentra el estudiante, no tiene permisos o ocurre un error
    """
    try:
        logger.info(f"Eliminando estudiante: {registro_academico} por usuario: {current_user.registro_academico}")
        
        # Solo el propio estudiante puede eliminar sus datos (o implementar roles admin)
        if current_user.registro_academico != registro_academico:
            logger.warning(f"Usuario {current_user.registro_academico} intentó eliminar estudiante {registro_academico}")
            raise InsufficientPermissionsError("eliminar datos de otro estudiante")
        
        db_estudiante = crud_estudiante.delete_estudiante(db, registro_academico)
        
        logger.info(f"Estudiante eliminado exitosamente: {registro_academico}")
        return {"message": "Estudiante eliminado exitosamente"}
        
    except BaseCustomException as e:
        logger.warning(f"Error controlado al eliminar estudiante: {e.message}")
        raise map_exception_to_http(e)
    except Exception as e:
        logger.error(f"Error inesperado al eliminar estudiante: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno del servidor"
        )