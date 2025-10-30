from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models.estudiante import Estudiante
from app.schemas.estudiante import EstudianteCreate, EstudianteUpdate
from app.auth import get_password_hash
from app.exceptions import (
    EstudianteNotFoundError,
    EstudianteAlreadyExistsError,
    DatabaseError,
    ValidationError
)
from app.config.logging import get_logger, log_function_call, log_execution_time

logger = get_logger(__name__)

@log_function_call
@log_execution_time
def get_estudiante(db: Session, registro_academico: str):
    """
    Obtiene un estudiante por su registro académico.
    
    Args:
        db: Sesión de base de datos
        registro_academico: Registro académico del estudiante
        
    Returns:
        Estudiante encontrado o None
        
    Raises:
        DatabaseError: Si ocurre un error de base de datos
    """
    try:
        logger.info(f"Buscando estudiante con registro académico: {registro_academico}")
        
        if not registro_academico or not registro_academico.strip():
            logger.warning("Se proporcionó un registro académico vacío o nulo")
            raise ValidationError("El registro académico es requerido")
        
        estudiante = db.query(Estudiante).filter(Estudiante.registro_academico == registro_academico).first()
        
        if estudiante:
            logger.info(f"Estudiante encontrado: {registro_academico}")
        else:
            logger.info(f"No se encontró estudiante con registro académico: {registro_academico}")
            
        return estudiante
        
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos al buscar estudiante {registro_academico}: {str(e)}")
        raise DatabaseError(f"Error al buscar estudiante: {str(e)}")
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al buscar estudiante {registro_academico}: {str(e)}")
        raise DatabaseError(f"Error inesperado al buscar estudiante: {str(e)}")

@log_function_call
@log_execution_time
def get_estudiante_by_ci(db: Session, ci: str):
    """
    Obtiene un estudiante por su CI.
    
    Args:
        db: Sesión de base de datos
        ci: CI del estudiante
        
    Returns:
        Estudiante encontrado o None
        
    Raises:
        DatabaseError: Si ocurre un error de base de datos
        ValidationError: Si el CI es inválido
    """
    try:
        logger.info(f"Buscando estudiante con CI: {ci}")
        
        if not ci or not ci.strip():
            logger.warning("Se proporcionó un CI vacío o nulo")
            raise ValidationError("El CI es requerido")
        
        estudiante = db.query(Estudiante).filter(Estudiante.ci == ci).first()
        
        if estudiante:
            logger.info(f"Estudiante encontrado con CI: {ci}")
        else:
            logger.info(f"No se encontró estudiante con CI: {ci}")
            
        return estudiante
        
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos al buscar estudiante por CI {ci}: {str(e)}")
        raise DatabaseError(f"Error al buscar estudiante por CI: {str(e)}")
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al buscar estudiante por CI {ci}: {str(e)}")
        raise DatabaseError(f"Error inesperado al buscar estudiante por CI: {str(e)}")

