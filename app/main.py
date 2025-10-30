from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.requests import Request
from fastapi.exceptions import RequestValidationError
from app.routers import auth, estudiantes, pagos, bloqueos
from app.database import engine, Base
from app.middleware import (
    configure_middleware,
    validation_exception_handler,
    http_exception_handler
)
from app.config.logging import get_logger
import logging

# Import all models to ensure they are registered with SQLAlchemy
from app.models import estudiante, pago, bloqueo

# Configurar logging antes de hacer cualquier cosa
logger = get_logger(__name__)

# Crear las tablas en la base de datos (solo las que no existen)
try:
    logger.info("Creando tablas de base de datos...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tablas de base de datos creadas exitosamente")
except Exception as e:
    logger.error(f"Error al crear tablas de base de datos: {str(e)}", exc_info=True)
    raise

app = FastAPI(
    title="Microservicio Estudiantil",
    description="API para gestión de estudiantes, pagos y bloqueos",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar manejadores de excepciones personalizados
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)

# Configurar middleware (incluyendo manejo de excepciones y logging)
configure_middleware(app)

logger.info("Aplicación FastAPI inicializada")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # En producción, especificar dominios específicos
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS configurado")

# Incluir routers
app.include_router(auth.router)
app.include_router(estudiantes.router)
app.include_router(pagos.router)
app.include_router(bloqueos.router)

logger.info("Routers incluidos exitosamente")

@app.get("/")
def read_root():
    """
    Endpoint raíz para verificar que la API está funcionando.
    
    Returns:
        Mensaje de confirmación
    """
    logger.info("Acceso al endpoint raíz")
    return {"message": "Microservicio Estudiantil - API funcionando correctamente"}


@app.get("/health")
def health_check():
    """
    Endpoint de health check para monitoreo.
    
    Returns:
        Estado de salud del servicio
    """
    logger.debug("Health check ejecutado")
    return {
        "status": "healthy", 
        "service": "microservicio_estudiantil",
        "version": "1.0.0"
    }


@app.on_event("startup")
async def startup_event():
    """
    Evento que se ejecuta al iniciar la aplicación.
    """
    logger.info("=== MICROSERVICIO ESTUDIANTIL INICIADO ===")
    logger.info("Versión: 1.0.0")
    logger.info("Configuración de logging: ACTIVA")
    logger.info("Middleware de excepciones: ACTIVO")
    logger.info("Sistema de trazabilidad: ACTIVO")
    logger.info("==========================================")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Evento que se ejecuta al cerrar la aplicación.
    """
    logger.info("=== MICROSERVICIO ESTUDIANTIL DETENIDO ===")
    logger.info("Cerrando conexiones y limpiando recursos...")
    logger.info("===========================================")