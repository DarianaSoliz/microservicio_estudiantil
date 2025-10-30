# 🎓 Microservicio Estudiantil - Sistema Mejorado

## 📋 Descripción del Proyecto

El **Microservicio Estudiantil** es una API REST desarrollada con FastAPI que gestiona información de estudiantes, pagos y bloqueos académicos. Este proyecto ha sido completamente mejorado con un sistema robusto de **excepciones personalizadas**, **logging comprehensivo**, **middleware avanzado** y **seguridad mejorada**.

## 🚀 Nuevas Características y Mejoras Implementadas

### 1. 🛠️ Sistema de Excepciones Personalizadas

#### 📍 Ubicación: `app/exceptions.py`

Hemos implementado un sistema jerárquico de excepciones que proporciona:

**🔹 Excepciones Base:**
- `BaseCustomException`: Clase base para todas las excepciones personalizadas
- `ValidationError`: Errores de validación de datos de entrada
- `NotFoundError`: Recursos no encontrados en la base de datos
- `ConflictError`: Conflictos de recursos (duplicados, violaciones de unicidad)
- `AuthenticationError`: Errores de autenticación (credenciales inválidas)
- `AuthorizationError`: Errores de autorización (permisos insuficientes)
- `DatabaseError`: Errores relacionados con operaciones de base de datos

**🔹 Excepciones Específicas del Dominio:**
```python
# Estudiantes
EstudianteNotFoundError(registro_academico="202312345")
EstudianteAlreadyExistsError(field="ci", value="12345678")

# Pagos
PagoNotFoundError(pago_id=123)
PagoAlreadyExistsError(details={"estudiante": "202312345"})

# Bloqueos
BloqueoNotFoundError(bloqueo_id=456)

# Carreras
CarreraNotFoundError(carrera_id=1, codigo="ING-SIS")
CarreraAlreadyExistsError(codigo="ING-SIS")

# Autenticación y Autorización
InvalidCredentialsError()
TokenExpiredError()
InsufficientPermissionsError(required_action="actualizar estudiante")
```

**🔹 Mapeo Automático a HTTP:**
```python
def map_exception_to_http(exception: BaseCustomException) -> HTTPException:
    # Convierte automáticamente excepciones personalizadas a códigos HTTP apropiados
    # - 400: ValidationError
    # - 401: AuthenticationError
    # - 403: AuthorizationError
    # - 404: NotFoundError
    # - 409: ConflictError
    # - 500: DatabaseError
```

### 2. 📊 Sistema de Logging Centralizado

#### 📍 Ubicación: `app/config/logging.py`

**🔹 Características del Sistema:**

1. **Configuración por Variables de Entorno:**
   ```bash
   LOG_LEVEL=INFO          # DEBUG, INFO, WARNING, ERROR, CRITICAL
   LOG_DIR=logs           # Directorio de archivos de log
   LOG_CONSOLE=true       # Mostrar logs en consola con colores
   LOG_FILE=true          # Guardar logs en archivos rotativos
   ```

2. **Múltiples Formatters:**
   - **ColoredFormatter**: Consola con colores para mejor legibilidad
   - **RequestFormatter**: Requests HTTP con ID único y información del usuario
   - **DetailedFormatter**: Archivos con información completa de debugging

3. **Archivos de Log Especializados:**
   ```
   logs/
   ├── app.log           # Log general de toda la aplicación
   ├── errors.log        # Solo errores y excepciones críticas
   ├── requests.log      # Requests HTTP con trazabilidad completa
   └── database.log      # Operaciones específicas de base de datos
   ```

4. **Rotación Automática:**
   - Archivos de máximo 10MB
   - Hasta 5 backups por tipo de log
   - Compresión automática de archivos antiguos

5. **Decoradores de Utilidad:**
   ```python
   @log_function_call     # Loggea entrada y salida de funciones
   @log_execution_time    # Mide y loggea tiempo de ejecución
   ```

**🔹 Ejemplo de Output de Logs:**
```
2024-10-28 10:30:15 [abc12345] [User:202312345] - app.routers.estudiantes - INFO - Creando estudiante: 202312346
2024-10-28 10:30:15 [abc12345] - app.crud.estudiante - INFO - Buscando estudiante con registro académico: 202312346
2024-10-28 10:30:15 [abc12345] - app.crud.estudiante - INFO - Estudiante creado exitosamente: 202312346
2024-10-28 10:30:15 [abc12345] - app.middleware - INFO - Request completado: POST /estudiantes - Status: 201 - Tiempo: 0.0234s
```

### 3. 🔧 Middleware Avanzado

#### 📍 Ubicación: `app/middleware.py`

