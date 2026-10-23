"""Acta de conformidad imprimible y copia firmada de la entrega de almacén."""
from uuid import uuid4
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import ValidationError, NotFound
from rest_framework.response import Response
from auditoria.utils import registrar_bitacora
from .models import ActaEntregaAlmacen, SolicitudCompra
from .tesoreria import validar_archivo


def estado_entregable(s):
    if s.estado != 'COMPRA_REGISTRADA' or s.cerrado_inmutable or not s.fecha_despacho_almacen or not s.cantidad_entregada:
        raise ValidationError({'detalle': 'Debe registrar la compra, la entrada y la salida de almacén antes de generar el acta.'})


def instantanea(s):
    return {'codigo': s.codigo, 'titulo': s.titulo, 'descripcion': s.descripcion, 'especificaciones': s.especificaciones,
            'solicitante': s.solicitante.nombre_completo, 'area': s.area.nombre if s.area_id else '',
            'cantidad_solicitada': s.cantidad, 'cantidad_recibida': s.cantidad_recibida, 'cantidad_entregada': s.cantidad_entregada,
            'proveedor': s.proveedor, 'monto_real': str(s.monto_real or ''), 'destino_registrado': s.entregado_a,
            'responsable_recepcion': s.responsable_recepcion, 'observacion_ingreso': s.observacion_ingreso, 'observacion_salida': s.observacion_salida,
            'fecha_ingreso': s.fecha_ingreso_almacen.isoformat() if s.fecha_ingreso_almacen else '',
            'fecha_salida': s.fecha_despacho_almacen.isoformat() if s.fecha_despacho_almacen else ''}


def receptor_acta(s):
    if s.requerimiento_mantenimiento_id:
        return s.requerimiento_mantenimiento.auxiliar_asignado
    if s.ticket_soporte_id:
        return s.ticket_soporte.tecnico_asignado
    return s.solicitante


def puede_leer_actas(s, usuario):
    from .views import tiene_permiso
    from usuarios.models import obtener_codigos_rol_efectivos
    receptor = receptor_acta(s)
    return (tiene_permiso(usuario, 'ENTREGAR_PRODUCTO')
            or 'DIRECTOR' in obtener_codigos_rol_efectivos(usuario)
            or (receptor is not None and receptor.pk == usuario.pk))


def pdf_acta(datos):
    from .acta_pdf import generar_acta_pdf
    return generar_acta_pdf(datos)


def representar(a, usuario):
    base = f'/api/compras/solicitudes/{a.solicitud_id}/actas-almacen/{a.pk}'
    return {'id': a.pk, 'referencia': str(a.referencia), 'datos': a.datos, 'generado_en': a.generado_en,
            'confirmado_en': a.confirmado_en, 'puede_reanudar': a.generado_por_id == usuario.pk and not a.confirmado_en,
            'original_url': base + '/original/', 'firmado_url': base + '/firmado/' if a.firmado else None}


@transaction.atomic
def actas(view, request):
    from .views import tiene_permiso, respuesta_sin_permiso
    s = view.get_object()
    director_lectura = request.method == 'GET' and puede_leer_actas(s, request.user)
    if not (tiene_permiso(request.user, 'ENTREGAR_PRODUCTO') or director_lectura):
        return respuesta_sin_permiso('ENTREGAR_PRODUCTO')
    if request.method == 'GET':
        return Response([representar(a, request.user) for a in s.actas_almacen.order_by('-generado_en', '-pk')])
    s = SolicitudCompra.objects.select_for_update().get(pk=s.pk)
    estado_entregable(s)
    if request.data.get('entrega_confirmada') is not True:
        raise ValidationError({'detalle': 'Confirme la entrega fisica del producto para elaborar el acta.'})
    receptor = receptor_acta(s)
    if receptor is None:
        raise ValidationError({'detalle': 'Asigne el tecnico receptor antes de entregar el producto.'})
    vinculado = bool(s.ticket_soporte_id or s.requerimiento_mantenimiento_id)
    recibe = receptor.nombre_completo if vinculado else ' '.join(str(request.data.get('recibe', receptor.nombre_completo)).split())
    if not vinculado and (len(recibe.split()) < 2 or len(recibe) > 150 or not all(any(c.isalpha() for c in parte) for parte in recibe.split())):
        raise ValidationError({'detalle': 'Indique el nombre completo de quien recibe.'})
    indicado = ' '.join(str(request.data.get('recibe', recibe)).split())
    if vinculado and indicado != recibe:
        raise ValidationError({'detalle': 'El acta debe identificar al receptor asignado al expediente.'})
    observaciones = str(request.data.get('observaciones', '')).strip()
    if len(observaciones) > 2000:
        raise ValidationError({'detalle': 'Las observaciones pueden tener hasta 2000 caracteres.'})
    referencia = uuid4()
    datos = {**instantanea(s), 'recibe': recibe, 'entrega': request.user.nombre_completo, 'observaciones': observaciones,
             'referencia': str(referencia), 'fecha': timezone.localtime().strftime('%d/%m/%Y %H:%M'),
             'recibe_id': receptor.pk if recibe == receptor.nombre_completo else None, 'entrega_id': request.user.pk,
             'tipo_receptor': 'Tecnico' if s.ticket_soporte_id or s.requerimiento_mantenimiento_id else 'Solicitante'}
    a = ActaEntregaAlmacen(solicitud=s, referencia=referencia, datos=datos, generado_por=request.user)
    a.original.save(f'acta-{referencia}.pdf', ContentFile(pdf_acta(datos)), save=False)
    a.save()
    registrar_bitacora(request=request, accion='GENERAR_ACTA_ALMACEN', modulo='Compras',
                      detalle=f'{s.codigo}: acta {referencia}, recibe {recibe}, entrega {request.user.nombre_completo}, {s.cantidad_entregada} unidad(es).', nivel='INFO')
    return Response(representar(a, request.user), status=201)


