"""PDF institucional liviano para los informes del flujo de Soporte UTIC."""

from datetime import datetime
from pathlib import Path
from textwrap import wrap
from django.conf import settings

AZUL = (0.071, 0.227, 0.420)
AZUL_CLARO = (0.941, 0.965, 0.988)
AMARILLO = (1.0, 0.780, 0.173)
GRIS = (0.365, 0.443, 0.522)
BORDE = (0.780, 0.831, 0.890)


def _logo_jpeg():
    """Devuelve el escudo institucional y sus dimensiones sin usar Pillow."""
    ruta = Path(__file__).resolve().parents[2] / "frontend" / "public" / "img" / "emi.jpg"
    if not ruta.exists():
        return None
    datos = ruta.read_bytes()
    indice = 2
    while indice + 9 < len(datos):
        if datos[indice] != 0xFF:
            indice += 1
            continue
        marcador = datos[indice + 1]
        if marcador in range(0xC0, 0xC4):
            alto = int.from_bytes(datos[indice + 5:indice + 7], "big")
            ancho = int.from_bytes(datos[indice + 7:indice + 9], "big")
            return datos, ancho, alto
        if indice + 4 > len(datos):
            break
        longitud = int.from_bytes(datos[indice + 2:indice + 4], "big")
        indice += 2 + max(longitud, 2)
    return None


def _texto(valor):
    return str(valor).strip() if valor not in (None, "") else "Sin registro"


def _pdf_text(valor):
    salida = []
    for byte in _texto(valor).encode("cp1252", "replace"):
        caracter = chr(byte)
        if caracter in "\\()":
            salida.append("\\" + caracter)
        elif byte < 32 or byte > 126:
            salida.append(f"\\{byte:03o}")
        else:
            salida.append(caracter)
    return "".join(salida)


def _lineas(valor, ancho=92):
    resultado = []
    for parrafo in _texto(valor).splitlines() or ["Sin registro"]:
        resultado.extend(wrap(parrafo, width=ancho, break_long_words=False) or [""])
    return resultado


def _fecha(valor=None):
    try:
        return (valor or datetime.now()).strftime("%d/%m/%Y")
    except AttributeError:
        return _texto(valor)


def _nombre(persona):
    if not persona:
        return "Sin registro"
    valor = getattr(persona, "nombre_completo", None)
    if not valor and hasattr(persona, "get_full_name"):
        valor = persona.get_full_name()
    return _texto(valor)


def _datos_compra(ticket):
    if not ticket.codigo_compra_vinculada:
        return None
    try:
        from compras.models import SolicitudCompra
        solicitud = SolicitudCompra.objects.filter(codigo=ticket.codigo_compra_vinculada).first()
    except Exception:
        solicitud = None
    if not solicitud:
        return None
    monto = solicitud.monto_real or solicitud.monto_desembolsado or solicitud.monto_estimado
    return solicitud.get_estado_display(), monto


