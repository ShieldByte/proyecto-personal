from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.models.orden import Orden, EstadoOrden
from app.models.maquina import Maquina
from app.schemas import OrdenCreate, OrdenResponse, OrdenUpdate

router = APIRouter(prefix="/ordenes", tags=["Órdenes de Producción"])


@router.get("/", response_model=List[OrdenResponse])
def listar_ordenes(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Retorna todas las órdenes de producción."""
    return db.query(Orden).offset(skip).limit(limit).all()


@router.get("/{orden_id}", response_model=OrdenResponse)
def obtener_orden(orden_id: int, db: Session = Depends(get_db)):
    orden = db.query(Orden).filter(Orden.id == orden_id).first()
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    return orden


@router.post("/", response_model=OrdenResponse, status_code=status.HTTP_201_CREATED)
def crear_orden(orden: OrdenCreate, db: Session = Depends(get_db)):
    """Crea una nueva orden de producción."""
    # Verificar que la máquina existe
    maquina = db.query(Maquina).filter(Maquina.id == orden.maquina_id).first()
    if not maquina:
        raise HTTPException(status_code=404, detail="Máquina no encontrada")

    nueva_orden = Orden(**orden.model_dump())
    db.add(nueva_orden)
    db.commit()
    db.refresh(nueva_orden)
    return nueva_orden


@router.patch("/{orden_id}", response_model=OrdenResponse)
def actualizar_orden(orden_id: int, datos: OrdenUpdate, db: Session = Depends(get_db)):
    """Actualiza el avance de una orden (unidades producidas, defectos, estado)."""
    orden = db.query(Orden).filter(Orden.id == orden_id).first()
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")

    update_data = datos.model_dump(exclude_unset=True)

    # Si se marca como en proceso, registrar fecha de inicio
    if update_data.get("estado") == EstadoOrden.EN_PROCESO and not orden.fecha_inicio:
        update_data["fecha_inicio"] = datetime.utcnow()

    # Si se completa, registrar fecha de fin
    if update_data.get("estado") == EstadoOrden.COMPLETADA and not orden.fecha_fin:
        update_data["fecha_fin"] = datetime.utcnow()

    for campo, valor in update_data.items():
        setattr(orden, campo, valor)

    db.commit()
    db.refresh(orden)
    return orden


@router.delete("/{orden_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_orden(orden_id: int, db: Session = Depends(get_db)):
    orden = db.query(Orden).filter(Orden.id == orden_id).first()
    if not orden:
        raise HTTPException(status_code=404, detail="Orden no encontrada")
    db.delete(orden)
    db.commit()