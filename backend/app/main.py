from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse
from contextlib import asynccontextmanager
import asyncio
import os

from app.database import engine, Base
from app.routers import ordenes, maquinas, dashboard
from app.routers.alertas import router as alertas_router, tarea_monitoreo
from app.models import orden, maquina, defecto
from app.models.alerta import Alerta

Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicia el monitor de alertas en background al arrancar
    task = asyncio.create_task(tarea_monitoreo())
    yield
    task.cancel()


app = FastAPI(
    title="MES Honda Celaya",
    description="Sistema de Ejecución de Manufactura",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FRONTEND_DIR = os.path.join(BASE_DIR, "frontend")

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(FRONTEND_DIR, "static")),
    name="static"
)

templates = Jinja2Templates(directory=os.path.join(FRONTEND_DIR, "templates"))

app.include_router(ordenes.router)
app.include_router(maquinas.router)
app.include_router(dashboard.router)
app.include_router(alertas_router)


@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")