def guardar_firmada(request, s):
    estado_entregable(s)
    acta_id = str(request.data.get('acta_id', ''))
    if not acta_id.isdigit():
        raise ValidationError({'detalle': 'Genere el acta de conformidad antes de registrar la entrega.'})
    a = get_object_or_404(ActaEntregaAlmacen.objects.select_for_update(), pk=acta_id, solicitud=s, generado_por=request.user)
    ultimo = s.actas_almacen.filter(generado_por=request.user).order_by('-generado_en', '-pk').first()
    if a.confirmado_en or ultimo.pk != a.pk:
        raise ValidationError({'detalle': 'Utilice la última acta generada y pendiente de firma.'})
    if any(a.datos.get(k) != v for k, v in instantanea(s).items()):
        raise ValidationError({'detalle': 'Los datos del expediente cambiaron. Genere una nueva acta con los datos actuales.'})
    receptor = receptor_acta(s)
    if (s.ticket_soporte_id or s.requerimiento_mantenimiento_id) and (not receptor or a.datos.get('recibe') != receptor.nombre_completo or a.datos.get('recibe_id', receptor.pk) != receptor.pk):
        raise ValidationError({'detalle': 'El receptor del expediente cambio. Genere el acta para el receptor actual.'})
    firmado = request.FILES.get('acta_conformidad')
    if not firmado:
        raise ValidationError({'detalle': 'Adjunte el acta PDF con las firmas de quien recibe y del encargado de almacén.'})
    validar_archivo(firmado, pdf=True)
    if s.ticket_soporte_id or s.requerimiento_mantenimiento_id:
        s.acta_firmada_en = timezone.now()
    a.firmado = firmado
    a.confirmado_en = timezone.now()
    a.save(update_fields=['firmado', 'confirmado_en'])
    with a.firmado.open('rb') as archivo:
        s.acta_conformidad.save(f'acta-firmada-{a.referencia}.pdf', ContentFile(archivo.read()), save=False)
    registrar_bitacora(request=request, accion='ARCHIVAR_ACTA_FIRMADA', modulo='Compras',
                      detalle=f'{s.codigo}: acta {a.referencia} firmada por ambas partes, archivada por {request.user.nombre_completo}.', nivel='INFO')


def archivo_acta(view, request, acta_id, clase):
    from .views import tiene_permiso, respuesta_sin_permiso
    s = view.get_object()
    director_lectura = request.method == 'GET' and puede_leer_actas(s, request.user)
    if not (tiene_permiso(request.user, 'ENTREGAR_PRODUCTO') or director_lectura):
        return respuesta_sin_permiso('ENTREGAR_PRODUCTO')
    a = get_object_or_404(ActaEntregaAlmacen, pk=acta_id, solicitud=s)
    archivo = getattr(a, clase)
    if not archivo:
        raise NotFound('El acta todavía no tiene este documento.')
    try:
        respuesta = FileResponse(archivo.open('rb'), content_type='application/pdf')
    except FileNotFoundError:
        raise NotFound('No se encontró el archivo del acta.')
    respuesta['Cache-Control'] = 'private, no-store'
    respuesta['X-Content-Type-Options'] = 'nosniff'
    return respuesta
