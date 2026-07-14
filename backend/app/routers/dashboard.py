from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.orden import Orden, EstadoOrden
from app.models.maquina import Maquina
from app.services.oee import calcular_oee

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/resumen")
def resumen_dashboard(db: Session = Depends(get_db)):
    """Retorna los KPIs principales para el dashboard."""

    total_ordenes = db.query(Orden).count()
    ordenes_en_proceso = db.query(Orden).filter(Orden.estado == EstadoOrden.EN_PROCESO).count()
    ordenes_completadas = db.query(Orden).filter(Orden.estado == EstadoOrden.COMPLETADA).count()

    # sumar totales
    totales = db.query(
        func.sum(Orden.unidades_objetivo).label("objetivo"),
        func.sum(Orden.unidades_producidas).label("producidas"),
        func.sum(Orden.unidades_defectuosas).label("defectuosas")
    ).first()

    objetivo = totales.objetivo or 0
    producidas = totales.producidas or 0
    defectuosas = totales.defectuosas or 0

    # calcular oee global (turno de 8 horas y 30 min de descanso)
    oee_global = calcular_oee(
        tiempo_disponible_min=480,
        tiempo_paro_min=30,
        unidades_objetivo=objetivo,
        unidades_producidas=producidas,
        unidades_defectuosas=defectuosas
    )

    return {
        "ordenes": {
            "total": total_ordenes,
            "en_proceso": ordenes_en_proceso,
            "completadas": ordenes_completadas,
        },
        "produccion": {
            "unidades_objetivo": objetivo,
            "unidades_producidas": producidas,
            "unidades_defectuosas": defectuosas,
            "unidades_buenas": producidas - defectuosas,
        },
        "oee": oee_global
    }