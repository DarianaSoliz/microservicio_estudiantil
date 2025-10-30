from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class Bloqueo(Base):
    __tablename__ = "bloqueo"
    
    codigo_bloqueo = Column(String(10), primary_key=True)
    registro_academico = Column(String(10), ForeignKey('estudiante.registro_academico'))
    descripcion = Column(String(100))
    
    # Relación con estudiante
    estudiante = relationship("Estudiante", back_populates="bloqueos")