# 🚀 Microservicio Estudiantil - Configuración Local

## 📋 Descripción
API para gestión de estudiantes, pagos y bloqueos desarrollada con FastAPI y PostgreSQL. Este documento describe los pasos para ejecutar el proyecto localmente sin Docker, conectándose a una base de datos PostgreSQL en Aiven.

## 🛠️ Requisitos Previos
- Python 3.13+ instalado
- Git instalado
- Acceso a internet para conectar a la base de datos de Aiven

## 📦 Configuración del Entorno

### 1. Clonar el Repositorio
```bash
git clone <tu-repositorio>
cd microservicio_estudiantil
```

### 2. Crear y Activar Entorno Virtual
```bash
# Crear entorno virtual
python -m venv .venv

# Activar entorno virtual
# En Windows PowerShell:
.venv\Scripts\Activate.ps1

# En Windows CMD:
.venv\Scripts\activate.bat

# En Linux/Mac:
source .venv/bin/activate
```

### 3. Instalar Dependencias
```bash
# Actualizar pip
python -m pip install --upgrade pip

# Instalar dependencias del proyecto
pip install -r requirements.txt
```

### 4. Configurar Variables de Entorno

El archivo `.env` ya está configurado con las credenciales de Aiven PostgreSQL:

```env
# Variables de entorno para la base de datos PostgreSQL - Aiven
DB_HOST="topicos-xd.i.aivencloud.com"
DB_NAME="defaultdb"
DB_PASSWORD="AVNS_6kmcp-nNyDI2rk7mUHg"
DB_PORT="18069"
DB_USER="avnadmin"

# URL de conexión a la base de datos principal - Aiven PostgreSQL
DATABASE_URL=postgresql://avnadmin:AVNS_6kmcp-nNyDI2rk7mUHg@topicos-xd.i.aivencloud.com:18069/defaultdb?sslmode=require
```

## 🔧 Solución de Problemas de Compatibilidad

### Problema con SQLAlchemy y Python 3.13
Si encuentras errores de compatibilidad con SQLAlchemy 2.0.x, ejecuta:

```bash
# Desinstalar SQLAlchemy 2.x
pip uninstall sqlalchemy -y

# Instalar SQLAlchemy 1.4.x compatible
pip install "sqlalchemy>=1.4,<2.0"
```

### Problema con FastAPI y Pydantic 2.x
Si encuentras errores relacionados con `'FieldInfo' object has no attribute 'in_'`, ejecuta:

```bash
# Instalar versiones compatibles
pip install fastapi==0.95.2 "pydantic>=1.8.0,<2.0"
```

### Verificar Instalación de psycopg2
Si psycopg2 no se instala correctamente:

```bash
pip install psycopg2-binary
```

## 🚀 Ejecutar la Aplicación

### 1. Probar Conexión a Base de Datos (Opcional)
```bash
python test_connection.py
```

Deberías ver la versión de PostgreSQL si la conexión es exitosa.

