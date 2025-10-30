from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from typing import Optional

# Esquemas para Pago
class PagoBase(BaseModel):
    registro_academico: Optional[str] = None
    descripcion: Optional[str] = None
    monto: Optional[Decimal] = None
    fecha_pago: Optional[date] = None

class PagoCreate(PagoBase):
    codigo_pago: str

class PagoUpdate(BaseModel):
    registro_academico: Optional[str] = None
    descripcion: Optional[str] = None
    monto: Optional[Decimal] = None
    fecha_pago: Optional[date] = None

class PagoResponse(PagoBase):
    codigo_pago: str
    
    class Config:
        orm_mode = True