**🔹 ExceptionHandlerMiddleware:**
- Captura **todas** las excepciones no manejadas
- Convierte excepciones personalizadas a respuestas HTTP apropiadas
- Loggea excepciones con información contextual completa
- Previene exposición de información sensible en errores

**🔹 RequestLoggingMiddleware:**
- Genera **ID único** para cada request (trazabilidad completa)
- Loggea información detallada: IP, User-Agent, parámetros, tiempo de procesamiento
- Agrega headers de debugging: `X-Request-ID`, `X-Process-Time`
- Mide performance de endpoints automáticamente

**🔹 SecurityHeadersMiddleware:**
- **Content Security Policy** configurado para Swagger UI
- Headers de seguridad automáticos:
  ```
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  X-XSS-Protection: 1; mode=block
  Referrer-Policy: strict-origin-when-cross-origin
  ```
- Protección contra ataques XSS, clickjacking y MIME sniffing

**🔹 DatabaseConnectionMiddleware:**
- Logging específico para operaciones que modifican datos
- Monitoreo de performance de queries
- Detección de operaciones costosas

### 4. 💾 Mejoras en Módulos CRUD

#### 📍 Archivos Actualizados:
- `app/crud/estudiante.py`
- `app/crud/pago.py`
- `app/crud/bloqueo.py`
- `app/crud/carrera.py` (creado completamente)

**🔹 Funcionalidades Mejoradas:**

1. **Manejo Robusto de Errores:**
   ```python
   try:
       # Operación de base de datos
       estudiante = create_estudiante(db, estudiante_data)
       logger.info(f"Estudiante creado: {estudiante.registro_academico}")
       return estudiante
   except IntegrityError as e:
       db.rollback()
       if "registro_academico" in str(e):
           raise EstudianteAlreadyExistsError("registro_academico", estudiante.registro_academico)
   except SQLAlchemyError as e:
       db.rollback()
       raise DatabaseError(f"Error de base de datos: {str(e)}")
   ```

2. **Validaciones Exhaustivas:**
   - Validación de parámetros de entrada
   - Verificación de integridad referencial
   - Validación de rangos de paginación
   - Verificación de permisos de operación

3. **Logging Detallado:**
   - Cada operación CRUD es loggeada
   - Información de performance y tiempo de ejecución
   - Contexto completo en caso de errores

4. **Transacciones Seguras:**
   - Rollback automático en caso de errores
   - Manejo de deadlocks y timeouts
   - Verificación de consistencia de datos

### 5. 🌐 Mejoras en Routers

#### 📍 Archivos Actualizados:
- `app/routers/estudiantes.py`
- `app/routers/auth.py`
- `app/routers/pagos.py`
- `app/routers/bloqueos.py`

**🔹 Funcionalidades Mejoradas:**

1. **Manejo de Excepciones Unificado:**
   ```python
   try:
       result = crud_operation(db, data)
       logger.info(f"Operación exitosa: {operation_name}")
       return result
   except BaseCustomException as e:
       logger.warning(f"Error controlado: {e.message}")
       raise map_exception_to_http(e)
   except Exception as e:
       logger.error(f"Error inesperado: {str(e)}", exc_info=True)
       raise HTTPException(status_code=500, detail="Error interno del servidor")
   ```

2. **Documentación Mejorada:**
   - Docstrings detallados para todos los endpoints
   - Ejemplos de uso en la documentación
   - Descripción de códigos de error posibles

3. **Respuestas Consistentes:**
   ```json
   {
     "message": "Descripción del error",
     "error_code": "ESTUDIANTE_NOT_FOUND",
     "details": {
       "registro_academico": "202312345"
     }
   }
   ```

### 6. ⚙️ Configuración Principal Mejorada

#### 📍 Archivo: `app/main.py`

**🔹 Mejoras Implementadas:**

1. **Inicialización con Logging:**
   ```python
   logger.info("=== MICROSERVICIO ESTUDIANTIL INICIADO ===")
   logger.info("Configuración de logging: ACTIVA")
   logger.info("Middleware de excepciones: ACTIVO")
   logger.info("Sistema de trazabilidad: ACTIVO")
   ```

2. **Configuración Automática:**
   - Middleware configurado automáticamente
   - Manejadores de excepciones globales
   - Eventos de startup y shutdown con logging