### 2. Ejecutar el Servidor
```bash
# Ejecutar con recarga automática
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# O ejecutar sin recarga automática
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 3. Verificar que el Servidor Esté Funcionando
El servidor debería mostrar logs similares a:

```
INFO:     Will watch for changes in these directories: ['...\microservicio_estudiantil']
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process [XXXX] using StatReload
2025-10-30 XX:XX:XX - app.config.logging - INFO - Sistema de logging configurado - Nivel: INFO
2025-10-30 XX:XX:XX - app.main - INFO - Creando tablas de base de datos...
2025-10-30 XX:XX:XX - app.main - INFO - Tablas de base de datos creadas exitosamente
2025-10-30 XX:XX:XX - app.main - INFO - Aplicación FastAPI inicializada
2025-10-30 XX:XX:XX - app.main - INFO - CORS configurado
2025-10-30 XX:XX:XX - app.main - INFO - Routers incluidos exitosamente
INFO:     Started server process [XXXX]
INFO:     Waiting for application startup.
2025-10-30 XX:XX:XX - app.main - INFO - === MICROSERVICIO ESTUDIANTIL INICIADO ===
2025-10-30 XX:XX:XX - app.main - INFO - Versión: 1.0.0
INFO:     Application startup complete.
```

## 🌐 Acceder a la Aplicación

Una vez que el servidor esté ejecutándose, puedes acceder a:

- **API Principal**: http://localhost:8000
- **Documentación Swagger**: http://localhost:8000/docs
- **Documentación ReDoc**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## 📊 Endpoints Principales

### Autenticación
- `POST /login` - Iniciar sesión con registro académico

### Estudiantes
- `GET /estudiantes/` - Listar estudiantes
- `POST /estudiantes/` - Crear estudiante
- `GET /estudiantes/{registro_academico}` - Obtener estudiante específico
- `PUT /estudiantes/{registro_academico}` - Actualizar estudiante
- `DELETE /estudiantes/{registro_academico}` - Eliminar estudiante

### Pagos
- `GET /pagos/` - Listar pagos
- `POST /pagos/` - Crear pago
- `GET /pagos/{pago_id}` - Obtener pago específico

### Bloqueos
- `GET /bloqueos/` - Listar bloqueos
- `POST /bloqueos/` - Crear bloqueo
- `GET /bloqueos/{bloqueo_id}` - Obtener bloqueo específico

## 🗄️ Configuración de Base de Datos

### Información de Conexión (Aiven PostgreSQL)
- **Host**: topicos-xd.i.aivencloud.com
- **Puerto**: 18069
- **Base de datos**: defaultdb
- **Usuario**: avnadmin
- **SSL**: Requerido

### Tablas Principales
- `estudiante` - Información de estudiantes
- `pago` - Registro de pagos
- `bloqueo` - Bloqueos académicos

## 🔧 Comandos Útiles

### Detener la Aplicación
```bash
# Presionar Ctrl+C en la terminal donde se ejecuta uvicorn
```

### Verificar Dependencias Instaladas
```bash
pip list
```

### Generar nuevo requirements.txt
```bash
pip freeze > requirements.txt
```

### Ejecutar Tests (si los hay)
```bash
pytest
```

## 📝 Estructura del Proyecto

```
microservicio_estudiantil/
├── app/
│   ├── __init__.py
│   ├── main.py              # Punto de entrada de la aplicación
│   ├── database.py          # Configuración de base de datos
│   ├── auth.py              # Autenticación JWT
│   ├── middleware.py        # Middlewares personalizados
│   ├── exceptions.py        # Excepciones personalizadas
│   ├── config/
│   │   └── logging.py       # Configuración de logging
│   ├── models/              # Modelos SQLAlchemy
│   │   ├── estudiante.py
│   │   ├── pago.py
│   │   └── bloqueo.py
│   ├── schemas/             # Esquemas Pydantic
│   │   ├── estudiante.py
│   │   ├── pago.py
│   │   ├── bloqueo.py
│   │   └── auth.py
│   ├── crud/                # Operaciones CRUD
│   │   ├── estudiante.py
│   │   ├── pago.py
│   │   └── bloqueo.py
│   └── routers/             # Endpoints de la API
│       ├── auth.py
│       ├── estudiantes.py
│       ├── pagos.py
│       └── bloqueos.py
├── .env                     # Variables de entorno
├── requirements.txt         # Dependencias Python
├── test_connection.py       # Script de prueba de conexión
└── README_SETUP_LOCAL.md    # Este archivo
```

## ⚠️ Notas Importantes

1. **Compatibilidad de Versiones**: Este proyecto requiere versiones específicas de las dependencias para funcionar correctamente con Python 3.13.

2. **Variables de Entorno**: Nunca commitees el archivo `.env` con credenciales reales al repositorio.

3. **Base de Datos**: El proyecto está configurado para conectarse a una instancia de PostgreSQL en Aiven. Las tablas se crean automáticamente al iniciar la aplicación.

4. **Logging**: La aplicación genera logs detallados que se pueden encontrar en la carpeta `logs/`.

5. **CORS**: Está configurado para aceptar peticiones desde cualquier origen (`*`). En producción, configura dominios específicos.

## 🆘 Troubleshooting

### Error: "No module named 'psycopg2'"
```bash
pip install psycopg2-binary
```

### Error: "Class SQLCoreOperations directly inherits TypingOnly"
```bash
pip uninstall sqlalchemy -y
pip install "sqlalchemy>=1.4,<2.0"
```

### Error: "'FieldInfo' object has no attribute 'in_'"
```bash
pip install fastapi==0.95.2 "pydantic>=1.8.0,<2.0"
```

### Error de conexión a base de datos
- Verifica que tengas acceso a internet
- Verifica las credenciales en el archivo `.env`
- Ejecuta `python test_connection.py` para probar la conexión

## 📞 Soporte

Si encuentras problemas no cubiertos en esta guía, revisa:
1. Los logs de la aplicación en la carpeta `logs/`
2. La salida de la consola donde ejecutas uvicorn
3. Verifica que todas las dependencias estén instaladas correctamente

---

**¡Listo!** Tu microservicio estudiantil debería estar funcionando correctamente en http://localhost:8000 🎉