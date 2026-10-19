"""Acta imprimible de la entrega fisica, con espacios para ambas firmas."""
from io import BytesIO
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph


def generar_acta_pdf(datos):
    salida = BytesIO()
    ancho, alto = A4
    pdf = canvas.Canvas(salida, pagesize=A4, pageCompression=0)
    pdf.setTitle('Acta de conformidad - materiales')
    pdf.setAuthor('Escuela Militar de Ingeniería')
    margen = 58
    logo = Path(__file__).resolve().parents[2] / 'frontend/public/img/emi.jpg'
    if logo.exists():
        pdf.drawImage(ImageReader(str(logo)), margen, alto - 120, width=54, height=62, preserveAspectRatio=True, mask='auto')
    pdf.setFillColor(colors.HexColor('#17629a'))
    pdf.setFont('Helvetica-Bold', 29)
    pdf.drawString(margen + 63, alto - 85, 'EMI')
    pdf.setFont('Helvetica-Bold', 6.7)
    pdf.drawString(margen + 63, alto - 98, 'ESCUELA MILITAR DE INGENIERÍA')
    pdf.setFont('Helvetica', 6.5)
    pdf.drawString(margen + 63, alto - 110, 'Unidad Académica - Santa Cruz')
    pdf.setFillColor(colors.black)
    titulo = ParagraphStyle('titulo', fontName='Helvetica-Bold', fontSize=14, leading=19, alignment=TA_CENTER)
    cuerpo = ParagraphStyle('cuerpo', fontName='Helvetica', fontSize=11, leading=18, alignment=TA_JUSTIFY)
    y = alto - 182
    p = Paragraph('ACTA DE CONFORMIDAD-MATERIALES', titulo)
    _, h = p.wrap(ancho - 2 * margen, alto)
    p.drawOn(pdf, margen, y - h)
    y -= h + 27
    fecha, _, hora = datos['fecha'].partition(' ')
    descripcion = datos.get('especificaciones') or datos.get('descripcion') or ''
    texto = (f"En la ciudad de Santa Cruz, a horas {escape(hora)}, de fecha {escape(fecha)}, "
             f"se realizó la entrega y recepción de <b>{escape(str(datos['cantidad_entregada']))} "
             f"unidad(es) de {escape(datos['titulo'])}</b>, correspondiente al pedido "
             f"<b>{escape(datos['codigo'])}</b>, con las características requeridas.")
    parrafos = [texto]
    if descripcion:
        parrafos.append('Características del material: ' + escape(descripcion))
    if datos.get('observaciones'):
        parrafos.append('Observaciones de entrega: ' + escape(datos['observaciones']))
    parrafos.append('Para tal efecto, y en señal de conformidad, se procede a la firma del presente documento por el encargado de almacenes que entrega y el receptor del material.')
    def nueva_pagina():
        pdf.setFont('Helvetica', 7)
        pdf.setFillColor(colors.HexColor('#666666'))
        pdf.drawString(margen, 38, 'Referencia: ' + datos['referencia'])
        pdf.showPage()
        pdf.setFillColor(colors.black)
        pdf.setFont('Helvetica-Bold', 10)
        pdf.drawString(margen, alto - 40, 'ACTA DE CONFORMIDAD-MATERIALES')
        return alto - 70

    for texto in parrafos:
        pendientes = [Paragraph(texto, cuerpo)]
        while pendientes:
            p = pendientes.pop(0)
            _, h = p.wrap(ancho - 2 * margen, alto)
            if y - h < 205:
                partes = p.split(ancho - 2 * margen, max(0, y - 205))
                if not partes:
                    y = nueva_pagina()
                    pendientes.insert(0, p)
                    continue
                p = partes[0]
                _, h = p.wrap(ancho - 2 * margen, alto)
                pendientes = partes[1:] + pendientes
            p.drawOn(pdf, margen, y - h)
            y -= h + 13
            if pendientes:
                y = nueva_pagina()
    if y < 250:
        y = nueva_pagina()
    firma_y = y - 115
    for centro, nombre, accion, cargo in [
        (ancho * .29, datos['entrega'], 'ENTREGUÉ CONFORME', 'ENCARGADO DE ALMACENES'),
        (ancho * .71, datos['recibe'], 'RECIBÍ CONFORME', 'TÉCNICO RECEPTOR' if datos.get('tipo_receptor') == 'Tecnico' else 'RECEPTOR DEL MATERIAL'),
    ]:
        pdf.setStrokeColor(colors.black)
        pdf.setDash(1, 2)
        pdf.line(centro - 98, firma_y, centro + 98, firma_y)
        pdf.setDash()
        pdf.setFont('Helvetica', 10)
        pdf.drawCentredString(centro, firma_y - 18, accion)
        pdf.setFont('Helvetica', 9)
        pdf.drawCentredString(centro, firma_y - 33, cargo)
        nombre_p = Paragraph(escape(nombre), ParagraphStyle('nombre', fontName='Helvetica', fontSize=9, leading=12, alignment=TA_CENTER))
        _, h = nombre_p.wrap(210, 100)
        nombre_p.drawOn(pdf, centro - 105, firma_y - 48 - h)
    pdf.setFont('Helvetica', 7)
    pdf.setFillColor(colors.HexColor('#666666'))
    pdf.drawString(margen, 53, f"Proveedor: {datos.get('proveedor', '')} - Bs. {datos.get('monto_real', '')}")
    pdf.drawString(margen, 38, 'Referencia: ' + datos['referencia'])
    pdf.save()
    return salida.getvalue()
