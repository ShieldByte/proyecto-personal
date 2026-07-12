from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Defecto(Base):
    __tablename__ = "defectos"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String(100), nullable=False)       # Ej: "Soldadura incompleta"
    descripcion = Column(Text, nullable=True)
    cantidad = Column(Integer, default=1)
    registrado_en = Column(DateTime, default=datetime.utcnow)

    orden_id = Column(Integer, ForeignKey("ordenes.id"), nullable=False)

    def __repr__(self):
        return f"<Defecto {self.tipo} x{self.cantidad}>"