3. **Monitoreo de Salud:**
   ```python
   @app.get("/health")
   def health_check():
       return {
           "status": "healthy", 
           "service": "microservicio_estudiantil",
           "version": "1.0.0"
       }
   ```

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                      │
├─────────────────────────────────────────────────────────────┤
│  SecurityHeadersMiddleware (Headers de seguridad)          │
├─────────────────────────────────────────────────────────────┤
│  DatabaseConnectionMiddleware (Logging de BD)              │
├─────────────────────────────────────────────────────────────┤
│  ExceptionHandlerMiddleware (Manejo global de errores)     │
├─────────────────────────────────────────────────────────────┤
│  RequestLoggingMiddleware (Logging de requests)            │
├─────────────────────────────────────────────────────────────┤
│                      Routers                               │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │    Auth     │ Estudiantes │    Pagos    │  Bloqueos   │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                      CRUD Layer                            │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │ Estudiante  │    Pago     │   Bloqueo   │   Carrera   │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                   Exception System                         │
│  ┌─────────────────┬─────────────────┬─────────────────┐    │
│  │ Custom Exceptions│  Error Mapping  │  HTTP Responses │    │
│  └─────────────────┴─────────────────┴─────────────────┘    │
├─────────────────────────────────────────────────────────────┤
│                   Logging System                           │
│  ┌─────────────┬─────────────┬─────────────┬─────────────┐  │
│  │   Console   │   App Log   │ Error Log   │Request Log  │  │
│  └─────────────┴─────────────┴─────────────┴─────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    Database Layer                          │
│  ┌─────────────────────────────────────────────────────┐    │
│  │              PostgreSQL Database                    │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Instalación y Configuración

### 1. **Prerrequisitos**
```bash
- Docker y Docker Compose
- Python 3.8+ (para desarrollo local)
- PostgreSQL (incluido en Docker)
```

### 2. **Configuración del Entorno**

1. **Clonar el repositorio:**
   ```bash
   git clone <repository-url>
   cd microservicio_estudiantil
   ```

2. **Configurar variables de entorno:**
   ```bash
   cp .env.example .env
   # Editar .env con tu configuración
   ```

3. **Variables de entorno importantes:**
   ```bash
   # Base de datos
   DATABASE_URL=postgresql://postgres:postgres@postgres:5432/postgres
   
   # Logging
   LOG_LEVEL=INFO
   LOG_DIR=logs
   LOG_CONSOLE=true
   LOG_FILE=true
   
   # Seguridad
   SECRET_KEY=your-secret-key-here-change-in-production
   ACCESS_TOKEN_EXPIRE_MINUTES=300
   
   # Aplicación
   HOST=0.0.0.0
   PORT=8000
   DEBUG=false
   ```

### 3. **Ejecución con Docker**
```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs en tiempo real
docker-compose logs -f app

# Reiniciar solo la aplicación
docker-compose restart app

# Parar todos los servicios
docker-compose down
```

### 4. **Ejecución Local (Desarrollo)**
```bash
# Instalar dependencias
pip install -r requirements.txt

# Configurar base de datos local
export DATABASE_URL="postgresql://usuario:password@localhost/microservicio_estudiantil"

# Ejecutar aplicación
uvicorn app.main:app --reload --log-level info
```

## 📚 Uso de la API

### **Endpoints Disponibles:**

#### 🔐 **Autenticación**
```bash
POST /auth/login-estudiante    # Login con registro académico
POST /auth/login              # Login con OAuth2 form
GET  /auth/me                 # Información del usuario autenticado
```

#### 👨‍🎓 **Estudiantes**
```bash
POST   /estudiantes/          # Crear estudiante
GET    /estudiantes/me        # Obtener información propia
GET    /estudiantes/{id}      # Obtener estudiante por ID
GET    /estudiantes/          # Listar estudiantes (paginado)
PUT    /estudiantes/{id}      # Actualizar estudiante
DELETE /estudiantes/{id}      # Eliminar estudiante
```

#### 💰 **Pagos**
```bash
POST /pagos/                  # Crear pago
GET  /pagos/{codigo}          # Obtener pago por código
GET  /pagos/                  # Listar pagos (paginado)
GET  /pagos/estudiante/{id}   # Pagos de un estudiante
```

#### 🚫 **Bloqueos**
```bash
POST /bloqueos/               # Crear bloqueo
GET  /bloqueos/{codigo}       # Obtener bloqueo por código
GET  /bloqueos/               # Listar bloqueos (paginado)
PUT  /bloqueos/{codigo}       # Actualizar bloqueo
GET  /bloqueos/estudiante/{id} # Bloqueos de un estudiante
```

#### 🎓 **Carreras**
```bash
POST   /carreras/             # Crear carrera
GET    /carreras/{id}         # Obtener carrera por ID
GET    /carreras/             # Listar carreras (paginado)
PUT    /carreras/{id}         # Actualizar carrera
DELETE /carreras/{id}         # Eliminar carrera
```

### **Documentación Interactiva:**
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc
- **Health Check:** http://localhost:8000/health

## 🔍 Monitoreo y Debugging