def _documento_pdf(titulo, subtitulo, ticket, secciones, meta, compra=None, firma=None, firmante=None, unidad=None, firmas=None, espaciado=False):
    paginas, pagina, y = [], [], 790
    modulo = getattr(getattr(ticket, '_meta', None), 'app_label', '')
    unidad = unidad or {'mantenimiento': 'MANTENIMIENTO', 'compras': 'COMPRAS Y ALMACÉN'}.get(modulo, 'UNIDAD DE TECNOLOGÍAS DE INFORMACIÓN Y COMUNICACIÓN')

    def color(rgb, trazo=False):
        pagina.append(f"{rgb[0]} {rgb[1]} {rgb[2]} {'RG' if trazo else 'rg'}")

    def rect(x, abajo, ancho, alto, relleno=None, borde=None):
        if relleno:
            color(relleno)
        if borde:
            color(borde, True)
        pagina.append(f"{x} {abajo} {ancho} {alto} re {'B' if relleno and borde else 'f' if relleno else 'S'}")

    def texto(x, arriba, valor, tamano=9, negrita=False, rgb=(0.09, 0.18, 0.29)):
        color(rgb)
        pagina.append(f"BT /{'F2' if negrita else 'F1'} {tamano} Tf {x} {arriba} Td ({_pdf_text(valor)}) Tj ET")

    def encabezado(continuacion=False):
        nonlocal pagina, y
        pagina = []
        rect(42, 756, 511, 58, AZUL)
        rect(51, 766, 45, 38, (1, 1, 1))
        pagina.append("q 43 0 0 36 52 767 cm /Logo Do Q")
        texto(112, 796, getattr(settings, 'SIA_INSTITUCION', 'ESCUELA MILITAR DE INGENIERÍA'), 11, True, (1, 1, 1))
        texto(112, 781, getattr(settings, 'SIA_SUBTITULO_INSTITUCION', 'MCAL. ANTONIO JOSÉ DE SUCRE  ·  BOLIVIA'), 7.5, False, (1, 1, 1))
        texto(112, 768, unidad, 7.5, False, AMARILLO)
        y = 735
        nombre = titulo + (" · CONTINUACIÓN" if continuacion else "")
        texto(max(55, 297 - len(nombre) * 3.7), y, nombre, 15, True, AZUL)
        y -= 18
        texto(max(70, 297 - len(subtitulo) * 2.6), y, subtitulo, 9, False, GRIS)
        y -= 24

    def nueva_pagina():
        if pagina:
            paginas.append(pagina.copy())
        encabezado(bool(paginas))

    def asegurar(alto):
        if y - alto < 72:
            nueva_pagina()

    def bloque_titulo(etiqueta):
        nonlocal y
        asegurar(80 if espaciado else 32)
        rect(42, y - 19, 511, 23, AZUL_CLARO, BORDE)
        rect(42, y - 19, 5, 23, AMARILLO)
        texto(54, y - 11, etiqueta, 9, True, AZUL)
        y -= 31

    def campo(etiqueta, valor):
        nonlocal y
        lineas = _lineas(valor)
        paso = 16 if espaciado else 12
        alto = (32 if espaciado else 20) + max(0, len(lineas) - 1) * paso
        asegurar(alto + 7)
        texto(49, y, etiqueta.upper(), 7, True, GRIS)
        for indice, linea in enumerate(lineas):
            texto(49, y - paso - indice * paso, linea, 9)
        y -= alto
        color(BORDE, True)
        pagina.append(f"49 {y + 5} m 546 {y + 5} l S")

    encabezado()
    for indice in range(0, len(meta), 2):
        for col, (etiqueta, valor) in enumerate(meta[indice:indice + 2]):
            x = 42 + col * 255.5
            rect(x, y - 25, 255.5, 28, (0.985, 0.990, 0.996), BORDE)
            texto(x + 9, y - 8, etiqueta.upper(), 6.8, True, GRIS)
            texto(x + 9, y - 20, valor, 8.7, True, AZUL)
        y -= 28
    y -= 12
    for numero, (nombre, campos) in enumerate(secciones, 1):
        bloque_titulo(f"{numero}. {nombre}")
        for etiqueta, valor in campos:
            campo(etiqueta, valor)
    if compra:
        bloque_titulo("ANEXO · REQUERIMIENTO DE COMPRA")
        for etiqueta, valor in compra:
            campo(etiqueta, valor)
    firmas = list(firmas or [])
    if firma:
        firmas.append((firma, firmante, 'Firma electrónica manuscrita'))
    for inicio in range(0, len(firmas), 2):
        asegurar(150)
        for columna, (trazos, nombre, cargo) in enumerate(firmas[inicio:inicio + 2]):
            x_base = 80 if len(firmas) == 1 else 55 + columna * 255
            escala = .45 if len(firmas) == 1 else .37
            color(AZUL, True)
            pagina.append('1.3 w')
            for trazo in trazos:
                puntos = [(x_base + x * escala, y - 95 + (200 - yy) * .35) for x, yy in trazo]
                pagina.append(f'{puntos[0][0]:.2f} {puntos[0][1]:.2f} m')
                pagina.extend(f'{x:.2f} {yy:.2f} l' for x, yy in puntos[1:])
                pagina.append('S')
            pagina.append(f'{x_base} {y - 102} m {x_base + 220} {y - 102} l S')
            texto(x_base, y - 116, cargo, 8, True, AZUL)
            for indice, linea in enumerate(_lineas(nombre, 42)):
                texto(x_base, y - 130 - indice * 11, linea, 8, False, GRIS)
        y -= 150
    if not firmas:
        asegurar(105)
        texto(49, y - 15, 'Emisión registrada en SIA; firmas disponibles en el expediente cuando correspondan.', 8, False, GRIS)
    # Las firmas guardadas se dibujan únicamente cuando pertenecen a este documento.
    paginas.append(pagina.copy())
    return _serializar_paginas(paginas, ticket)


