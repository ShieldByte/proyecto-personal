from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from typing import Optional

from app.models.orden import Orden, EstadoOrden
from app.models.alerta import Alerta
from app.models.maquina import Maquina
from app.services.oee import calcular_oee


TURNOS_HORARIO = {
    "Matutino":    {"inicio": 6,  "fin": 14},
    "Vespertino":  {"inicio": 14, "fin": 22},
    "Nocturno":    {"inicio": 22, "fin": 6},
}


def obtener_datos_reporte(
    db: Session,
    turno: str,
    fecha: date
) -> dict:
    """
    Recopila todos los datos necesarios para generar el reporte de turno.
    """

    # Órdenes del turno y fecha
    ordenes = db.query(Orden).filter(
        Orden.turno == turno,
        func.date(Orden.creada_en) == fecha
    ).all()

    # Totales de producción
    total_objetivo = sum(o.unidades_objetivo for o in ordenes)
    total_producidas = sum(o.unidades_producidas for o in ordenes)
    total_defectuosas = sum(o.unidades_defectuosas for o in ordenes)
    total_buenas = total_producidas - total_defectuosas

    # OEE del turno
    oee = calcular_oee(
        tiempo_disponible_min=480,
        tiempo_paro_min=30,
        unidades_objetivo=total_objetivo,
        unidades_producidas=total_producidas,
        unidades_defectuosas=total_defectuosas
    ) if total_objetivo > 0 else {
        "disponibilidad": 0, "rendimiento": 0,
        "calidad": 0, "oee": 0, "clasificacion": "Sin datos"
    }

    # Cumplimiento por orden
    ordenes_data = []
    for o in ordenes:
        buenas = o.unidades_producidas - o.unidades_defectuosas
        cumplimiento = round(
            (buenas / o.unidades_objetivo * 100), 1
        ) if o.unidades_objetivo > 0 else 0

        pct_defectos = round(
            (o.unidades_defectuosas / o.unidades_producidas * 100), 1
        ) if o.unidades_producidas > 0 else 0

        ordenes_data.append({
            "numero_orden": o.numero_orden,
            "producto": o.producto,
            "maquina_id": o.maquina_id,
            "estado": o.estado.value,
            "unidades_objetivo": o.unidades_objetivo,
            "unidades_producidas": o.unidades_producidas,
            "unidades_buenas": buenas,
            "unidades_defectuosas": o.unidades_defectuosas,
            "pct_defectos": pct_defectos,
            "cumplimiento": cumplimiento,
        })

    # Alertas del turno
    alertas = db.query(Alerta).filter(
        func.date(Alerta.creada_en) == fecha
    ).order_by(Alerta.creada_en.desc()).all()

    alertas_data = [{
        "tipo": a.tipo.value,
        "severidad": a.severidad.value,
        "mensaje": a.mensaje,
        "resuelta": a.resuelta,
        "hora": a.creada_en.strftime("%H:%M")
    } for a in alertas]

    return {
        "turno": turno,
        "fecha": fecha.strftime("%d/%m/%Y"),
        "fecha_generacion": datetime.now().strftime("%d/%m/%Y %H:%M"),
        "totales": {
            "objetivo": total_objetivo,
            "producidas": total_producidas,
            "buenas": total_buenas,
            "defectuosas": total_defectuosas,
            "cumplimiento": round(
                (total_buenas / total_objetivo * 100), 1
            ) if total_objetivo > 0 else 0
        },
        "oee": oee,
        "ordenes": ordenes_data,
        "alertas": alertas_data,
        "total_ordenes": len(ordenes),
        "ordenes_completadas": sum(
            1 for o in ordenes if o.estado == EstadoOrden.COMPLETADA
        ),
    }