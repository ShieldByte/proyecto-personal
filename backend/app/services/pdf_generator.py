from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table,
    TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from io import BytesIO


# ── Paleta de colores Honda ──────────────────────────────────
HONDA_RED   = colors.HexColor("#CC0000")
HONDA_DARK  = colors.HexColor("#1a1a2e")
GRAY_LIGHT  = colors.HexColor("#f5f5f5")
GRAY_MID    = colors.HexColor("#e0e0e0")
GREEN       = colors.HexColor("#00a878")
ORANGE      = colors.HexColor("#f4a261")
TEXT_DARK   = colors.HexColor("#1a1a2e")
TEXT_GRAY   = colors.HexColor("#666666")


def generar_pdf(datos: dict) -> bytes:
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=1.5*cm,
        leftMargin=1.5*cm,
        topMargin=1.5*cm,
        bottomMargin=1.5*cm
    )

    estilos = getSampleStyleSheet()
    historia = []

    # ── ENCABEZADO ───────────────────────────────────────────
    estilo_titulo = ParagraphStyle(
        "titulo",
        fontSize=20,
        textColor=colors.white,
        alignment=TA_LEFT,
        fontName="Helvetica-Bold",
        leading=24
    )
    estilo_sub = ParagraphStyle(
        "sub",
        fontSize=10,
        textColor=colors.HexColor("#cccccc"),
        alignment=TA_LEFT,
        fontName="Helvetica",
    )

    encabezado_data = [[
        Paragraph("MES Honda Celaya", estilo_titulo),
        Paragraph(
            f"Generado: {datos['fecha_generacion']}",
            ParagraphStyle("gen", fontSize=8, textColor=colors.HexColor("#aaaaaa"),
                           alignment=TA_RIGHT, fontName="Helvetica")
        )
    ]]

    tabla_enc = Table(encabezado_data, colWidths=[12*cm, 5*cm])
    tabla_enc.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), HONDA_DARK),
        ("ROWPADDING",    (0, 0), (-1, -1), 14),
        ("ROUNDEDCORNERS", [6]),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    historia.append(tabla_enc)
    historia.append(Spacer(1, 0.4*cm))

    # Subtítulo de turno
    historia.append(Paragraph(
        f"Reporte de Turno {datos['turno']}  ·  {datos['fecha']}",
        ParagraphStyle("turno", fontSize=13, textColor=HONDA_RED,
                       fontName="Helvetica-Bold", spaceAfter=4)
    ))
    historia.append(HRFlowable(width="100%", thickness=2,
                                color=HONDA_RED, spaceAfter=12))

    # ── KPIs PRINCIPALES ────────────────────────────────────
    t = datos["totales"]
    oee = datos["oee"]

    kpi_data = [
        ["MÉTRICA", "VALOR", "MÉTRICA", "VALOR"],
        ["Unidades Objetivo",    str(t["objetivo"]),
         "OEE Global",          f"{oee['oee']}%"],
        ["Unidades Producidas",  str(t["producidas"]),
         "Disponibilidad",      f"{oee['disponibilidad']}%"],
        ["Unidades Buenas",      str(t["buenas"]),
         "Rendimiento",         f"{oee['rendimiento']}%"],
        ["Unidades Defectuosas", str(t["defectuosas"]),
         "Calidad",             f"{oee['calidad']}%"],
        ["Cumplimiento",         f"{t['cumplimiento']}%",
         "Clasificación OEE",   oee["clasificacion"]],
    ]

    col_w = [5*cm, 3*cm, 5*cm, 3*cm]
    tabla_kpi = Table(kpi_data, colWidths=col_w)
    tabla_kpi.setStyle(TableStyle([
        # Encabezado
        ("BACKGROUND",   (0, 0), (-1, 0), HONDA_DARK),
        ("TEXTCOLOR",    (0, 0), (-1, 0), colors.white),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0), 8),
        ("ALIGN",        (0, 0), (-1, 0), "CENTER"),
        # Filas alternas
        ("BACKGROUND",   (0, 1), (-1, -1), GRAY_LIGHT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [GRAY_LIGHT, colors.white]),
        # Columnas de etiqueta
        ("FONTNAME",     (0, 1), (0, -1), "Helvetica-Bold"),
        ("FONTNAME",     (2, 1), (2, -1), "Helvetica-Bold"),
        ("TEXTCOLOR",    (0, 1), (0, -1), TEXT_DARK),
        ("TEXTCOLOR",    (2, 1), (2, -1), TEXT_DARK),
        # Columnas de valor
        ("TEXTCOLOR",    (1, 1), (1, -1), HONDA_RED),
        ("TEXTCOLOR",    (3, 1), (3, -1), HONDA_RED),
        ("FONTNAME",     (1, 1), (1, -1), "Helvetica-Bold"),
        ("FONTNAME",     (3, 1), (3, -1), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 1), (-1, -1), 9),
        ("ALIGN",        (1, 1), (1, -1), "CENTER"),
        ("ALIGN",        (3, 1), (3, -1), "CENTER"),
        ("ROWPADDING",   (0, 0), (-1, -1), 7),
        ("GRID",         (0, 0), (-1, -1), 0.5, GRAY_MID),
        ("ROUNDEDCORNERS", [4]),
    ]))
    historia.append(tabla_kpi)
    historia.append(Spacer(1, 0.5*cm))

    # ── TABLA DE ÓRDENES ────────────────────────────────────
    historia.append(Paragraph(
        "Detalle de Órdenes de Producción",
        ParagraphStyle("sec", fontSize=11, fontName="Helvetica-Bold",
                       textColor=HONDA_DARK, spaceBefore=8, spaceAfter=6)
    ))

    if datos["ordenes"]:
        enc_ord = ["N° Orden", "Producto", "Estado",
                   "Objetivo", "Producidas", "Buenas", "Defect.", "Cumpl.%"]
        filas_ord = [enc_ord]

        for o in datos["ordenes"]:
            # Truncar texto largo
            producto = (o["producto"][:28] + "…") if len(o["producto"]) > 30 else o["producto"]
            filas_ord.append([
                o["numero_orden"],
                producto,
                o["estado"].replace("_", " ").title(),
                str(o["unidades_objetivo"]),
                str(o["unidades_producidas"]),
                str(o["unidades_buenas"]),
                str(o["unidades_defectuosas"]),
                f"{o['cumplimiento']}%",
            ])

        col_w_ord = [3*cm, 4.5*cm, 2.2*cm, 1.5*cm, 1.8*cm, 1.5*cm, 1.5*cm, 1.5*cm]
        tabla_ord = Table(filas_ord, colWidths=col_w_ord)

        # Colorear fila según cumplimiento
        estilos_ord = [
            ("BACKGROUND",  (0, 0), (-1, 0), HONDA_DARK),
            ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, -1), 8),
            ("ALIGN",       (3, 0), (-1, -1), "CENTER"),
            ("ROWPADDING",  (0, 0), (-1, -1), 6),
            ("GRID",        (0, 0), (-1, -1), 0.5, GRAY_MID),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [GRAY_LIGHT, colors.white]),
        ]

        # Colorear cumplimiento por semáforo
        for i, o in enumerate(datos["ordenes"], start=1):
            c = o["cumplimiento"]
            color_fila = GREEN if c >= 90 else (ORANGE if c >= 60 else HONDA_RED)
            estilos_ord.append(("TEXTCOLOR", (7, i), (7, i), color_fila))
            estilos_ord.append(("FONTNAME",  (7, i), (7, i), "Helvetica-Bold"))

        tabla_ord.setStyle(TableStyle(estilos_ord))
        historia.append(tabla_ord)
    else:
        historia.append(Paragraph(
            "No hay órdenes registradas para este turno.",
            ParagraphStyle("vacio", fontSize=9, textColor=TEXT_GRAY,
                           alignment=TA_CENTER)
        ))

    historia.append(Spacer(1, 0.5*cm))

    # ── ALERTAS DEL TURNO ───────────────────────────────────
    historia.append(Paragraph(
        "Alertas Registradas en el Turno",
        ParagraphStyle("sec2", fontSize=11, fontName="Helvetica-Bold",
                       textColor=HONDA_DARK, spaceBefore=8, spaceAfter=6)
    ))

    if datos["alertas"]:
        enc_al = ["Hora", "Severidad", "Tipo", "Mensaje", "Estado"]
        filas_al = [enc_al]
        for a in datos["alertas"]:
            filas_al.append([
                a["hora"],
                a["severidad"].title(),
                a["tipo"].replace("_", " ").title(),
                (a["mensaje"][:55] + "…") if len(a["mensaje"]) > 57 else a["mensaje"],
                "Resuelta" if a["resuelta"] else "Activa",
            ])

        col_w_al = [1.5*cm, 2.5*cm, 3*cm, 8*cm, 2*cm]
        tabla_al = Table(filas_al, colWidths=col_w_al)
        tabla_al.setStyle(TableStyle([
            ("BACKGROUND",  (0, 0), (-1, 0), HONDA_DARK),
            ("TEXTCOLOR",   (0, 0), (-1, 0), colors.white),
            ("FONTNAME",    (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",    (0, 0), (-1, -1), 8),
            ("ROWPADDING",  (0, 0), (-1, -1), 6),
            ("GRID",        (0, 0), (-1, -1), 0.5, GRAY_MID),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [GRAY_LIGHT, colors.white]),
        ]))
        historia.append(tabla_al)
    else:
        historia.append(Paragraph(
            "Sin alertas registradas en este turno.",
            ParagraphStyle("vacio2", fontSize=9, textColor=TEXT_GRAY,
                           alignment=TA_CENTER)
        ))

    # ── PIE DE PÁGINA ────────────────────────────────────────
    historia.append(Spacer(1, 0.8*cm))
    historia.append(HRFlowable(width="100%", thickness=1,
                                color=GRAY_MID, spaceAfter=8))
    historia.append(Paragraph(
        f"MES Honda Celaya  ·  Reporte generado automáticamente  ·  {datos['fecha_generacion']}",
        ParagraphStyle("pie", fontSize=7, textColor=TEXT_GRAY,
                       alignment=TA_CENTER)
    ))

    doc.build(historia)
    return buffer.getvalue()