from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class Maquina(Base):
    __tablename__ = "maquinas"

    id = Column(Integer, primary_key=True, index=True)
    codigo = Column(String(20), unique=True, nullable=False)  # Ej: "EST-01"
    nombre = Column(String(100), nullable=False)              # Ej: "Estación Soldadura"
    area = Column(String(50), nullable=False)                 # Ej: "Carrocería"
    activa = Column(Boolean, default=True)
    creada_en = Column(DateTime, default=datetime.utcnow)

    # Relación: una máquina tiene muchas órdenes
    ordenes = relationship("Orden", back_populates="maquina")

    def __repr__(self):
        return f"<Maquina {self.codigo} - {self.nombre}>"
