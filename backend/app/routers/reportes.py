from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.services.reporte import obtener_datos_reporte
from app.services.pdf_generator import generar_pdf
from app.services.excel_generator import generar_excel

router = APIRouter(prefix="/reportes", tags=["Reportes"])


@router.get("/turno")
def datos_reporte_turno(
    turno: str = Query(..., description="Matutino | Vespertino | Nocturno"),
    fecha: date = Query(default=None),
    db: Session = Depends(get_db)
):
    """Retorna los datos del reporte en JSON (para previsualización)."""
    if fecha is None:
        fecha = date.today()
    return obtener_datos_reporte(db, turno, fecha)


@router.get("/exportar/pdf")
def exportar_pdf(
    turno: str = Query(...),
    fecha: date = Query(default=None),
    db: Session = Depends(get_db)
):
    if fecha is None:
        fecha = date.today()

    datos = obtener_datos_reporte(db, turno, fecha)
    pdf_bytes = generar_pdf(datos)

    nombre = f"reporte_{turno.lower()}_{fecha.strftime('%Y%m%d')}.pdf"
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={nombre}"}
    )


@router.get("/exportar/excel")
def exportar_excel(
    turno: str = Query(...),
    fecha: date = Query(default=None),
    db: Session = Depends(get_db)
):
    if fecha is None:
        fecha = date.today()

    datos = obtener_datos_reporte(db, turno, fecha)
    excel_bytes = generar_excel(datos)

    nombre = f"reporte_{turno.lower()}_{fecha.strftime('%Y%m%d')}.xlsx"
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename={nombre}"}
    )