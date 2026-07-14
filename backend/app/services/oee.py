from typing import List


def calcular_oee(
    tiempo_disponible_min: float,
    tiempo_paro_min: float,
    unidades_objetivo: int,
    unidades_producidas: int,
    unidades_defectuosas: int
) -> dict:
    """
    Calcula el OEE (Disponibilidad * Rendimiento * Calidad)
    """
    tiempo_operativo = tiempo_disponible_min - tiempo_paro_min
    disponibilidad = (tiempo_operativo / tiempo_disponible_min) if tiempo_disponible_min > 0 else 0

    rendimiento = (unidades_producidas / unidades_objetivo) if unidades_objetivo > 0 else 0
    rendimiento = min(rendimiento, 1.0)

    unidades_buenas = unidades_producidas - unidades_defectuosas
    calidad = (unidades_buenas / unidades_producidas) if unidades_producidas > 0 else 0

    oee = disponibilidad * rendimiento * calidad

    return {
        "disponibilidad": round(disponibilidad * 100, 2),
        "rendimiento": round(rendimiento * 100, 2),
        "calidad": round(calidad * 100, 2),
        "oee": round(oee * 100, 2),
        "clasificacion": clasificar_oee(oee * 100)
    }


def clasificar_oee(oee: float) -> str:
    if oee >= 85:
        return "Clase Mundial"
    elif oee >= 65:
        return "Aceptable"
    elif oee >= 45:
        return "Regular"
    else:
        return "Crítico"