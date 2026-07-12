from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os

from app.database import engine, Base
from app.routers import ordenes, maquinas, dashboard

# Importar modelos para que SQLAlchemy los registre
from app.models import orden, maquina, defecto

# Crear tablas en la BD al iniciar
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="MES Honda Celaya",
    description="Sistema de Ejecución de Manufactura — Monitoreo de línea de producción",
    version="1.0.0",
)

# CORS para que el frontend pueda consumir la API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar routers
app.include_router(ordenes.router)
app.include_router(maquinas.router)
app.include_router(dashboard.router)


@app.get("/", tags=["Root"])
def root():
    return {
        "sistema": "MES Honda Celaya",
        "version": "1.0.0",
        "estado": "operativo",
        "docs": "/docs"
    }