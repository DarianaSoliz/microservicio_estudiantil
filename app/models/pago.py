from sqlalchemy import Column, String, DECIMAL, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Pago(Base):
    __tablename__ = "pago"
    
    codigo_pago = Column(String(10), primary_key=True)
    registro_academico = Column(String(10), ForeignKey('estudiante.registro_academico'))
    descripcion = Column(String(100))
    monto = Column(DECIMAL(10,2))
    fecha_pago = Column(Date, default=func.current_date())
    
    # Relación con estudiante
    estudiante = relationship("Estudiante", back_populates="pagos")