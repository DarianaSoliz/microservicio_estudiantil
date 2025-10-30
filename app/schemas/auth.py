from pydantic import BaseModel, Field
from typing import Optional

# Esquemas para autenticación
class UserLogin(BaseModel):
    registro_academico: str = Field(..., min_length=5, max_length=15, description="Registro académico del estudiante")
    contrasena: str = Field(..., min_length=4, max_length=50, description="Contraseña del estudiante")

class Token(BaseModel):
    access_token: str
    token_type: str
    
class TokenData(BaseModel):
    registro_academico: Optional[str] = None