### **Logs en Tiempo Real:**
```bash
# Log general de la aplicación
tail -f logs/app.log

# Solo errores críticos
tail -f logs/errors.log

# Requests HTTP con trazabilidad
tail -f logs/requests.log

# Operaciones de base de datos
tail -f logs/database.log

# Logs de Docker
docker-compose logs -f app
```

### **Headers de Debugging:**
Cada response incluye headers útiles para debugging:
```
X-Request-ID: abc12345        # ID único del request
X-Process-Time: 0.0234        # Tiempo de procesamiento en segundos
```

### **Ejemplo de Trazabilidad:**
```bash
# Buscar todos los logs de un request específico
grep "abc12345" logs/app.log

# Buscar operaciones de un estudiante específico
grep "202312345" logs/app.log

# Buscar errores de los últimos 10 minutos
grep "ERROR" logs/errors.log | tail -20
```

## 🧪 Testing y Validación

### **Casos de Prueba Recomendados:**

1. **Crear estudiante válido:**
   ```bash
   curl -X POST "http://localhost:8000/estudiantes/" \
        -H "Content-Type: application/json" \
        -d '{
          "registro_academico": "202312345",
          "nombre": "Juan",
          "apellido": "Pérez",
          "ci": "12345678",
          "correo": "juan.perez@email.com",
          "contrasena": "password123"
        }'
   ```

2. **Intentar crear estudiante duplicado (debe fallar):**
   ```bash
   # Repetir el mismo request anterior
   # Debería retornar error 409 con mensaje específico
   ```

3. **Login y autenticación:**
   ```bash
   curl -X POST "http://localhost:8000/auth/login-estudiante" \
        -H "Content-Type: application/json" \
        -d '{
          "registro_academico": "202312345",
          "contrasena": "password123"
        }'
   ```

4. **Operaciones con autenticación:**
   ```bash
   # Usar el token obtenido en el login
   curl -X GET "http://localhost:8000/estudiantes/me" \
        -H "Authorization: Bearer <tu-token-aqui>"
   ```

### **Validación de Errores:**

- **400 Bad Request:** Datos de entrada inválidos
- **401 Unauthorized:** Token inválido o expirado
- **403 Forbidden:** Permisos insuficientes
- **404 Not Found:** Recurso no encontrado
- **409 Conflict:** Recurso ya existe (duplicado)
- **500 Internal Server Error:** Error interno del servidor

## 🔒 Seguridad Implementada

### **Headers de Seguridad Automáticos:**
```
Content-Security-Policy: Configurado para Swagger UI
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
```

### **Autenticación JWT:**
- Tokens con expiración configurable
- Algoritmo HS256 seguro
- Validación automática en endpoints protegidos

### **Logging Seguro:**
- Las contraseñas **nunca** se loggean
- Información sensible protegida
- Logs de auditoría para todas las operaciones

### **Manejo Seguro de Errores:**
- Los errores internos no exponen información del sistema
- Mensajes de error estructurados y consistentes
- Stack traces solo en logs, no en responses

## 📈 Performance y Escalabilidad

### **Métricas Automáticas:**
- Tiempo de procesamiento de cada request
- Performance de operaciones de base de datos
- Detección de endpoints lentos

### **Optimizaciones Implementadas:**
- Conexiones de base de datos optimizadas
- Logging asíncrono para mejor performance
- Middleware eficiente con mínimo overhead

### **Monitoreo de Recursos:**
```bash
# Ver uso de recursos de Docker
docker stats

# Monitorear logs de performance
grep "Tiempo:" logs/requests.log | tail -20
```

## 🚨 Troubleshooting

### **Problemas Comunes:**

1. **Error de conexión a base de datos:**
   ```bash
   # Verificar que PostgreSQL esté funcionando
   docker-compose ps
   
   # Ver logs de la base de datos
   docker-compose logs postgres
   ```

2. **Swagger UI no carga:**
   - Verificar que el CSP permite recursos de CDN
   - Revisar logs del navegador (F12 → Console)

3. **Logs no se generan:**
   - Verificar variables LOG_FILE=true y LOG_DIR en .env
   - Verificar permisos del directorio logs/

4. **Errores de autenticación:**
   - Verificar que SECRET_KEY esté configurado
   - Verificar que el token no haya expirado

### **Comandos de Diagnóstico:**
```bash
# Estado de contenedores
docker-compose ps

# Logs de la aplicación
docker-compose logs app --tail=50

# Logs de la base de datos
docker-compose logs postgres --tail=20

# Verificar conectividad
curl http://localhost:8000/health

# Probar endpoint protegido
curl -H "Authorization: Bearer <token>" http://localhost:8000/estudiantes/me
```
