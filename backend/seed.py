"""
Script de datos de prueba para Proyecto MES.
Genera datos realistas simulando una semana de producción.

Uso:
    cd backend
    python seed.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, date, timedelta
import random
from app.database import SessionLocal, engine, Base
from app.models.maquina import Maquina
from app.models.orden import Orden, EstadoOrden
from app.models.defecto import Defecto
from app.models.alerta import Alerta, TipoAlerta, SeveridadAlerta

# Importar todos los modelos para que SQLAlchemy los registre
from app.models import orden, maquina, defecto
from app.models.alerta import Alerta

Base.metadata.create_all(bind=engine)

# ── CONFIGURACIÓN ────────────────────────────────────────────
DIAS_ATRAS = 7          # Cuántos días de historial generar
ORDENES_POR_DIA = 6     # Órdenes por día (2 por turno)
SEED = 42               # Semilla para reproducibilidad
random.seed(SEED)

# ── DATOS MAESTROS ───────────────────────────────────────────
MAQUINAS = [
    {"codigo": "EST-SOL-01", "nombre": "Estación Soldadura Lateral",      "area": "Carrocería"},
    {"codigo": "EST-SOL-02", "nombre": "Estación Soldadura Frontal",      "area": "Carrocería"},
    {"codigo": "EST-PIN-01", "nombre": "Cabina de Pintura Base",          "area": "Pintura"},
    {"codigo": "EST-PIN-02", "nombre": "Cabina de Pintura Acabado",       "area": "Pintura"},
    {"codigo": "EST-ENS-01", "nombre": "Línea Ensamble Motor",            "area": "Ensamble"},
    {"codigo": "EST-ENS-02", "nombre": "Línea Ensamble Interior",         "area": "Ensamble"},
    {"codigo": "EST-ENS-03", "nombre": "Línea Ensamble Suspensión",       "area": "Ensamble"},
    {"codigo": "EST-CAL-01", "nombre": "Estación Control de Calidad",     "area": "Calidad"},
    {"codigo": "EST-LOG-01", "nombre": "Estación Logística de Salida",    "area": "Logística"},
]

PRODUCTOS = [
    "Acura ADX 2025 — Panel Lateral Derecho",
    "Acura ADX 2025 — Panel Lateral Izquierdo",
    "Acura ADX 2025 — Panel Frontal",
    "Acura ADX 2025 — Panel Trasero",
    "Acura ADX 2025 — Ensamble Motor V6",
    "Acura ADX 2025 — Ensamble Interior Cabina",
    "Acura ADX 2025 — Sistema Suspensión Delantera",
    "Acura ADX 2025 — Sistema Suspensión Trasera",
    "Acura ADX 2025 — Módulo Tablero Completo",
    "Honda CR-V 2025 — Carrocería Lateral",
    "Honda CR-V 2025 — Techo Panorámico",
    "Honda CR-V 2025 — Ensamble Transmisión",
    "Honda HR-V 2025 — Panel Puerta Delantera",
    "Honda HR-V 2025 — Ensamble Chasis",
]

TURNOS = ["Matutino", "Vespertino", "Nocturno"]

TIPOS_DEFECTO = [
    "Soldadura incompleta",
    "Porosidad en pintura",
    "Desalineación de panel",
    "Torque incorrecto en sujeción",
    "Rayón en superficie",
    "Burbuja en capa de pintura",
    "Dimensión fuera de tolerancia",
    "Falla en punto de soldadura",
    "Contaminación en pintura",
    "Imperfección en acabado",
]

# ── PERFILES DE RENDIMIENTO ──────────────────────────────────
# Cada máquina tiene un perfil de eficiencia realista
PERFILES = {
    "EST-SOL-01": {"base": 92, "variacion": 5,  "defecto_base": 2.0},
    "EST-SOL-02": {"base": 88, "variacion": 7,  "defecto_base": 2.5},
    "EST-PIN-01": {"base": 85, "variacion": 8,  "defecto_base": 3.5},
    "EST-PIN-02": {"base": 90, "variacion": 6,  "defecto_base": 3.0},
    "EST-ENS-01": {"base": 94, "variacion": 4,  "defecto_base": 1.5},
    "EST-ENS-02": {"base": 91, "variacion": 5,  "defecto_base": 2.0},
    "EST-ENS-03": {"base": 87, "variacion": 8,  "defecto_base": 2.8},
    "EST-CAL-01": {"base": 96, "variacion": 3,  "defecto_base": 0.5},
    "EST-LOG-01": {"base": 98, "variacion": 2,  "defecto_base": 0.2},
}

# ── HELPERS ──────────────────────────────────────────────────

def rendimiento_maquina(codigo: str) -> float:
    """Genera un rendimiento realista según el perfil de la máquina."""
    perfil = PERFILES.get(codigo, {"base": 88, "variacion": 8})
    valor = random.gauss(perfil["base"], perfil["variacion"] / 2)
    return max(50.0, min(100.0, valor))


def defectos_realistas(producidas: int, codigo: str) -> int:
    """Calcula defectos con distribución realista."""
    perfil = PERFILES.get(codigo, {"defecto_base": 3.0})
    pct = random.gauss(perfil["defecto_base"], 1.0)
    pct = max(0.0, min(15.0, pct))
    return max(0, round(producidas * pct / 100))


def numero_orden(dia_idx: int, turno: str, seq: int) -> str:
    fecha = date.today() - timedelta(days=dia_idx)
    turno_codigo = {"Matutino": "M", "Vespertino": "V", "Nocturno": "N"}[turno]
    return f"ORD-{fecha.strftime('%Y%m%d')}-{turno_codigo}{seq:02d}"


def fecha_turno(dia_idx: int, turno: str) -> datetime:
    """Retorna datetime de inicio del turno."""
    base = datetime.now() - timedelta(days=dia_idx)
    horas = {"Matutino": 6, "Vespertino": 14, "Nocturno": 22}[turno]
    return base.replace(hour=horas, minute=random.randint(0, 15),
                        second=0, microsecond=0)


def limpiar_bd(db):
    """Elimina todos los datos existentes antes de insertar."""
    print("Limpiando base de datos...")
    db.query(Defecto).delete()
    db.query(Alerta).delete()
    db.query(Orden).delete()
    db.query(Maquina).delete()
    db.commit()
    print("   [OK] Base de datos limpia")


# ── GENERADORES ──────────────────────────────────────────────

def crear_maquinas(db) -> list:
    print("\nCreando maquinas...")
    maquinas = []
    for datos in MAQUINAS:
        m = Maquina(**datos)
        db.add(m)
        maquinas.append(m)
    db.commit()
    for m in maquinas:
        db.refresh(m)
        print(f"   [OK] {m.codigo} — {m.nombre}")
    return maquinas


def crear_ordenes_y_defectos(db, maquinas: list) -> list:
    print(f"\nGenerando ordenes ({DIAS_ATRAS} dias x {ORDENES_POR_DIA} ordenes)...")
    ordenes_creadas = []
    seq_global = 1

    for dia_idx in range(DIAS_ATRAS, -1, -1):  # Del más antiguo al más reciente
        fecha_dia = date.today() - timedelta(days=dia_idx)

        # 2 órdenes por turno = 6 por día
        for turno in TURNOS:
            for seq in range(1, 3):
                maquina = random.choice(maquinas)
                perfil = PERFILES.get(maquina.codigo, {"base": 88})
                objetivo = random.randint(80, 150)

                # Determinar estado según antigüedad
                if dia_idx > 0:
                    # Días anteriores: todas completadas
                    estado = EstadoOrden.COMPLETADA
                    rend = rendimiento_maquina(maquina.codigo) / 100
                    producidas = round(objetivo * rend)
                    defectuosas = defectos_realistas(producidas, maquina.codigo)
                    inicio = fecha_turno(dia_idx, turno)
                    fin = inicio + timedelta(hours=7, minutes=random.randint(30, 59))
                elif turno == "Matutino":
                    # Hoy matutino: completadas o en proceso
                    if seq == 1:
                        estado = EstadoOrden.COMPLETADA
                        rend = rendimiento_maquina(maquina.codigo) / 100
                        producidas = round(objetivo * rend)
                        defectuosas = defectos_realistas(producidas, maquina.codigo)
                        inicio = fecha_turno(0, turno)
                        fin = inicio + timedelta(hours=3, minutes=30)
                    else:
                        estado = EstadoOrden.EN_PROCESO
                        rend = rendimiento_maquina(maquina.codigo) / 100 * 0.6
                        producidas = round(objetivo * rend)
                        defectuosas = defectos_realistas(producidas, maquina.codigo)
                        inicio = fecha_turno(0, turno)
                        fin = None
                elif turno == "Vespertino":
                    # Hoy vespertino: pendientes o en proceso
                    estado = random.choice([EstadoOrden.PENDIENTE, EstadoOrden.EN_PROCESO])
                    if estado == EstadoOrden.EN_PROCESO:
                        producidas = round(objetivo * random.uniform(0.1, 0.4))
                        defectuosas = defectos_realistas(producidas, maquina.codigo)
                        inicio = fecha_turno(0, turno)
                    else:
                        producidas = 0
                        defectuosas = 0
                        inicio = None
                    fin = None
                else:
                    # Nocturno de hoy: todas pendientes
                    estado = EstadoOrden.PENDIENTE
                    producidas = 0
                    defectuosas = 0
                    inicio = None
                    fin = None

                orden = Orden(
                    numero_orden=numero_orden(dia_idx, turno, seq_global),
                    producto=random.choice(PRODUCTOS),
                    unidades_objetivo=objetivo,
                    unidades_producidas=producidas,
                    unidades_defectuosas=defectuosas,
                    estado=estado,
                    turno=turno,
                    maquina_id=maquina.id,
                    fecha_inicio=inicio,
                    fecha_fin=fin,
                    creada_en=fecha_turno(dia_idx, turno) - timedelta(minutes=30)
                )
                db.add(orden)
                db.flush()

                # Crear defectos detallados para órdenes con defectos
                if defectuosas > 0 and estado != EstadoOrden.PENDIENTE:
                    num_tipos = random.randint(1, min(3, defectuosas))
                    defectos_restantes = defectuosas
                    for i in range(num_tipos):
                        cantidad = (defectos_restantes if i == num_tipos - 1
                                    else random.randint(1, max(1, defectos_restantes - 1)))
                        defectos_restantes -= cantidad
                        d = Defecto(
                            tipo=random.choice(TIPOS_DEFECTO),
                            descripcion=f"Detectado en inspección — estación {maquina.codigo}",
                            cantidad=cantidad,
                            orden_id=orden.id,
                            registrado_en=inicio + timedelta(
                                hours=random.randint(1, 5)
                            ) if inicio else datetime.utcnow()
                        )
                        db.add(d)
                        if defectos_restantes <= 0:
                            break

                ordenes_creadas.append(orden)
                seq_global += 1

    db.commit()
    print(f"   [OK] {len(ordenes_creadas)} ordenes creadas con sus defectos")
    return ordenes_creadas


def crear_alertas(db, ordenes: list):
    print("\nGenerando alertas historicas...")
    alertas_creadas = 0

    # Alertas de OEE bajo (días con bajo rendimiento)
    for dia_idx in range(DIAS_ATRAS, 0, -1):
        if random.random() < 0.3:  # 30% de días tienen alerta de OEE
            severidad = random.choice([
                SeveridadAlerta.ADVERTENCIA,
                SeveridadAlerta.CRITICA
            ])
            oee_val = random.uniform(38, 63) if severidad == SeveridadAlerta.CRITICA else random.uniform(55, 64)
            fecha_al = datetime.now() - timedelta(days=dia_idx,
                                                   hours=random.randint(1, 6))
            a = Alerta(
                tipo=TipoAlerta.OEE_BAJO,
                severidad=severidad,
                mensaje=f"OEE {'crítico' if severidad == SeveridadAlerta.CRITICA else 'bajo'}: {oee_val:.1f}%",
                detalle=f"Disponibilidad: {random.uniform(70,90):.1f}% | Rendimiento: {random.uniform(65,88):.1f}% | Calidad: {random.uniform(82,95):.1f}%",
                resuelta=True,
                creada_en=fecha_al,
                resuelta_en=fecha_al + timedelta(hours=random.randint(1, 3))
            )
            db.add(a)
            alertas_creadas += 1

    # Alertas de defectos por orden (órdenes con alta tasa de defectos)
    ordenes_con_defectos = [
        o for o in ordenes
        if o.unidades_producidas > 0
        and (o.unidades_defectuosas / o.unidades_producidas) > 0.05
    ]

    for orden in ordenes_con_defectos[:15]:  # Máximo 15 alertas de defectos
        pct = (orden.unidades_defectuosas / orden.unidades_producidas) * 100
        severidad = SeveridadAlerta.CRITICA if pct > 10 else SeveridadAlerta.ADVERTENCIA
        fecha_al = orden.creada_en + timedelta(hours=random.randint(1, 4))
        resuelta = orden.estado == EstadoOrden.COMPLETADA

        a = Alerta(
            tipo=TipoAlerta.DEFECTOS_ALTO,
            severidad=severidad,
            mensaje=f"Tasa de defectos {'crítica' if severidad == SeveridadAlerta.CRITICA else 'elevada'} en {orden.numero_orden}: {pct:.1f}%",
            detalle=f"{orden.unidades_defectuosas} defectos de {orden.unidades_producidas} unidades producidas.",
            resuelta=resuelta,
            orden_id=orden.id,
            creada_en=fecha_al,
            resuelta_en=fecha_al + timedelta(hours=1) if resuelta else None
        )
        db.add(a)
        alertas_creadas += 1

    # Alertas de calidad baja
    for _ in range(random.randint(2, 4)):
        dia = random.randint(1, DIAS_ATRAS)
        fecha_al = datetime.now() - timedelta(days=dia, hours=random.randint(0, 5))
        a = Alerta(
            tipo=TipoAlerta.CALIDAD_BAJA,
            severidad=SeveridadAlerta.ADVERTENCIA,
            mensaje=f"Calidad por debajo del estándar: {random.uniform(82, 89):.1f}%",
            detalle="Revisar proceso de inspección y estaciones con mayor índice de defectos.",
            resuelta=True,
            creada_en=fecha_al,
            resuelta_en=fecha_al + timedelta(minutes=random.randint(30, 120))
        )
        db.add(a)
        alertas_creadas += 1

    # Alertas de órdenes detenidas
    for _ in range(random.randint(3, 5)):
        dia = random.randint(1, DIAS_ATRAS)
        minutos = random.randint(65, 180)
        fecha_al = datetime.now() - timedelta(days=dia, hours=random.randint(1, 4))
        orden_ref = random.choice(ordenes)
        a = Alerta(
            tipo=TipoAlerta.ORDEN_DETENIDA,
            severidad=SeveridadAlerta.ADVERTENCIA,
            mensaje=f"Orden {orden_ref.numero_orden} sin actualización por {minutos} min",
            detalle="Verificar si la estación está operativa o si hay un paro no registrado.",
            resuelta=True,
            orden_id=orden_ref.id,
            creada_en=fecha_al,
            resuelta_en=fecha_al + timedelta(minutes=random.randint(15, 45))
        )
        db.add(a)
        alertas_creadas += 1

    # 2-3 alertas activas de hoy (sin resolver)
    for _ in range(random.randint(2, 3)):
        tipo = random.choice([TipoAlerta.OEE_BAJO, TipoAlerta.DEFECTOS_ALTO])
        severidad = random.choice([SeveridadAlerta.ADVERTENCIA, SeveridadAlerta.CRITICA])
        fecha_al = datetime.now() - timedelta(minutes=random.randint(5, 90))

        if tipo == TipoAlerta.OEE_BAJO:
            oee_val = random.uniform(40, 63)
            mensaje = f"OEE bajo: {oee_val:.1f}% (objetivo: ≥65%)"
            detalle = f"Disponibilidad: {random.uniform(70,85):.1f}% | Calidad: {random.uniform(85,92):.1f}%"
        else:
            pct = random.uniform(6, 14)
            orden_ref = random.choice([o for o in ordenes if o.estado == EstadoOrden.EN_PROCESO] or ordenes)
            mensaje = f"Defectos elevados en {orden_ref.numero_orden}: {pct:.1f}%"
            detalle = "Supera el umbral permitido de 5%. Requiere intervención."

        a = Alerta(
            tipo=tipo,
            severidad=severidad,
            mensaje=mensaje,
            detalle=detalle,
            resuelta=False,
            creada_en=fecha_al
        )
        db.add(a)
        alertas_creadas += 1

    db.commit()
    print(f"   [OK] {alertas_creadas} alertas generadas")


def imprimir_resumen(db):
    total_maquinas = db.query(Maquina).count()
    total_ordenes = db.query(Orden).count()
    completadas = db.query(Orden).filter(Orden.estado == EstadoOrden.COMPLETADA).count()
    en_proceso = db.query(Orden).filter(Orden.estado == EstadoOrden.EN_PROCESO).count()
    pendientes = db.query(Orden).filter(Orden.estado == EstadoOrden.PENDIENTE).count()
    total_defectos = db.query(Defecto).count()
    total_alertas = db.query(Alerta).count()
    alertas_activas = db.query(Alerta).filter(Alerta.resuelta == False).count()

    print("\n" + "═" * 50)
    print("  RESUMEN DE DATOS GENERADOS")
    print("═" * 50)
    print(f"  Maquinas/Estaciones : {total_maquinas}")
    print(f"  Ordenes totales     : {total_ordenes}")
    print(f"     Completadas       : {completadas}")
    print(f"     En proceso        : {en_proceso}")
    print(f"     Pendientes        : {pendientes}")
    print(f"  Registros defecto   : {total_defectos}")
    print(f"  Alertas totales     : {total_alertas}")
    print(f"     Activas           : {alertas_activas}")
    print("═" * 50)
    print("  Sistema listo para demostracion")
    print("═" * 50)


# ── MAIN ─────────────────────────────────────────────────────

def main():
    print("═" * 50)
    print("  Proyecto MES — Generador de datos")
    print("═" * 50)

    db = SessionLocal()
    try:
        limpiar_bd(db)
        maquinas = crear_maquinas(db)
        ordenes = crear_ordenes_y_defectos(db, maquinas)
        crear_alertas(db, ordenes)
        imprimir_resumen(db)

    except Exception as e:
        db.rollback()
        print(f"\nError: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()