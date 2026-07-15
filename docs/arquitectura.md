# Arquitectura del Sistema MES Honda Celaya

## Diagrama General

┌────────────────────────────────────────────────────────────┐
│ CLIENTE │
│ Navegador Web (HTML/CSS/JS) │
│ │
│ ┌─────────────┐ ┌──────────────┐ ┌───────────────────┐ │
│ │ Dashboard │ │ Órdenes │ │ Reportes/Alertas │ │
│ │ OEE Gauge │ │ CRUD Table │ │ PDF / Excel │ │
│ └──────┬──────┘ └──────┬───────┘ └────────┬──────────┘ │
└─────────┼────────────────┼───────────────────┼─────────────┘
│ HTTP REST │ HTTP REST │ WebSocket
┌─────────▼────────────────▼───────────────────▼─────────────┐
│ BACKEND (FastAPI) │
│ │
│ /maquinas /ordenes /dashboard /alertas /reportes │
│ │
│ ┌──────────────┐ ┌───────────────┐ ┌─────────────────┐ │
│ │ Routers │ │ Services │ │ WS Manager │ │
│ │ REST API │ │ OEE / Mon. │ │ Broadcast │ │
│ └──────┬───────┘ └───────┬───────┘ └────────┬────────┘ │
└─────────┼──────────────────┼───────────────────┼───────────┘
│ SQLAlchemy ORM │ │ Async task
┌─────────▼──────────────────▼───────────────────▼───────────┐
│ BASE DE DATOS (SQLite) │
│ │
│ maquinas │ ordenes │ defectos │ alertas │
└────────────────────────────────────────────────────────────┘

## Flujo de datos

1. El operador registra una orden desde el dashboard
2. FastAPI valida los datos con Pydantic y los persiste en SQLite
3. El monitor en background evalúa umbrales cada 30 segundos
4. Si se viola un umbral, crea una alerta y la transmite por WebSocket
5. El frontend recibe la alerta en tiempo real sin recargar la página
6. Al finalizar el turno, el supervisor exporta el reporte en PDF o Excel

## Tecnologías

| Capa          | Tecnología              | Justificación                                      |
| ------------- | ----------------------- | -------------------------------------------------- |
| Backend       | Python 3.11 + FastAPI   | Alto rendimiento, documentación automática         |
| ORM           | SQLAlchemy              | Abstracción de BD, migración futura a PostgreSQL   |
| Base de datos | SQLite → PostgreSQL     | SQLite para desarrollo, PostgreSQL para producción |
| Frontend      | HTML + CSS + JS vanilla | Sin dependencias, máximo control                   |
| Tiempo real   | WebSockets nativos      | Alertas instantáneas sin polling                   |
| Exportación   | ReportLab + OpenPyXL    | PDFs y Excel profesionales                         |
| Despliegue    | Docker (fase siguiente) | Portabilidad entre entornos                        |

## Módulos del sistema

### 1. Gestión de Máquinas

Catálogo de estaciones de trabajo con código, nombre y área.

### 2. Órdenes de Producción

CRUD completo con trazabilidad de estado: Pendiente → En Proceso → Completada.

### 3. Cálculo de OEE

Implementación de la fórmula estándar de manufactura:

- **Disponibilidad** = (Tiempo operativo / Tiempo disponible) × 100
- **Rendimiento** = (Unidades producidas / Unidades objetivo) × 100
- **Calidad** = (Unidades buenas / Unidades producidas) × 100
- **OEE** = Disponibilidad × Rendimiento × Calidad

### 4. Sistema de Alertas

Monitor en background con 5 reglas de negocio:

- OEE global por debajo del umbral (crítico < 45%, advertencia < 65%)
- Tasa de defectos por orden elevada (crítico > 10%, advertencia > 5%)
- Calidad global por debajo del 90%
- Órdenes en proceso sin actualización por más de 60 minutos

### 5. Reportes por Turno

Generación de reportes en PDF y Excel con:

- KPIs de producción y OEE
- Detalle por orden con semáforo de cumplimiento
- Historial de alertas del turno