@log_function_call
@log_execution_time
def get_estudiantes(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene una lista paginada de estudiantes.
    
    Args:
        db: Sesión de base de datos
        skip: Número de registros a omitir
        limit: Máximo número de registros a retornar
        
    Returns:
        Lista de estudiantes
        
    Raises:
        DatabaseError: Si ocurre un error de base de datos
        ValidationError: Si los parámetros de paginación son inválidos
    """
    try:
        logger.info(f"Obteniendo estudiantes con skip={skip}, limit={limit}")
        
        if skip < 0:
            logger.warning(f"Valor de skip inválido: {skip}")
            raise ValidationError("El valor de skip debe ser mayor o igual a 0")
            
        if limit < 1 or limit > 1000:
            logger.warning(f"Valor de limit inválido: {limit}")
            raise ValidationError("El valor de limit debe estar entre 1 y 1000")
        
        estudiantes = db.query(Estudiante).offset(skip).limit(limit).all()
        
        logger.info(f"Se obtuvieron {len(estudiantes)} estudiantes")
        return estudiantes
        
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos al obtener estudiantes: {str(e)}")
        raise DatabaseError(f"Error al obtener estudiantes: {str(e)}")
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al obtener estudiantes: {str(e)}")
        raise DatabaseError(f"Error inesperado al obtener estudiantes: {str(e)}")

@log_function_call
@log_execution_time
def create_estudiante(db: Session, estudiante: EstudianteCreate):
    """
    Crea un nuevo estudiante.
    
    Args:
        db: Sesión de base de datos
        estudiante: Datos del estudiante a crear
        
    Returns:
        Estudiante creado
        
    Raises:
        EstudianteAlreadyExistsError: Si ya existe un estudiante con el mismo registro académico o CI
        DatabaseError: Si ocurre un error de base de datos
        ValidationError: Si los datos del estudiante son inválidos
    """
    try:
        logger.info(f"Creando nuevo estudiante con registro académico: {estudiante.registro_academico}")
        
        # Verificar si ya existe el registro académico
        existing_student = get_estudiante(db, estudiante.registro_academico)
        if existing_student:
            logger.warning(f"Ya existe estudiante con registro académico: {estudiante.registro_academico}")
            raise EstudianteAlreadyExistsError("registro_academico", estudiante.registro_academico)
        
        # Verificar si ya existe el CI
        if estudiante.ci:
            existing_ci = get_estudiante_by_ci(db, estudiante.ci)
            if existing_ci:
                logger.warning(f"Ya existe estudiante con CI: {estudiante.ci}")
                raise EstudianteAlreadyExistsError("ci", estudiante.ci)
        
        # Crear datos del estudiante
        estudiante_data = estudiante.dict()
        estudiante_data["contrasena"] = get_password_hash(estudiante.contrasena)
        
        db_estudiante = Estudiante(**estudiante_data)
        db.add(db_estudiante)
        db.commit()
        db.refresh(db_estudiante)
        
        logger.info(f"Estudiante creado exitosamente: {estudiante.registro_academico}")
        return db_estudiante
        
    except EstudianteAlreadyExistsError:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al crear estudiante: {str(e)}")
        if "registro_academico" in str(e):
            raise EstudianteAlreadyExistsError("registro_academico", estudiante.registro_academico)
        elif "ci" in str(e):
            raise EstudianteAlreadyExistsError("ci", estudiante.ci)
        else:
            raise DatabaseError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de base de datos al crear estudiante: {str(e)}")
        raise DatabaseError(f"Error al crear estudiante: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al crear estudiante: {str(e)}")
        raise DatabaseError(f"Error inesperado al crear estudiante: {str(e)}")

@log_function_call
@log_execution_time
def update_estudiante(db: Session, registro_academico: str, estudiante_update: EstudianteUpdate):
    """
    Actualiza un estudiante existente.
    
    Args:
        db: Sesión de base de datos
        registro_academico: Registro académico del estudiante a actualizar
        estudiante_update: Datos a actualizar
        
    Returns:
        Estudiante actualizado
        
    Raises:
        EstudianteNotFoundError: Si no se encuentra el estudiante
        EstudianteAlreadyExistsError: Si se intenta cambiar a un CI que ya existe
        DatabaseError: Si ocurre un error de base de datos
    """
    try:
        logger.info(f"Actualizando estudiante con registro académico: {registro_academico}")
        
        db_estudiante = db.query(Estudiante).filter(Estudiante.registro_academico == registro_academico).first()
        if not db_estudiante:
            logger.warning(f"No se encontró estudiante para actualizar: {registro_academico}")
            raise EstudianteNotFoundError(registro_academico=registro_academico)
        
        update_data = estudiante_update.dict(exclude_unset=True)
        
        # Si se está actualizando el CI, verificar que no exista
        if "ci" in update_data and update_data["ci"]:
            existing_ci = db.query(Estudiante).filter(
                Estudiante.ci == update_data["ci"],
                Estudiante.registro_academico != registro_academico
            ).first()
            if existing_ci:
                logger.warning(f"CI ya existe en otro estudiante: {update_data['ci']}")
                raise EstudianteAlreadyExistsError("ci", update_data["ci"])
        
        # Si se está actualizando la contraseña, hashearla
        if "contrasena" in update_data:
            update_data["contrasena"] = get_password_hash(update_data["contrasena"])
        
        for field, value in update_data.items():
            setattr(db_estudiante, field, value)
        
        db.commit()
        db.refresh(db_estudiante)
        
        logger.info(f"Estudiante actualizado exitosamente: {registro_academico}")
        return db_estudiante
        
    except EstudianteNotFoundError:
        raise
    except EstudianteAlreadyExistsError:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al actualizar estudiante: {str(e)}")
        if "ci" in str(e):
            raise EstudianteAlreadyExistsError("ci", update_data.get("ci", ""))
        else:
            raise DatabaseError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de base de datos al actualizar estudiante: {str(e)}")
        raise DatabaseError(f"Error al actualizar estudiante: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al actualizar estudiante: {str(e)}")
        raise DatabaseError(f"Error inesperado al actualizar estudiante: {str(e)}")

@log_function_call
@log_execution_time
def delete_estudiante(db: Session, registro_academico: str):
    """
    Elimina un estudiante.
    
    Args:
        db: Sesión de base de datos
        registro_academico: Registro académico del estudiante a eliminar
        
    Returns:
        Estudiante eliminado
        
    Raises:
        EstudianteNotFoundError: Si no se encuentra el estudiante
        DatabaseError: Si ocurre un error de base de datos
    """
    try:
        logger.info(f"Eliminando estudiante con registro académico: {registro_academico}")
        
        db_estudiante = db.query(Estudiante).filter(Estudiante.registro_academico == registro_academico).first()
        if not db_estudiante:
            logger.warning(f"No se encontró estudiante para eliminar: {registro_academico}")
            raise EstudianteNotFoundError(registro_academico=registro_academico)
        
        db.delete(db_estudiante)
        db.commit()
        
        logger.info(f"Estudiante eliminado exitosamente: {registro_academico}")
        return db_estudiante
        
    except EstudianteNotFoundError:
        raise
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de base de datos al eliminar estudiante: {str(e)}")
        raise DatabaseError(f"Error al eliminar estudiante: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al eliminar estudiante: {str(e)}")
        raise DatabaseError(f"Error inesperado al eliminar estudiante: {str(e)}")