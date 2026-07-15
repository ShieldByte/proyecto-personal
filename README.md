# Proyecto MES

![Estado](https://img.shields.io/badge/Estado-Completado-brightgreen)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-green)
![Tests](https://img.shields.io/badge/Tests-11%20passed-brightgreen)
![Licencia](https://img.shields.io/badge/Licencia-MIT-green)

Sistema MES (Manufacturing Execution System) simplificado para monitoreo
en tiempo real de líneas de producción automotriz. Desarrollado como
proyecto de portafolio para aplicar a residencia profesional en planta
automotriz Honda de México, Celaya, Guanajuato.

---

## ¿Qué es un MES?

Un Manufacturing Execution System es el software que conecta el piso de
producción con los sistemas de gestión empresarial. Registra en tiempo
real lo que ocurre en cada estación de trabajo: unidades producidas,
defectos, paros y eficiencia. Honda utiliza sistemas MES en todas sus
plantas para garantizar los estándares de calidad Monozukuri.

---

## Funcionalidades implementadas

### Dashboard en tiempo real

- Gauge visual de OEE con actualización automática cada 15 segundos
- KPIs de producción: unidades objetivo, producidas, buenas y defectuosas
- Gráfica de historial OEE del turno
- Gráfica de producción por máquina (buenas vs defectuosas)

### Gestión de órdenes de producción

- Creación de órdenes con número, producto, turno y estación asignada
- Actualización de avance en tiempo real (unidades producidas y defectos)
- Trazabilidad de estado: Pendiente → En Proceso → Completada
- Barra de progreso con semáforo de cumplimiento

### Cálculo de OEE

Implementación de la fórmula estándar de manufactura de clase mundial:

```
OEE = Disponibilidad × Rendimiento × Calidad
```

| Indicador      | Fórmula                                         |
| -------------- | ----------------------------------------------- |
| Disponibilidad | (Tiempo operativo / Tiempo disponible) × 100    |
| Rendimiento    | (Unidades producidas / Unidades objetivo) × 100 |
| Calidad        | (Unidades buenas / Unidades producidas) × 100   |

| Clasificación | Rango OEE |
| ------------- | --------- |
| Clase Mundial | ≥ 85%     |
| Aceptable     | 65% – 84% |
| Regular       | 45% – 64% |
| Crítico       | < 45%     |

### Sistema de alertas automáticas

Monitor en background que evalúa reglas de negocio cada 30 segundos
y transmite alertas en tiempo real mediante WebSocket:

| Regla                      | Umbral Advertencia | Umbral Crítico |
| -------------------------- | ------------------ | -------------- |
| OEE Global                 | < 65%              | < 45%          |
| Tasa de defectos por orden | > 5%               | > 10%          |
| Calidad global             | < 90%              | —              |
| Orden sin actualización    | > 60 min           | —              |

### Reportes exportables por turno

- Selección de turno (Matutino / Vespertino / Nocturno) y fecha
- Previsualización de KPIs antes de exportar
- Exportación en **PDF** con diseño profesional Honda
- Exportación en **Excel** con 3 hojas: Resumen, Órdenes y Alertas

---

## Stack tecnológico

| Capa              | Tecnología                        |
| ----------------- | --------------------------------- |
| Backend           | Python 3.11 + FastAPI             |
| Base de datos     | SQLite (dev) → PostgreSQL (prod)  |
| ORM               | SQLAlchemy                        |
| Validación        | Pydantic v2                       |
| Frontend          | HTML5 + CSS3 + JavaScript vanilla |
| Tiempo real       | WebSockets nativos                |
| Exportación PDF   | ReportLab                         |
| Exportación Excel | OpenPyXL                          |
| Pruebas           | Pytest                            |

---

## Estructura del proyecto

```
proyecto-mes/
├── backend/
│   ├── app/
│   │   ├── main.py              # Punto de entrada FastAPI
│   │   ├── database.py          # Conexión SQLAlchemy
│   │   ├── models/              # Modelos de BD
│   │   │   ├── maquina.py
│   │   │   ├── orden.py
│   │   │   ├── defecto.py
│   │   │   └── alerta.py
│   │   ├── schemas/             # Validación Pydantic
│   │   │   └── orden.py
│   │   ├── routers/             # Endpoints REST
│   │   │   ├── maquinas.py
│   │   │   ├── ordenes.py
│   │   │   ├── dashboard.py
│   │   │   ├── alertas.py
│   │   │   └── reportes.py
│   │   └── services/            # Lógica de negocio
│   │       ├── oee.py
│   │       ├── monitor.py
│   │       ├── reporte.py
│   │       ├── pdf_generator.py
│   │       └── excel_generator.py
├── frontend/
│   ├── static/
│   │   ├── css/style.css
│   │   └── js/dashboard.js
│   └── templates/
│       └── index.html
├── docs/
│   └── arquitectura.md
├── tests/
│   └── test_oee.py
├── requirements.txt
└── README.md
```

---

## Instalación y ejecución local

### Requisitos

- Python 3.11+
- Git

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/ShieldByte/proyecto-mes.git
cd proyecto-mes

# 2. Crear y activar entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Levantar el servidor
cd backend
uvicorn app.main:app --reload

# 5. Abrir en el navegador
# Dashboard:        http://localhost:8000
# Documentación API: http://localhost:8000/docs
```

### Ejecutar pruebas

```bash
python -m pytest tests/ -v
```

---

## API REST

La documentación interactiva completa está disponible en
`http://localhost:8000/docs` al levantar el servidor.

| Método | Endpoint                   | Descripción            |
| ------ | -------------------------- | ---------------------- |
| GET    | `/maquinas/`               | Listar máquinas        |
| POST   | `/maquinas/`               | Crear máquina          |
| GET    | `/ordenes/`                | Listar órdenes         |
| POST   | `/ordenes/`                | Crear orden            |
| PATCH  | `/ordenes/{id}`            | Actualizar avance      |
| GET    | `/dashboard/resumen`       | KPIs globales          |
| GET    | `/alertas/`                | Listar alertas activas |
| PATCH  | `/alertas/{id}/resolver`   | Resolver alerta        |
| WS     | `/alertas/ws`              | WebSocket tiempo real  |
| GET    | `/reportes/turno`          | Datos del turno        |
| GET    | `/reportes/exportar/pdf`   | Descargar PDF          |
| GET    | `/reportes/exportar/excel` | Descargar Excel        |

---

## Roadmap

- [x] Modelos de datos y base de datos
- [x] API REST completa con documentación automática
- [x] Dashboard con OEE en tiempo real
- [x] Sistema de alertas con WebSocket
- [x] Reportes exportables PDF y Excel
- [x] Pruebas unitarias del motor OEE
- [ ] Migración a PostgreSQL
- [ ] Dockerización del proyecto
- [ ] Autenticación de usuarios por rol (Operador / Supervisor)
- [ ] Módulo de mantenimiento predictivo

---

## Autor

**Alex** — Estudiante de Ingeniería en Sistemas Computacionales  
TecNM / Instituto Tecnológico de Celaya  
GitHub: [@ShieldByte](https://github.com/ShieldByte)

---

> Proyecto desarrollado con el objetivo de aplicar a residencia profesional
> en Honda de México, Planta Celaya, Guanajuato.
> Demuestra conocimiento práctico de sistemas MES, industria 4.0,
> desarrollo web backend/frontend y principios de manufactura esbelta.
