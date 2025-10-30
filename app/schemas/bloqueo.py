from pydantic import BaseModel
from typing import Optional

# Esquemas para Bloqueo
class BloqueoBase(BaseModel):
    registro_academico: Optional[str] = None
    descripcion: Optional[str] = None

class BloqueoCreate(BloqueoBase):
    codigo_bloqueo: str

class BloqueoUpdate(BaseModel):
    registro_academico: Optional[str] = None
    descripcion: Optional[str] = None

class BloqueoResponse(BloqueoBase):
    codigo_bloqueo: str
    
    class Config:
        from_attributes = True