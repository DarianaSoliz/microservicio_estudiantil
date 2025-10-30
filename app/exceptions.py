"""
Excepciones personalizadas para el microservicio estudiantil.
"""

from typing import Any, Dict, Optional
from fastapi import HTTPException, status


class BaseCustomException(Exception):
    """Excepción base personalizada para el microservicio estudiantil."""
    
    def __init__(
        self,
        message: str,
        error_code: str = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(BaseCustomException):
    """Excepción para errores de validación de datos."""
    pass


class NotFoundError(BaseCustomException):
    """Excepción para recursos no encontrados."""
    pass


class ConflictError(BaseCustomException):
    """Excepción para conflictos de recursos (duplicados, etc.)."""
    pass


class AuthenticationError(BaseCustomException):
    """Excepción para errores de autenticación."""
    pass


class AuthorizationError(BaseCustomException):
    """Excepción para errores de autorización."""
    pass


class DatabaseError(BaseCustomException):
    """Excepción para errores de base de datos."""
    pass


# Excepciones específicas del dominio

class EstudianteNotFoundError(NotFoundError):
    """Excepción cuando no se encuentra un estudiante."""
    
    def __init__(self, registro_academico: str = None, ci: str = None):
        if registro_academico:
            message = f"Estudiante con registro académico {registro_academico} no encontrado"
            details = {"registro_academico": registro_academico}
        elif ci:
            message = f"Estudiante con CI {ci} no encontrado"
            details = {"ci": ci}
        else:
            message = "Estudiante no encontrado"
            details = {}
        
        super().__init__(
            message=message,
            error_code="ESTUDIANTE_NOT_FOUND",
            details=details
        )


class EstudianteAlreadyExistsError(ConflictError):
    """Excepción cuando un estudiante ya existe."""
    
    def __init__(self, field: str, value: str):
        message = f"Ya existe un estudiante con {field}: {value}"
        super().__init__(
            message=message,
            error_code="ESTUDIANTE_ALREADY_EXISTS",
            details={field: value}
        )


class PagoNotFoundError(NotFoundError):
    """Excepción cuando no se encuentra un pago."""
    
    def __init__(self, pago_id: int = None):
        if pago_id:
            message = f"Pago con ID {pago_id} no encontrado"
            details = {"pago_id": pago_id}
        else:
            message = "Pago no encontrado"
            details = {}
        
        super().__init__(
            message=message,
            error_code="PAGO_NOT_FOUND",
            details=details
        )


class PagoAlreadyExistsError(ConflictError):
    """Excepción cuando un pago ya existe."""
    
    def __init__(self, details: Dict[str, Any]):
        message = "Ya existe un pago con los datos proporcionados"
        super().__init__(
            message=message,
            error_code="PAGO_ALREADY_EXISTS",
            details=details
        )


class BloqueoNotFoundError(NotFoundError):
    """Excepción cuando no se encuentra un bloqueo."""
    
    def __init__(self, bloqueo_id: int = None):
        if bloqueo_id:
            message = f"Bloqueo con ID {bloqueo_id} no encontrado"
            details = {"bloqueo_id": bloqueo_id}
        else:
            message = "Bloqueo no encontrado"
            details = {}
        
        super().__init__(
            message=message,
            error_code="BLOQUEO_NOT_FOUND",
            details=details
        )


class InsufficientPermissionsError(AuthorizationError):
    """Excepción para permisos insuficientes."""
    
    def __init__(self, required_action: str):
        message = f"Permisos insuficientes para realizar la acción: {required_action}"
        super().__init__(
            message=message,
            error_code="INSUFFICIENT_PERMISSIONS",
            details={"required_action": required_action}
        )


class InvalidCredentialsError(AuthenticationError):
    """Excepción para credenciales inválidas."""
    
    def __init__(self):
        message = "Credenciales inválidas"
        super().__init__(
            message=message,
            error_code="INVALID_CREDENTIALS"
        )


class TokenExpiredError(AuthenticationError):
    """Excepción para token expirado."""
    
    def __init__(self):
        message = "Token de acceso expirado"
        super().__init__(
            message=message,
            error_code="TOKEN_EXPIRED"
        )


class InvalidTokenError(AuthenticationError):
    """Excepción para token inválido."""
    
    def __init__(self):
        message = "Token de acceso inválido"
        super().__init__(
            message=message,
            error_code="INVALID_TOKEN"
        )


def map_exception_to_http(exception: BaseCustomException) -> HTTPException:
    """
    Mapea excepciones personalizadas a HTTPException de FastAPI.
    
    Args:
        exception: La excepción personalizada a mapear
        
    Returns:
        HTTPException: La excepción HTTP correspondiente
    """
    status_code_mapping = {
        ValidationError: status.HTTP_400_BAD_REQUEST,
        NotFoundError: status.HTTP_404_NOT_FOUND,
        ConflictError: status.HTTP_409_CONFLICT,
        AuthenticationError: status.HTTP_401_UNAUTHORIZED,
        AuthorizationError: status.HTTP_403_FORBIDDEN,
        DatabaseError: status.HTTP_500_INTERNAL_SERVER_ERROR,
        
        # Excepciones específicas del dominio
        EstudianteNotFoundError: status.HTTP_404_NOT_FOUND,
        EstudianteAlreadyExistsError: status.HTTP_409_CONFLICT,
        PagoNotFoundError: status.HTTP_404_NOT_FOUND,
        PagoAlreadyExistsError: status.HTTP_409_CONFLICT,
        BloqueoNotFoundError: status.HTTP_404_NOT_FOUND,
        InsufficientPermissionsError: status.HTTP_403_FORBIDDEN,
        InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
        TokenExpiredError: status.HTTP_401_UNAUTHORIZED,
        InvalidTokenError: status.HTTP_401_UNAUTHORIZED,
    }
    
    status_code = status_code_mapping.get(type(exception), status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    detail = {
        "message": exception.message,
        "error_code": exception.error_code,
        "details": exception.details
    }
    
    return HTTPException(status_code=status_code, detail=detail)