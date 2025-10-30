# Microservicio Estudiantil - Sistema de Excepciones y Logging

Este documento describe las mejoras implementadas en el microservicio estudiantil, incluyendo un sistema robusto de excepciones personalizadas y logging comprehensivo.

## 🚀 Nuevas Características Implementadas

### 1. Sistema de Excepciones Personalizadas

#### Ubicación: `app/exceptions.py`

Se implementó un sistema jerárquico de excepciones personalizadas que incluye:

**Excepciones Base:**
- `BaseCustomException`: Clase base para todas las excepciones personalizadas
- `ValidationError`: Para errores de validación de datos
- `NotFoundError`: Para recursos no encontrados
- `ConflictError`: Para conflictos de recursos (duplicados, etc.)
- `AuthenticationError`: Para errores de autenticación
- `AuthorizationError`: Para errores de autorización
- `DatabaseError`: Para errores de base de datos

**Excepciones Específicas del Dominio:**
- `EstudianteNotFoundError` / `EstudianteAlreadyExistsError`
- `PagoNotFoundError` / `PagoAlreadyExistsError`
- `BloqueoNotFoundError`
- `InsufficientPermissionsError`
- `InvalidCredentialsError`
- `TokenExpiredError` / `InvalidTokenError`

**Función de Mapeo:**
- `map_exception_to_http()`: Convierte excepciones personalizadas a HTTPException de FastAPI

### 2. Sistema de Logging Centralizado

#### Ubicación: `app/config/logging.py`

**Características del Sistema de Logging:**

- **Configuración Centralizada**: Un solo punto de configuración para todo el logging
- **Múltiples Formatters**: 
  - `ColoredFormatter`: Para consola con colores
  - `RequestFormatter`: Para requests HTTP con información contextual
  - `DetailedFormatter`: Para archivos con información completa
- **Múltiples Handlers**:
  - Consola con colores
  - Archivo de aplicación general (`logs/app.log`)
  - Archivo de errores (`logs/errors.log`)
  - Archivo de requests HTTP (`logs/requests.log`)
  - Archivo de base de datos (`logs/database.log`)
- **Rotación de Archivos**: Automática por tamaño (10MB por archivo)
- **Decoradores de Utilidad**:
  - `@log_function_call`: Loggea llamadas a funciones
  - `@log_execution_time`: Loggea tiempo de ejecución

**Configuración por Variables de Entorno:**
```bash
LOG_LEVEL=INFO          # Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_DIR=logs           # Directorio de logs
LOG_CONSOLE=true       # Habilitar logging en consola
LOG_FILE=true          # Habilitar logging en archivos
```

### 3. Middleware Avanzado

#### Ubicación: `app/middleware.py`

**Middlewares Implementados:**

1. **ExceptionHandlerMiddleware**:
   - Captura todas las excepciones no manejadas
   - Convierte excepciones personalizadas a respuestas HTTP apropiadas
   - Loggea excepciones con información contextual

2. **RequestLoggingMiddleware**:
   - Genera ID único para cada request
   - Loggea información completa de requests y responses
   - Mide tiempo de procesamiento
   - Agrega headers de debugging (`X-Request-ID`, `X-Process-Time`)

3. **SecurityHeadersMiddleware**:
   - Agrega headers de seguridad estándar
   - Content Security Policy básico
   - Protección XSS y clickjacking

4. **DatabaseConnectionMiddleware**:
   - Loggea operaciones de base de datos
   - Específico para métodos que modifican datos

### 4. Mejoras en Módulos CRUD

#### Archivos Actualizados:
- `app/crud/estudiante.py`
- `app/crud/pago.py`
- `app/crud/bloqueo.py`

**Mejoras Implementadas:**
- **Manejo de Excepciones**: Uso de excepciones personalizadas en lugar de retornar `None`
- **Logging Detallado**: Logging de todas las operaciones con información contextual
- **Validaciones Mejoradas**: Validaciones más robustas con mensajes específicos
- **Manejo de Transacciones**: Rollback automático en caso de errores
- **Decoradores de Performance**: Medición de tiempo de ejecución

### 5. Mejoras en Routers

#### Archivos Actualizados:
- `app/routers/estudiantes.py`
- `app/routers/auth.py`

