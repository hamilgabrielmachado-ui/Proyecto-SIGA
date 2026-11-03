"""Exportación de reportes a PDF (ReportLab) y Excel (openpyxl)."""
from datetime import datetime


def exportar_pdf(reporte, ruta, usuario=""):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    estilos = getSampleStyleSheet()
    doc = SimpleDocTemplate(str(ruta), pagesize=landscape(A4), leftMargin=1.5 * cm, rightMargin=1.5 * cm,
                            topMargin=1.5 * cm, bottomMargin=1.5 * cm, title=reporte.titulo)
    elementos = [Paragraph(reporte.titulo, estilos["Title"])]
    sub = f"Generado el {datetime.now():%Y-%m-%d %H:%M}" + (f" por {usuario}" if usuario else "")
    elementos += [Paragraph(sub, estilos["Normal"]), Spacer(1, 0.3 * cm)]
    if reporte.resumen:
        elementos += [Paragraph(reporte.resumen, estilos["Normal"]), Spacer(1, 0.3 * cm)]
    if reporte.filas:
        celda = estilos["BodyText"]
        celda.fontSize = 8
        datos = [[Paragraph(f"<b>{c}</b>", celda) for c in reporte.columnas]]
        datos += [[Paragraph(str(v if v is not None else ""), celda) for v in fila] for fila in reporte.filas]
        tabla = Table(datos, repeatRows=1)
        tabla.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#DCE6F5")),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#B8C2D3")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F6F8FB")]),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
        elementos.append(tabla)
    else:
        elementos.append(Paragraph("No hay datos para los filtros seleccionados.", estilos["Normal"]))
    doc.build(elementos)


def exportar_excel(reporte, ruta, usuario=""):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill

    wb = Workbook()
    ws = wb.active
    ws.title = "Reporte"[:31]
    ws.append([reporte.titulo])
    ws["A1"].font = Font(bold=True, size=14)
    ws.append([f"Generado el {datetime.now():%Y-%m-%d %H:%M}" + (f" por {usuario}" if usuario else "")])
    if reporte.resumen:
        ws.append([reporte.resumen])
    ws.append([])
    fila_enc = ws.max_row + 1
    ws.append(reporte.columnas)
    for c in ws[fila_enc]:
        c.font = Font(bold=True)
        c.fill = PatternFill("solid", fgColor="DCE6F5")
        c.alignment = Alignment(horizontal="center")
    for fila in reporte.filas:
        ws.append([("" if v is None else v) for v in fila])
    for i, col in enumerate(ws.iter_cols(min_row=fila_enc), start=1):
        ancho = max((len(str(c.value)) for c in col if c.value is not None), default=8)
        ws.column_dimensions[ws.cell(row=fila_enc, column=i).column_letter].width = min(max(ancho + 2, 10), 50)
    wb.save(str(ruta))
