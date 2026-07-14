from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum, Text
from datetime import datetime
import enum
from app.database import Base


class SeveridadAlerta(str, enum.Enum):
    INFO = "info"
    ADVERTENCIA = "advertencia"
    CRITICA = "critica"


class TipoAlerta(str, enum.Enum):
    OEE_BAJO = "oee_bajo"
    DEFECTOS_ALTO = "defectos_alto"
    ORDEN_DETENIDA = "orden_detenida"
    CALIDAD_BAJA = "calidad_baja"
    RENDIMIENTO_BAJO = "rendimiento_bajo"


class Alerta(Base):
    __tablename__ = "alertas"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(Enum(TipoAlerta), nullable=False)
    severidad = Column(Enum(SeveridadAlerta), nullable=False)
    mensaje = Column(String(255), nullable=False)
    detalle = Column(Text, nullable=True)
    resuelta = Column(Boolean, default=False)
    orden_id = Column(Integer, ForeignKey("ordenes.id"), nullable=True)
    creada_en = Column(DateTime, default=datetime.utcnow)
    resuelta_en = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<Alerta [{self.severidad}] {self.tipo} - {self.mensaje[:40]}>"