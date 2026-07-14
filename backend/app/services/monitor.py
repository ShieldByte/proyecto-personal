from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.models.orden import Orden, EstadoOrden
from app.models.alerta import Alerta, TipoAlerta, SeveridadAlerta
from app.services.oee import calcular_oee

# ===== UMBRALES CONFIGURABLES =====
UMBRALES = {
    "oee_critico": 45.0,        # OEE < 45% → alerta crítica
    "oee_advertencia": 65.0,    # OEE < 65% → advertencia
    "defectos_pct_critico": 10.0,   # >10% defectos → crítico
    "defectos_pct_advertencia": 5.0, # >5% defectos → advertencia
    "calidad_minima": 90.0,     # Calidad < 90% → advertencia
    "minutos_sin_avance": 60,   # Orden en proceso sin actualizar > 60 min
}


def ya_existe_alerta_activa(db: Session, tipo: TipoAlerta, orden_id: int = None) -> bool:
    """Evita duplicar alertas del mismo tipo para la misma orden."""
    query = db.query(Alerta).filter(
        Alerta.tipo == tipo,
        Alerta.resuelta == False
    )
    if orden_id:
        query = query.filter(Alerta.orden_id == orden_id)
    return query.first() is not None


def crear_alerta(
    db: Session,
    tipo: TipoAlerta,
    severidad: SeveridadAlerta,
    mensaje: str,
    detalle: str = None,
    orden_id: int = None
) -> Alerta:
    alerta = Alerta(
        tipo=tipo,
        severidad=severidad,
        mensaje=mensaje,
        detalle=detalle,
        orden_id=orden_id
    )
    db.add(alerta)
    db.commit()
    db.refresh(alerta)
    return alerta


def evaluar_alertas(db: Session) -> list:
    """
    Evalúa todas las reglas de negocio y genera alertas cuando
    se violan los umbrales. Retorna lista de alertas nuevas.
    """
    nuevas_alertas = []

    # ── 1. ALERTA DE OEE GLOBAL ──────────────────────────────
    totales = db.query(
        func.sum(Orden.unidades_objetivo).label("objetivo"),
        func.sum(Orden.unidades_producidas).label("producidas"),
        func.sum(Orden.unidades_defectuosas).label("defectuosas")
    ).filter(Orden.estado == EstadoOrden.EN_PROCESO).first()

    if totales.objetivo and totales.objetivo > 0:
        oee = calcular_oee(
            tiempo_disponible_min=480,
            tiempo_paro_min=30,
            unidades_objetivo=totales.objetivo,
            unidades_producidas=totales.producidas or 0,
            unidades_defectuosas=totales.defectuosas or 0
        )

        if oee["oee"] < UMBRALES["oee_critico"]:
            if not ya_existe_alerta_activa(db, TipoAlerta.OEE_BAJO):
                alerta = crear_alerta(
                    db,
                    tipo=TipoAlerta.OEE_BAJO,
                    severidad=SeveridadAlerta.CRITICA,
                    mensaje=f"OEE crítico: {oee['oee']}% (mínimo esperado: {UMBRALES['oee_critico']}%)",
                    detalle=(
                        f"Disponibilidad: {oee['disponibilidad']}% | "
                        f"Rendimiento: {oee['rendimiento']}% | "
                        f"Calidad: {oee['calidad']}%"
                    )
                )
                nuevas_alertas.append(alerta)

        elif oee["oee"] < UMBRALES["oee_advertencia"]:
            if not ya_existe_alerta_activa(db, TipoAlerta.OEE_BAJO):
                alerta = crear_alerta(
                    db,
                    tipo=TipoAlerta.OEE_BAJO,
                    severidad=SeveridadAlerta.ADVERTENCIA,
                    mensaje=f"OEE bajo: {oee['oee']}% (objetivo: ≥{UMBRALES['oee_advertencia']}%)",
                    detalle=f"Calidad: {oee['calidad']}% | Rendimiento: {oee['rendimiento']}%"
                )
                nuevas_alertas.append(alerta)

        # Alerta de calidad baja independiente
        if oee["calidad"] < UMBRALES["calidad_minima"]:
            if not ya_existe_alerta_activa(db, TipoAlerta.CALIDAD_BAJA):
                alerta = crear_alerta(
                    db,
                    tipo=TipoAlerta.CALIDAD_BAJA,
                    severidad=SeveridadAlerta.ADVERTENCIA,
                    mensaje=f"Calidad por debajo del estándar: {oee['calidad']}%",
                    detalle="Revisar proceso de inspección y estaciones con mayor índice de defectos."
                )
                nuevas_alertas.append(alerta)

    # ── 2. ALERTAS POR ORDEN ─────────────────────────────────
    ordenes_activas = db.query(Orden).filter(
        Orden.estado == EstadoOrden.EN_PROCESO
    ).all()

    for orden in ordenes_activas:

        # Tasa de defectos por orden
        if orden.unidades_producidas > 0:
            pct_defectos = (orden.unidades_defectuosas / orden.unidades_producidas) * 100

            if pct_defectos > UMBRALES["defectos_pct_critico"]:
                if not ya_existe_alerta_activa(db, TipoAlerta.DEFECTOS_ALTO, orden.id):
                    alerta = crear_alerta(
                        db,
                        tipo=TipoAlerta.DEFECTOS_ALTO,
                        severidad=SeveridadAlerta.CRITICA,
                        mensaje=f"Tasa de defectos crítica en {orden.numero_orden}: {pct_defectos:.1f}%",
                        detalle=f"{orden.unidades_defectuosas} defectos de {orden.unidades_producidas} unidades producidas.",
                        orden_id=orden.id
                    )
                    nuevas_alertas.append(alerta)

            elif pct_defectos > UMBRALES["defectos_pct_advertencia"]:
                if not ya_existe_alerta_activa(db, TipoAlerta.DEFECTOS_ALTO, orden.id):
                    alerta = crear_alerta(
                        db,
                        tipo=TipoAlerta.DEFECTOS_ALTO,
                        severidad=SeveridadAlerta.ADVERTENCIA,
                        mensaje=f"Defectos elevados en {orden.numero_orden}: {pct_defectos:.1f}%",
                        detalle=f"Umbral permitido: {UMBRALES['defectos_pct_advertencia']}%",
                        orden_id=orden.id
                    )
                    nuevas_alertas.append(alerta)

        # Orden detenida (en proceso pero sin actualizarse hace mucho)
        if orden.fecha_inicio:
            minutos_sin_avance = (datetime.utcnow() - orden.fecha_inicio).total_seconds() / 60
            if minutos_sin_avance > UMBRALES["minutos_sin_avance"]:
                if not ya_existe_alerta_activa(db, TipoAlerta.ORDEN_DETENIDA, orden.id):
                    alerta = crear_alerta(
                        db,
                        tipo=TipoAlerta.ORDEN_DETENIDA,
                        severidad=SeveridadAlerta.ADVERTENCIA,
                        mensaje=f"Orden {orden.numero_orden} sin actualización por {int(minutos_sin_avance)} min",
                        detalle="Verificar si la estación está operativa o si hay un paro no registrado.",
                        orden_id=orden.id
                    )
                    nuevas_alertas.append(alerta)

    return nuevas_alertas