**Mejoras Implementadas:**
- **Manejo de Excepciones Unificado**: Captura y mapeo consistente de excepciones
- **Logging de Operaciones**: Logging detallado de todas las operaciones
- **Documentación Mejorada**: Docstrings detallados para todos los endpoints
- **Respuestas Consistentes**: Formato estándar para todas las respuestas de error

### 6. Configuración Principal Mejorada

#### Archivo: `app/main.py`

**Mejoras:**
- **Inicialización con Logging**: Logging de todo el proceso de inicialización
- **Middleware Integrado**: Configuración automática de todos los middlewares
- **Manejadores de Eventos**: Eventos de startup y shutdown con logging
- **Manejadores de Excepciones**: Configuración de manejadores globales

## 📁 Estructura de Archivos de Log

Cuando ejecutes la aplicación, se creará automáticamente la siguiente estructura de logs:

```
logs/
├── app.log           # Log general de la aplicación
├── errors.log        # Solo errores y excepciones
├── requests.log      # Requests HTTP con trazabilidad
└── database.log      # Operaciones de base de datos
```

## 🔧 Configuración y Uso

### 1. Variables de Entorno

Copia el archivo `.env.example` a `.env` y configura las variables:

```bash
cp .env.example .env
```

### 2. Instalación de Dependencias

```bash
pip install -r requirements.txt
```

### 3. Ejecución

```bash
uvicorn app.main:app --reload --log-level info
```

### 4. Monitoreo de Logs

Para monitorear los logs en tiempo real:

```bash
# Log general
tail -f logs/app.log

# Solo errores
tail -f logs/errors.log

# Requests HTTP
tail -f logs/requests.log
```

## 📊 Ejemplo de Log Output

### Request Logging
```
2024-10-28 10:30:15 [abc12345] - app.middleware - INFO - Request iniciado: POST /estudiantes
2024-10-28 10:30:15 [abc12345] - app.routers.estudiantes - INFO - Creando estudiante: 202312345
2024-10-28 10:30:15 [abc12345] - app.crud.estudiante - INFO - Buscando estudiante con registro académico: 202312345
2024-10-28 10:30:15 [abc12345] - app.crud.estudiante - INFO - Estudiante creado exitosamente: 202312345
2024-10-28 10:30:15 [abc12345] - app.middleware - INFO - Request completado: POST /estudiantes - Status: 201 - Tiempo: 0.0234s
```

### Error Logging
```
2024-10-28 10:31:20 [def67890] - app.crud.estudiante - WARNING - Ya existe estudiante con registro académico: 202312345
2024-10-28 10:31:20 [def67890] - app.routers.estudiantes - WARNING - Error controlado al crear estudiante: Ya existe un estudiante con registro_academico: 202312345
```

## 🧪 Testing del Sistema

### Casos de Prueba Recomendados

1. **Crear estudiante duplicado** - Debe retornar error 409 con mensaje específico
2. **Acceder sin autenticación** - Debe retornar error 401
3. **Actualizar datos de otro estudiante** - Debe retornar error 403
4. **Buscar estudiante inexistente** - Debe retornar error 404
5. **Parámetros de paginación inválidos** - Debe retornar error 400

### Endpoints de Monitoreo

- `GET /health` - Health check básico
- `GET /` - Verificación de funcionamiento
- Headers de respuesta incluyen `X-Request-ID` y `X-Process-Time`

## 🔒 Consideraciones de Seguridad

1. **Headers de Seguridad**: Automáticamente agregados por `SecurityHeadersMiddleware`
2. **Logging Seguro**: No se loggean contraseñas ni datos sensibles
3. **Trazabilidad**: Cada request tiene un ID único para auditoría
4. **Error Handling**: Los errores internos no exponen información sensible

## 📈 Beneficios Implementados

1. **Debugging Mejorado**: Logs detallados facilitan la identificación de problemas
2. **Monitoreo**: Métricas de performance y trazabilidad completa
3. **Mantenibilidad**: Código más limpio con manejo consistente de errores
4. **Escalabilidad**: Sistema preparado para entornos de producción
5. **Seguridad**: Manejo seguro de errores y logging de auditoría

