from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.models.orden import EstadoOrden
from app.models.alerta import SeveridadAlerta, TipoAlerta


# --- Esquemas para Máquina ---

class MaquinaBase(BaseModel):
    codigo: str = Field(..., example="EST-01")
    nombre: str = Field(..., example="Estación Soldadura")
    area: str = Field(..., example="Carrocería")

class MaquinaCreate(MaquinaBase):
    pass

class MaquinaResponse(MaquinaBase):
    id: int
    activa: bool
    creada_en: datetime

    class Config:
        from_attributes = True


# --- Esquemas para Orden ---

class OrdenBase(BaseModel):
    numero_orden: str = Field(..., example="ORD-2024-001")
    producto: str = Field(..., example="Acura ADX - Carrocería")
    unidades_objetivo: int = Field(..., gt=0)
    turno: str = Field(..., example="Matutino")
    maquina_id: int

class OrdenCreate(OrdenBase):
    pass

class OrdenUpdate(BaseModel):
    unidades_producidas: Optional[int] = None
    unidades_defectuosas: Optional[int] = None
    estado: Optional[EstadoOrden] = None

class OrdenResponse(OrdenBase):
    id: int
    unidades_producidas: int
    unidades_defectuosas: int
    estado: EstadoOrden
    eficiencia: float
    fecha_inicio: Optional[datetime]
    fecha_fin: Optional[datetime]
    creada_en: datetime

    class Config:
        from_attributes = True


# --- Esquema para Defecto ---

class DefectoCreate(BaseModel):
    tipo: str = Field(..., example="Soldadura incompleta")
    descripcion: Optional[str] = None
    cantidad: int = Field(default=1, gt=0)
    orden_id: int

class DefectoResponse(DefectoCreate):
    id: int
    registrado_en: datetime

    class Config:
        from_attributes = True


class AlertaResponse(BaseModel):
    id: int
    tipo: TipoAlerta
    severidad: SeveridadAlerta
    mensaje: str
    detalle: Optional[str]
    resuelta: bool
    orden_id: Optional[int]
    creada_en: datetime
    resuelta_en: Optional[datetime]

    class Config:
        from_attributes = True