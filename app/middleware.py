"""
Middleware para manejo de excepciones globales y logging de requests.
"""

import time
import uuid
from typing import Callable
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from app.exceptions import BaseCustomException, map_exception_to_http
from app.config.logging import get_logger

logger = get_logger(__name__)


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """
    Middleware para manejo global de excepciones.
    
    Captura todas las excepciones no manejadas y las convierte en respuestas HTTP apropiadas.
    También maneja el logging de excepciones con información contextual.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        try:
            response = await call_next(request)
            return response
            
        except BaseCustomException as e:
            # Excepciones personalizadas de la aplicación
            logger.warning(
                f"Excepción personalizada capturada: {e.__class__.__name__}: {e.message}",
                extra={
                    "error_code": e.error_code,
                    "details": e.details,
                    "path": request.url.path,
                    "method": request.method,
                    "client_ip": request.client.host if request.client else "unknown"
                }
            )
            
            http_exception = map_exception_to_http(e)
            return JSONResponse(
                status_code=http_exception.status_code,
                content=http_exception.detail
            )
            
        except HTTPException as e:
            # Excepciones HTTP de FastAPI
            logger.warning(
                f"HTTPException capturada: {e.status_code}: {e.detail}",
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "client_ip": request.client.host if request.client else "unknown"
                }
            )
            raise e
            
        except Exception as e:
            # Excepciones no controladas
            logger.error(
                f"Excepción no controlada: {e.__class__.__name__}: {str(e)}",
                exc_info=True,
                extra={
                    "path": request.url.path,
                    "method": request.method,
                    "client_ip": request.client.host if request.client else "unknown"
                }
            )
            
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "message": "Error interno del servidor",
                    "error_code": "INTERNAL_SERVER_ERROR",
                    "details": {}
                }
            )


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logging de requests HTTP.
    
    Registra información de cada request incluyendo:
    - URL, método, headers relevantes
    - Tiempo de procesamiento
    - Código de respuesta
    - ID único de request para trazabilidad
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generar ID único para el request
        request_id = str(uuid.uuid4())[:8]
        start_time = time.time()
        
        # Obtener información del request
        client_ip = request.client.host if request.client else "unknown"
        user_agent = request.headers.get("user-agent", "unknown")
        
        # Log del inicio del request
        logger.info(
            f"Request iniciado: {request.method} {request.url.path}",
            extra={
                "request_id": request_id,
                "client_ip": client_ip,
                "user_agent": user_agent,
                "query_params": dict(request.query_params),
            }
        )
        
        try:
            # Procesar request
            response = await call_next(request)
            
            # Calcular tiempo de procesamiento
            process_time = time.time() - start_time
            
            # Log del final del request
            logger.info(
                f"Request completado: {request.method} {request.url.path} - "
                f"Status: {response.status_code} - Tiempo: {process_time:.4f}s",
                extra={
                    "request_id": request_id,
                    "status_code": response.status_code,
                    "process_time": process_time,
                    "client_ip": client_ip,
                }
            )
            
            # Agregar headers de respuesta para debugging
            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time"] = f"{process_time:.4f}"
            
            return response
            
        except Exception as e:
            # Log de errores durante el procesamiento
            process_time = time.time() - start_time
            
            logger.error(
                f"Request falló: {request.method} {request.url.path} - "
                f"Error: {e.__class__.__name__}: {str(e)} - Tiempo: {process_time:.4f}s",
                exc_info=True,
                extra={
                    "request_id": request_id,
                    "process_time": process_time,
                    "client_ip": client_ip,
                    "error_type": e.__class__.__name__,
                }
            )
            
            # Re-lanzar la excepción para que sea manejada por el ExceptionHandlerMiddleware
            raise


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware para agregar headers de seguridad a las respuestas.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)
        
        # Headers de seguridad básicos
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Content Security Policy para permitir Swagger UI
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data: https:; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self';"
        )
        
        return response


class DatabaseConnectionMiddleware(BaseHTTPMiddleware):
    """
    Middleware para logging de conexiones de base de datos.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Solo loggear para endpoints que modifican datos
        if request.method in ["POST", "PUT", "DELETE", "PATCH"]:
            logger.debug(
                f"Operación de base de datos: {request.method} {request.url.path}",
                extra={
                    "operation_type": "database",
                    "method": request.method,
                    "path": request.url.path
                }
            )
        
        return await call_next(request)


def configure_middleware(app):
    """
    Configura todos los middlewares de la aplicación.
    
    Args:
        app: Instancia de FastAPI
    """
    # Agregar middlewares en orden inverso de ejecución
    # (el último agregado es el primero en ejecutarse)
    
    # Middleware de headers de seguridad (se ejecuta al final)
    app.add_middleware(SecurityHeadersMiddleware)
    
    # Middleware de conexiones de base de datos
    app.add_middleware(DatabaseConnectionMiddleware)
    
    # Middleware de manejo de excepciones (se ejecuta antes del logging para capturar errores)
    app.add_middleware(ExceptionHandlerMiddleware)
    
    # Middleware de logging de requests (se ejecuta primero)
    app.add_middleware(RequestLoggingMiddleware)
    
    logger.info("Middlewares configurados exitosamente")


# Manejadores de excepciones adicionales para FastAPI
async def validation_exception_handler(request: Request, exc: Exception):
    """
    Manejador específico para errores de validación de FastAPI.
    """
    logger.warning(
        f"Error de validación: {str(exc)}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "client_ip": request.client.host if request.client else "unknown"
        }
    )
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "message": "Error de validación en los datos proporcionados",
            "error_code": "VALIDATION_ERROR",
            "details": {"validation_errors": str(exc)}
        }
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    Manejador específico para HTTPExceptions.
    """
    logger.warning(
        f"HTTP Exception: {exc.status_code}: {exc.detail}",
        extra={
            "path": request.url.path,
            "method": request.method,
            "status_code": exc.status_code,
            "client_ip": request.client.host if request.client else "unknown"
        }
    )
    
    # Si el detail ya es un diccionario (como nuestras excepciones personalizadas), devolverlo tal como está
    if isinstance(exc.detail, dict):
        return JSONResponse(status_code=exc.status_code, content=exc.detail)
    
    # Si el detail es un string, envolverlo en nuestro formato estándar
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "message": exc.detail,
            "error_code": f"HTTP_{exc.status_code}",
            "details": {}
        }
    )