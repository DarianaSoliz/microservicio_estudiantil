from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models.bloqueo import Bloqueo
from app.models.estudiante import Estudiante
from app.schemas.bloqueo import BloqueoCreate, BloqueoUpdate
from app.exceptions import (
    BloqueoNotFoundError,
    EstudianteNotFoundError,
    DatabaseError,
    ValidationError
)
from app.config.logging import get_logger, log_function_call, log_execution_time

logger = get_logger(__name__)

@log_function_call
@log_execution_time
def generate_codigo_bloqueo(db: Session):
    """
    Genera un código único para el bloqueo.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Código de bloqueo generado
        
    Raises:
        DatabaseError: Si ocurre un error de base de datos
    """
    try:
        logger.debug("Generando nuevo código de bloqueo")
        
        last_bloqueo = db.query(Bloqueo).order_by(Bloqueo.codigo_bloqueo.desc()).first()
        if last_bloqueo:
            last_number = int(last_bloqueo.codigo_bloqueo[1:])  # Quitar la 'B' del inicio
            new_number = last_number + 1
        else:
            new_number = 1
        
        codigo = f"B{new_number:05d}"
        logger.debug(f"Código de bloqueo generado: {codigo}")
        return codigo
        
    except ValueError as e:
        logger.error(f"Error al procesar código de bloqueo: {str(e)}")
        raise DatabaseError(f"Error al generar código de bloqueo: {str(e)}")
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos al generar código de bloqueo: {str(e)}")
        raise DatabaseError(f"Error al generar código de bloqueo: {str(e)}")
    except Exception as e:
        logger.error(f"Error inesperado al generar código de bloqueo: {str(e)}")
        raise DatabaseError(f"Error inesperado al generar código de bloqueo: {str(e)}")


@log_function_call
@log_execution_time
def get_bloqueo(db: Session, codigo_bloqueo: str):
    """
    Obtiene un bloqueo por su código.
    
    Args:
        db: Sesión de base de datos
        codigo_bloqueo: Código del bloqueo
        
    Returns:
        Bloqueo encontrado o None
        
    Raises:
        DatabaseError: Si ocurre un error de base de datos
        ValidationError: Si el código de bloqueo es inválido
    """
    try:
        logger.info(f"Buscando bloqueo con código: {codigo_bloqueo}")
        
        if not codigo_bloqueo or not codigo_bloqueo.strip():
            logger.warning("Se proporcionó un código de bloqueo vacío o nulo")
            raise ValidationError("El código de bloqueo es requerido")
        
        bloqueo = db.query(Bloqueo).filter(Bloqueo.codigo_bloqueo == codigo_bloqueo).first()
        
        if bloqueo:
            logger.info(f"Bloqueo encontrado: {codigo_bloqueo}")
        else:
            logger.info(f"No se encontró bloqueo con código: {codigo_bloqueo}")
            
        return bloqueo
        
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos al buscar bloqueo {codigo_bloqueo}: {str(e)}")
        raise DatabaseError(f"Error al buscar bloqueo: {str(e)}")
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al buscar bloqueo {codigo_bloqueo}: {str(e)}")
        raise DatabaseError(f"Error inesperado al buscar bloqueo: {str(e)}")


@log_function_call
@log_execution_time
def get_bloqueos_by_estudiante(db: Session, registro_academico: str):
    """
    Obtiene todos los bloqueos de un estudiante.
    
    Args:
        db: Sesión de base de datos
        registro_academico: Registro académico del estudiante
        
    Returns:
        Lista de bloqueos del estudiante
        
    Raises:
        DatabaseError: Si ocurre un error de base de datos
        ValidationError: Si el registro académico es inválido
    """
    try:
        logger.info(f"Obteniendo bloqueos del estudiante: {registro_academico}")
        
        if not registro_academico or not registro_academico.strip():
            logger.warning("Se proporcionó un registro académico vacío o nulo")
            raise ValidationError("El registro académico es requerido")
        
        bloqueos = db.query(Bloqueo).filter(Bloqueo.registro_academico == registro_academico).all()
        
        logger.info(f"Se encontraron {len(bloqueos)} bloqueos para el estudiante {registro_academico}")
        return bloqueos
        
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos al obtener bloqueos del estudiante {registro_academico}: {str(e)}")
        raise DatabaseError(f"Error al obtener bloqueos del estudiante: {str(e)}")
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al obtener bloqueos del estudiante {registro_academico}: {str(e)}")
        raise DatabaseError(f"Error inesperado al obtener bloqueos del estudiante: {str(e)}")


