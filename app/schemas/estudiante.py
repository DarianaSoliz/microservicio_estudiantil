from pydantic import BaseModel, Field
from typing import Optional

# Esquemas para Estudiante
class EstudianteBase(BaseModel):
    codigo_carrera: Optional[str] = None
    registro_academico: str
    nombre: str
    apellido: str
    ci: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    estado_academico: Optional[str] = "REGULAR"

class EstudianteCreate(EstudianteBase):
    contrasena: str = Field(..., min_length=4, max_length=50, description="Contraseña del estudiante")

class EstudianteUpdate(BaseModel):
    codigo_carrera: Optional[str] = None
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    ci: Optional[str] = None
    correo: Optional[str] = None
    telefono: Optional[str] = None
    direccion: Optional[str] = None
    estado_academico: Optional[str] = None

class EstudianteResponse(EstudianteBase):
    class Config:
        orm_mode = True