def _serializar_paginas(paginas, ticket):

    objetos = []
    def agregar(contenido):
        objetos.append(contenido)
        return len(objetos)
    catalogo, arbol = agregar(b""), agregar(b"")
    f1 = agregar(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica /Encoding /WinAnsiEncoding >>")
    f2 = agregar(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold /Encoding /WinAnsiEncoding >>")
    logo = _logo_jpeg()
    logo_id = None
    if logo:
        datos_logo, ancho_logo, alto_logo = logo
        logo_id = agregar(
            f"<< /Type /XObject /Subtype /Image /Width {ancho_logo} /Height {alto_logo} /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length {len(datos_logo)} >>\nstream\n".encode()
            + datos_logo + b"\nendstream"
        )
    else:
        # Un píxel blanco mantiene válida la referencia /Logo del encabezado.
        datos_logo = b"\xff\xd8\xff\xdb\x00C" + b"\x08" * 65 + b"\xff\xd9"
        logo_id = agregar(f"<< /Type /XObject /Subtype /Image /Width 1 /Height 1 /ColorSpace /DeviceRGB /BitsPerComponent 8 /Filter /DCTDecode /Length {len(datos_logo)} >>\nstream\n".encode() + datos_logo + b"\nendstream")
    ids = []
    for numero, comandos in enumerate(paginas, 1):
        pie = f"BT /F1 7 Tf 42 36 Td (SIA - Expediente {_pdf_text(ticket.codigo)}) Tj ET BT /F1 7 Tf 500 36 Td (Página {numero} de {len(paginas)}) Tj ET"
        flujo = ("\n".join(comandos) + "\n" + pie).encode("latin-1")
        contenido = agregar(b"<< /Length %d >>\nstream\n" % len(flujo) + flujo + b"\nendstream")
        ids.append(agregar(f"<< /Type /Page /Parent {arbol} 0 R /MediaBox [0 0 595 842] /Resources << /Font << /F1 {f1} 0 R /F2 {f2} 0 R >> /XObject << /Logo {logo_id} 0 R >> >> /Contents {contenido} 0 R >>".encode()))
    objetos[catalogo - 1] = f"<< /Type /Catalog /Pages {arbol} 0 R >>".encode()
    objetos[arbol - 1] = f"<< /Type /Pages /Kids [{' '.join(f'{item} 0 R' for item in ids)}] /Count {len(ids)} >>".encode()
    salida = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    posiciones = [0]
    for numero, objeto in enumerate(objetos, 1):
        posiciones.append(len(salida)); salida.extend(f"{numero} 0 obj\n".encode() + objeto + b"\nendobj\n")
    xref = len(salida)
    salida.extend(f"xref\n0 {len(objetos)+1}\n0000000000 65535 f \n".encode())
    for posicion in posiciones[1:]:
        salida.extend(f"{posicion:010d} 00000 n \n".encode())
    salida.extend(f"trailer\n<< /Size {len(objetos)+1} /Root {catalogo} 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return bytes(salida)


def informe_requerimiento(ticket):
    return _documento_pdf("INFORME TÉCNICO DE REQUERIMIENTO", "Solicitud de componente, repuesto o insumo", ticket, [
        ("DATOS DEL REQUERIMIENTO", [("Asunto", ticket.titulo), ("Solicitante", _nombre(ticket.solicitante)), ("Ubicación", ticket.ubicacion), ("Equipo afectado", ticket.equipo_afectado)]),
        ("EVALUACIÓN TÉCNICA", [("Diagnóstico", ticket.diagnostico), ("Plan de solución", ticket.plan_solucion), ("Justificación", ticket.justificacion_compra)]),
    ], [("Código", ticket.codigo), ("Fecha de emisión", _fecha()), ("Técnico responsable", _nombre(ticket.tecnico_asignado)), ("Gestión", datetime.now().year)], [
        ("Componente requerido", ticket.componente_requerido), ("Cantidad", ticket.cantidad_componente), ("Especificaciones técnicas", ticket.especificaciones_tecnicas), ("Proveedor de referencia", ticket.proveedor_cotizacion), ("Costo estimado", f"Bs. {_texto(ticket.costo_estimado)}"),
    ])


def informe_final_jefatura(ticket, informe_final, firma=None, firmante=None):
    from usuarios.models import DocumentoProceso
    tecnico = DocumentoProceso.objects.filter(soporte=ticket, tipo='Informe técnico de soporte', usuario_id=ticket.tecnico_asignado_id).exclude(firma=[]).order_by('-creado_en', '-pk').first()
    firmas = [(tecnico.firma, tecnico.nombre_firmante, 'Firma del técnico responsable')] if tecnico else []
    if firma:
        firmas.append((firma, firmante, 'Firma del jefe de UTIC'))
    compra = None
    if ticket.requiere_compra:
        datos_compra = _datos_compra(ticket)
        estado_compra = datos_compra[0] if datos_compra else ticket.get_estado_compra_componente_display()
        monto_compra = datos_compra[1] if datos_compra and datos_compra[1] is not None else ticket.costo_estimado
        compra = [("¿Requirió compra?", "Sí"), ("Componente", ticket.componente_requerido), ("Cantidad", ticket.cantidad_componente), ("Especificaciones", ticket.especificaciones_tecnicas), ("Expediente vinculado", ticket.codigo_compra_vinculada), ("Estado de la compra", estado_compra), ("Monto registrado", f"Bs. {_texto(monto_compra)}")]
    else:
        compra = [("¿Requirió compra?", "No"), ("Resultado", "La atención fue resuelta sin adquisición de componentes o insumos.")]
    return _documento_pdf("INFORME TÉCNICO FINAL DE SOPORTE UTIC", "Cierre y validación del servicio técnico", ticket, [
        ("DATOS DEL REQUERIMIENTO", [("Asunto", ticket.titulo), ("Solicitante", _nombre(ticket.solicitante)), ("Ubicación", ticket.ubicacion), ("Equipo afectado", ticket.equipo_afectado), ("Descripción", ticket.descripcion)]),
        ("DIAGNÓSTICO Y PLAN DE SOLUCIÓN", [("Diagnóstico técnico", ticket.diagnostico), ("Plan de solución", ticket.plan_solucion)]),
        ("INTERVENCIÓN Y PRUEBAS", [("Intervención realizada", ticket.solucion), ("Resultado de pruebas", ticket.resultado_pruebas), ("Conclusión del técnico", ticket.informe_tecnico)]),
        ("CONFORMIDAD DEL SOLICITANTE", [("Resultado", "Conforme" if ticket.conformidad_usuario else "No conforme"), ("Observaciones", ticket.observaciones_usuario)]),
        ("VALIDACIÓN DE JEFATURA UTIC", [("Informe final", informe_final)]),
    ], [("Nro. de informe", f"INF-TEC-{ticket.codigo}"), ("Fecha de emisión", _fecha(getattr(ticket, "cerrado_en", None))), ("Código de ticket", ticket.codigo), ("Gestión", datetime.now().year)], compra, firmas=firmas, espaciado=True)


def informe_tecnico(ticket, texto_informe, firma=None, firmante=None):
    return _documento_pdf("INFORME TÉCNICO DE ATENCIÓN", "Diagnóstico, intervención y pruebas", ticket, [
        ("DATOS DE LA ORDEN", [("Asunto", ticket.titulo), ("Solicitante", _nombre(ticket.solicitante)), ("Ubicación", ticket.ubicacion), ("Equipo", ticket.equipo_afectado)]),
        ("EVALUACIÓN", [("Diagnóstico", ticket.diagnostico), ("Plan de solución", ticket.plan_solucion)]),
        ("TRABAJO REALIZADO", [("Intervención", ticket.solucion), ("Resultado de pruebas", ticket.resultado_pruebas), ("Conclusión técnica", texto_informe)]),
    ], [("Código", ticket.codigo), ("Fecha de emisión", _fecha()), ("Técnico responsable", _nombre(ticket.tecnico_asignado)), ("Gestión", datetime.now().year)], firmas=[(firma, firmante, 'Firma del técnico responsable')] if firma else [])


def informe_jefe_carrera(ticket, contenido):
    return _documento_pdf("INFORME FINAL DEL JEFE DE CARRERA", "Informe del trabajo realizado para Dirección", ticket, [
        ("DATOS DEL TRABAJO", [("Asunto", ticket.titulo), ("Carrera / área", getattr(ticket.area, "nombre", "")), ("Solicitante", _nombre(ticket.solicitante)), ("Técnico", _nombre(ticket.tecnico_asignado))]),
        ("RESULTADO TÉCNICO", [("Diagnóstico", ticket.diagnostico), ("Trabajo realizado", ticket.solucion), ("Pruebas", ticket.resultado_pruebas)]),
        ("INFORME DE JEFATURA UTIC", [("Conclusión", ticket.informe_final)]),
        ("INFORME DEL JEFE DE CARRERA", [("Conclusión y observaciones", contenido)]),
    ], [("Código", ticket.codigo), ("Fecha de emisión", _fecha()), ("Jefe de carrera", _nombre(ticket.solicitante)), ("Gestión", datetime.now().year)])


def informe_requerimiento_mantenimiento(requerimiento):
    return _documento_pdf("INFORME TÉCNICO DE REQUERIMIENTO", "Solicitud de componente para mantenimiento", requerimiento, [
        ("DATOS DEL REQUERIMIENTO", [("Asunto", requerimiento.titulo), ("Solicitante", _nombre(requerimiento.solicitante)), ("Ubicación", requerimiento.ubicacion)]),
        ("EVALUACIÓN TÉCNICA", [("Diagnóstico", requerimiento.diagnostico), ("Plan de solución", requerimiento.plan_solucion)]),
    ], [("Código", requerimiento.codigo), ("Fecha de emisión", _fecha()), ("Técnico responsable", _nombre(requerimiento.auxiliar_asignado)), ("Gestión", datetime.now().year)], [
        ("Componente requerido", requerimiento.producto_requerido), ("Cantidad", requerimiento.cantidad_requerida),
        ("Especificaciones técnicas", requerimiento.especificacion_producto), ("Costo estimado", f"Bs. {_texto(requerimiento.costo_estimado)}"),
    ])
