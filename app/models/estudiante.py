from sqlalchemy import Column, String, Text
from sqlalchemy.orm import relationship
from app.database import Base

class Estudiante(Base):
    __tablename__ = "estudiante"
    
    # Campo sin clave foránea ya que carrera está en otro microservicio
    codigo_carrera = Column(String(8))
    registro_academico = Column(String(10), primary_key=True)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    ci = Column(String(20), unique=True)
    correo = Column(String(100))
    contrasena = Column(Text, nullable=False)
    telefono = Column(String(20))
    direccion = Column(String(150))
    estado_academico = Column(String(20), default='REGULAR')
    
    # Relaciones
    pagos = relationship("Pago", back_populates="estudiante")
    bloqueos = relationship("Bloqueo", back_populates="estudiante")