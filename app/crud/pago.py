from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from app.models.pago import Pago
from app.models.estudiante import Estudiante
from app.schemas.pago import PagoCreate
from app.exceptions import (
    PagoNotFoundError,
    EstudianteNotFoundError,
    DatabaseError,
    ValidationError
)
from app.config.logging import get_logger, log_function_call, log_execution_time

logger = get_logger(__name__)

@log_function_call
@log_execution_time
def generate_codigo_pago(db: Session):
    """
    Genera un código único para el pago.
    
    Args:
        db: Sesión de base de datos
        
    Returns:
        Código de pago generado
        
    Raises:
        DatabaseError: Si ocurre un error de base de datos
    """
    try:
        logger.debug("Generando nuevo código de pago")
        
        last_pago = db.query(Pago).order_by(Pago.codigo_pago.desc()).first()
        if last_pago:
            last_number = int(last_pago.codigo_pago[1:])  # Quitar la 'P' del inicio
            new_number = last_number + 1
        else:
            new_number = 1
        
        codigo = f"P{new_number:05d}"
        logger.debug(f"Código de pago generado: {codigo}")
        return codigo
        
    except ValueError as e:
        logger.error(f"Error al procesar código de pago: {str(e)}")
        raise DatabaseError(f"Error al generar código de pago: {str(e)}")
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos al generar código de pago: {str(e)}")
        raise DatabaseError(f"Error al generar código de pago: {str(e)}")
    except Exception as e:
        logger.error(f"Error inesperado al generar código de pago: {str(e)}")
        raise DatabaseError(f"Error inesperado al generar código de pago: {str(e)}")

@log_function_call
@log_execution_time
def get_pago(db: Session, codigo_pago: str):
    """
    Obtiene un pago por su código.
    
    Args:
        db: Sesión de base de datos
        codigo_pago: Código del pago
        
    Returns:
        Pago encontrado o None
        
    Raises:
        DatabaseError: Si ocurre un error de base de datos
        ValidationError: Si el código de pago es inválido
    """
    try:
        logger.info(f"Buscando pago con código: {codigo_pago}")
        
        if not codigo_pago or not codigo_pago.strip():
            logger.warning("Se proporcionó un código de pago vacío o nulo")
            raise ValidationError("El código de pago es requerido")
        
        pago = db.query(Pago).filter(Pago.codigo_pago == codigo_pago).first()
        
        if pago:
            logger.info(f"Pago encontrado: {codigo_pago}")
        else:
            logger.info(f"No se encontró pago con código: {codigo_pago}")
            
        return pago
        
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos al buscar pago {codigo_pago}: {str(e)}")
        raise DatabaseError(f"Error al buscar pago: {str(e)}")
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al buscar pago {codigo_pago}: {str(e)}")
        raise DatabaseError(f"Error inesperado al buscar pago: {str(e)}")

@log_function_call
@log_execution_time
def get_pagos_by_estudiante(db: Session, registro_academico: str):
    """
    Obtiene todos los pagos de un estudiante.
    
    Args:
        db: Sesión de base de datos
        registro_academico: Registro académico del estudiante
        
    Returns:
        Lista de pagos del estudiante
        
    Raises:
        DatabaseError: Si ocurre un error de base de datos
        ValidationError: Si el registro académico es inválido
    """
    try:
        logger.info(f"Obteniendo pagos del estudiante: {registro_academico}")
        
        if not registro_academico or not registro_academico.strip():
            logger.warning("Se proporcionó un registro académico vacío o nulo")
            raise ValidationError("El registro académico es requerido")
        
        pagos = db.query(Pago).filter(Pago.registro_academico == registro_academico).all()
        
        logger.info(f"Se encontraron {len(pagos)} pagos para el estudiante {registro_academico}")
        return pagos
        
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos al obtener pagos del estudiante {registro_academico}: {str(e)}")
        raise DatabaseError(f"Error al obtener pagos del estudiante: {str(e)}")
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al obtener pagos del estudiante {registro_academico}: {str(e)}")
        raise DatabaseError(f"Error inesperado al obtener pagos del estudiante: {str(e)}")

@log_function_call
@log_execution_time
def get_pagos(db: Session, skip: int = 0, limit: int = 100):
    """
    Obtiene una lista paginada de pagos.
    
    Args:
        db: Sesión de base de datos
        skip: Número de registros a omitir
        limit: Máximo número de registros a retornar
        
    Returns:
        Lista de pagos
        
    Raises:
        DatabaseError: Si ocurre un error de base de datos
        ValidationError: Si los parámetros de paginación son inválidos
    """
    try:
        logger.info(f"Obteniendo pagos con skip={skip}, limit={limit}")
        
        if skip < 0:
            logger.warning(f"Valor de skip inválido: {skip}")
            raise ValidationError("El valor de skip debe ser mayor o igual a 0")
            
        if limit < 1 or limit > 1000:
            logger.warning(f"Valor de limit inválido: {limit}")
            raise ValidationError("El valor de limit debe estar entre 1 y 1000")
        
        pagos = db.query(Pago).offset(skip).limit(limit).all()
        
        logger.info(f"Se obtuvieron {len(pagos)} pagos")
        return pagos
        
    except SQLAlchemyError as e:
        logger.error(f"Error de base de datos al obtener pagos: {str(e)}")
        raise DatabaseError(f"Error al obtener pagos: {str(e)}")
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Error inesperado al obtener pagos: {str(e)}")
        raise DatabaseError(f"Error inesperado al obtener pagos: {str(e)}")

@log_function_call
@log_execution_time
def create_pago(db: Session, pago: PagoCreate):
    """
    Crea un nuevo pago.
    
    Args:
        db: Sesión de base de datos
        pago: Datos del pago a crear
        
    Returns:
        Pago creado
        
    Raises:
        EstudianteNotFoundError: Si no existe el estudiante
        DatabaseError: Si ocurre un error de base de datos
        ValidationError: Si los datos del pago son inválidos
    """
    try:
        logger.info(f"Creando nuevo pago para estudiante: {pago.registro_academico}")
        
        # Verificar que el estudiante existe
        estudiante = db.query(Estudiante).filter(Estudiante.registro_academico == pago.registro_academico).first()
        if not estudiante:
            logger.warning(f"No se encontró estudiante: {pago.registro_academico}")
            raise EstudianteNotFoundError(registro_academico=pago.registro_academico)
        
        # Crear pago
        pago_data = pago.dict()
        pago_data["codigo_pago"] = generate_codigo_pago(db)
        
        db_pago = Pago(**pago_data)
        db.add(db_pago)
        db.commit()
        db.refresh(db_pago)
        
        logger.info(f"Pago creado exitosamente: {db_pago.codigo_pago}")
        return db_pago
        
    except EstudianteNotFoundError:
        db.rollback()
        raise
    except IntegrityError as e:
        db.rollback()
        logger.error(f"Error de integridad al crear pago: {str(e)}")
        raise DatabaseError(f"Error de integridad: {str(e)}")
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de base de datos al crear pago: {str(e)}")
        raise DatabaseError(f"Error al crear pago: {str(e)}")
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado al crear pago: {str(e)}")
        raise DatabaseError(f"Error inesperado al crear pago: {str(e)}")