@log_function_call
@log_execution_time
def get_bloqueos(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene una lista paginada de bloqueos.
    
    Args:
        db: Sesión de base de datos
        skip: Número de registros a omitir
        limit: Máximo número de registros a retornar
        
    Returns:
        Lista de bloqueos
        
    Raises:
        DatabaseError: Si ocurre un error de base de datos
        ValidationError: Si los parámetros de paginación son inválidos
    """
    try:
        logger.info(f"Obteniendo bloqueos con skip={skip}, limit={limit}")
        
        if skip < 0:
            logger.warning(f"Valor de skip inválido: {skip}")
            raise ValidationError("El valor de skip debe ser mayor o igual a 0")
            
        if limit < 1 or limit > 1000:
            logger.warning(f"Valor de limit inválido: {limit}")
            raise ValidationError("El valor de limit debe estar entre 1 y 1000")
        
        bloqueos = db.query(Bloqueo).offset(skip).limit(limit).all()
        
        logger.info(f"Se obtuvieron {len(bloqueos)} bloqueos")
        return bloqueos
        
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos al obtener bloqueos: {str(e)}")
        raise DatabaseError(f"Error al obtener bloqueos: {str(e)}")
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al obtener bloqueos: {str(e)}")
        raise DatabaseError(f"Error inesperado al obtener bloqueos: {str(e)}")


@log_function_call
@log_execution_time
def create_bloqueo(db: Session, bloqueo: BloqueoCreate):
    """
    Crea un nuevo bloqueo.
    
    Args:
        db: Sesión de base de datos
        bloqueo: Datos del bloqueo a crear
        
    Returns:
        Bloqueo creado
        
    Raises:
        EstudianteNotFoundError: Si no existe el estudiante
        DatabaseError: Si ocurre un error de base de datos
        ValidationError: Si los datos del bloqueo son inválidos
    """
    try:
        logger.info(f"Creando nuevo bloqueo para estudiante: {bloqueo.registro_academico}")
        
        # Verificar que el estudiante existe
        estudiante = db.query(Estudiante).filter(Estudiante.registro_academico == bloqueo.registro_academico).first()
        if not estudiante:
            logger.warning(f"No se encontró estudiante: {bloqueo.registro_academico}")
            raise EstudianteNotFoundError(registro_academico=bloqueo.registro_academico)
        
        # Crear bloqueo
        bloqueo_data = bloqueo.dict()
        bloqueo_data["codigo_bloqueo"] = generate_codigo_bloqueo(db)
        
        db_bloqueo = Bloqueo(**bloqueo_data)
        db.add(db_bloqueo)
        db.commit()
        db.refresh(db_bloqueo)
        
        logger.info(f"Bloqueo creado exitosamente: {db_bloqueo.codigo_bloqueo}")
        return db_bloqueo
        
    except EstudianteNotFoundError:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al crear bloqueo: {str(e)}")
        raise DatabaseError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de base de datos al crear bloqueo: {str(e)}")
        raise DatabaseError(f"Error al crear bloqueo: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al crear bloqueo: {str(e)}")
        raise DatabaseError(f"Error inesperado al crear bloqueo: {str(e)}")


@log_function_call
@log_execution_time
def update_bloqueo(db: Session, codigo_bloqueo: str, bloqueo_update: BloqueoUpdate):
    """
    Actualiza un bloqueo existente.
    
    Args:
        db: Sesión de base de datos
        codigo_bloqueo: Código del bloqueo a actualizar
        bloqueo_update: Datos a actualizar
        
    Returns:
        Bloqueo actualizado
        
    Raises:
        BloqueoNotFoundError: Si no se encuentra el bloqueo
        DatabaseError: Si ocurre un error de base de datos
    """
    try:
        logger.info(f"Actualizando bloqueo con código: {codigo_bloqueo}")
        
        db_bloqueo = db.query(Bloqueo).filter(Bloqueo.codigo_bloqueo == codigo_bloqueo).first()
        if not db_bloqueo:
            logger.warning(f"No se encontró bloqueo para actualizar: {codigo_bloqueo}")
            raise BloqueoNotFoundError(bloqueo_id=None)
        
        update_data = bloqueo_update.dict(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(db_bloqueo, field, value)
        
        db.commit()
        db.refresh(db_bloqueo)
        
        logger.info(f"Bloqueo actualizado exitosamente: {codigo_bloqueo}")
        return db_bloqueo
        
    except BloqueoNotFoundError:
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al actualizar bloqueo: {str(e)}")
        raise DatabaseError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de base de datos al actualizar bloqueo: {str(e)}")
        raise DatabaseError(f"Error al actualizar bloqueo: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al actualizar bloqueo: {str(e)}")
        raise DatabaseError(f"Error inesperado al actualizar bloqueo: {str(e)}")