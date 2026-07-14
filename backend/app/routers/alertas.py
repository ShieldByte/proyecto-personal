from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import List
import asyncio
import json
from datetime import datetime

from app.database import get_db, SessionLocal
from app.models.alerta import Alerta, SeveridadAlerta
from app.schemas.orden import AlertaResponse
from app.services.monitor import evaluar_alertas

router = APIRouter(prefix="/alertas", tags=["Alertas"])


# ── Gestor de conexiones WebSocket ──────────────────────────
class GestorWebSocket:
    def __init__(self):
        self.conexiones_activas: List[WebSocket] = []

    async def conectar(self, ws: WebSocket):
        await ws.accept()
        self.conexiones_activas.append(ws)

    def desconectar(self, ws: WebSocket):
        if ws in self.conexiones_activas:
            self.conexiones_activas.remove(ws)

    async def broadcast(self, mensaje: dict):
        caidas = []
        for ws in self.conexiones_activas:
            try:
                await ws.send_text(json.dumps(mensaje, default=str))
            except Exception:
                caidas.append(ws)
        for ws in caidas:
            self.desconectar(ws)


gestor = GestorWebSocket()


# ── Tarea de monitoreo en background ────────────────────────
async def tarea_monitoreo():
    """Se ejecuta cada 30 segundos y evalúa todas las reglas de alerta."""
    while True:
        await asyncio.sleep(30)
        db = SessionLocal()
        try:
            nuevas = evaluar_alertas(db)
            for alerta in nuevas:
                await gestor.broadcast({
                    "evento": "nueva_alerta",
                    "id": alerta.id,
                    "tipo": alerta.tipo,
                    "severidad": alerta.severidad,
                    "mensaje": alerta.mensaje,
                    "detalle": alerta.detalle,
                    "creada_en": alerta.creada_en.isoformat()
                })
        finally:
            db.close()


# ── Endpoints REST ───────────────────────────────────────────
@router.get("/", response_model=List[AlertaResponse])
def listar_alertas(
    solo_activas: bool = True,
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    query = db.query(Alerta)
    if solo_activas:
        query = query.filter(Alerta.resuelta == False)
    return query.order_by(Alerta.creada_en.desc()).offset(skip).limit(limit).all()


@router.patch("/{alerta_id}/resolver")
def resolver_alerta(alerta_id: int, db: Session = Depends(get_db)):
    alerta = db.query(Alerta).filter(Alerta.id == alerta_id).first()
    if not alerta:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Alerta no encontrada")
    alerta.resuelta = True
    alerta.resuelta_en = datetime.utcnow()
    db.commit()
    return {"ok": True, "mensaje": "Alerta marcada como resuelta"}


@router.get("/conteo")
def conteo_alertas(db: Session = Depends(get_db)):
    total = db.query(Alerta).filter(Alerta.resuelta == False).count()
    criticas = db.query(Alerta).filter(
        Alerta.resuelta == False,
        Alerta.severidad == SeveridadAlerta.CRITICA
    ).count()
    return {"total": total, "criticas": criticas}


# ── WebSocket ────────────────────────────────────────────────
@router.websocket("/ws")
async def websocket_alertas(ws: WebSocket):
    await gestor.conectar(ws)
    db = SessionLocal()
    try:
        # Al conectar, enviar alertas activas existentes
        alertas_activas = db.query(Alerta).filter(
            Alerta.resuelta == False
        ).order_by(Alerta.creada_en.desc()).limit(20).all()

        await ws.send_text(json.dumps({
            "evento": "alertas_iniciales",
            "alertas": [
                {
                    "id": a.id,
                    "tipo": a.tipo,
                    "severidad": a.severidad,
                    "mensaje": a.mensaje,
                    "detalle": a.detalle,
                    "creada_en": a.creada_en.isoformat()
                } for a in alertas_activas
            ]
        }, default=str))

        # Mantener conexión abierta
        while True:
            await ws.receive_text()

    except WebSocketDisconnect:
        gestor.desconectar(ws)
    finally:
        db.close()