from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class EstadoOrden(str, enum.Enum):
    PENDIENTE = "pendiente"
    EN_PROCESO = "en_proceso"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"


class Orden(Base):
    __tablename__ = "ordenes"

    id = Column(Integer, primary_key=True, index=True)
    numero_orden = Column(String(30), unique=True, nullable=False)  # Ej: "ORD-2024-001"
    producto = Column(String(100), nullable=False)                   # Ej: "Acura ADX - Carrocería"
    unidades_objetivo = Column(Integer, nullable=False)
    unidades_producidas = Column(Integer, default=0)
    unidades_defectuosas = Column(Integer, default=0)
    estado = Column(Enum(EstadoOrden), default=EstadoOrden.PENDIENTE)
    turno = Column(String(20), nullable=False)                       # "Matutino", "Vespertino", "Nocturno"
    fecha_inicio = Column(DateTime, nullable=True)
    fecha_fin = Column(DateTime, nullable=True)
    creada_en = Column(DateTime, default=datetime.utcnow)

    # Llave foránea a Maquina
    maquina_id = Column(Integer, ForeignKey("maquinas.id"), nullable=False)
    maquina = relationship("Maquina", back_populates="ordenes")

    @property
    def eficiencia(self):
        """Porcentaje de unidades buenas sobre objetivo."""
        if self.unidades_objetivo == 0:
            return 0.0
        buenas = self.unidades_producidas - self.unidades_defectuosas
        return round((buenas / self.unidades_objetivo) * 100, 2)

    def __repr__(self):
        return f"<Orden {self.numero_orden} - {self.estado}>"