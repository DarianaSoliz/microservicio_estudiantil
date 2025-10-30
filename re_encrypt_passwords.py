"""
Script para re-encriptar las contraseñas de los estudiantes en la base de datos
usando bcrypt, tal como lo hace el módulo de autenticación principal.

Ejecuta este archivo una sola vez cada vez que quieras actualizar los hashes
por cambios en la política de contraseñas o después de migraciones de datos.
"""

import os
import bcrypt
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# ============================================================
# 🔧 CONFIGURACIÓN DE CONEXIÓN
# ============================================================

load_dotenv()

# Primero intentamos con la conexión local, luego con la de Docker, y finalmente con un valor predeterminado
DATABASE_URL = (
    os.getenv("DATABASE_URL_LOCAL")
    or os.getenv("DATABASE_URL")
    or "postgres://avnadmin:AVNS_6kmcp-nNyDI2rk7mUHg@topicos-xd.i.aivencloud.com:18069/defaultdb?sslmode=require"
)

print(f"📡 Conectando a la base de datos: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else 'conexión enmascarada'}")
engine = create_engine(DATABASE_URL)

# ============================================================
# 🔐 FUNCIÓN DE ENCRIPTACIÓN
# ============================================================


def hash_password(password: str) -> str:
    """
    Retorna un hash bcrypt seguro basado en la contraseña original.
    """
    password_bytes = password.encode("utf-8")
    if len(password_bytes) > 72:
        password_bytes = password_bytes[:72]
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed.decode("utf-8")


# ============================================================
# 🚀 PROCESO PRINCIPAL
# ============================================================


def reencrypt_student_passwords():
    """
    Vuelve a encriptar todas las contraseñas de los estudiantes
    tomando como base su número de CI actual.
    """
    with engine.begin() as conn:  # Usar begin() para transacciones automáticas
        # Obtener estudiantes con sus CI actuales
        result = conn.execute(
            text("SELECT registro_academico, ci FROM estudiante WHERE ci IS NOT NULL")
        )
        students = result.fetchall()

        print(
            f"🔍 {len(students)} estudiantes encontrados para re-encriptar contraseñas..."
        )

        updated = 0
        for row in students:
            ra = row[0]
            ci = row[1]
            if not ci:
                continue
            hashed = hash_password(ci)
            conn.execute(
                text(
                    "UPDATE estudiante SET contrasena = :hash WHERE registro_academico = :ra"
                ),
                {"hash": hashed, "ra": ra},
            )
            updated += 1

        # No necesitamos commit() explícito con begin()
        print(f"✅ {updated} contraseñas re-encriptadas correctamente usando bcrypt.")


# ============================================================
# ▶️ EJECUCIÓN
# ============================================================

if __name__ == "__main__":
    try:
        reencrypt_student_passwords()
    except Exception as e:
        print("❌ Error durante la re-encriptación:", e)
