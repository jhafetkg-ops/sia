"""Documentos del expediente y firmas manuscritas, sin infraestructura PKI.

Las coordenadas se validan y el documento conserva una instantánea inmutable.
La lectura se autoriza mediante el queryset del módulo de origen.
"""
import math
import json
from functools import wraps
from django.db import transaction
from rest_framework.exceptions import ValidationError
from auditoria.utils import registrar_bitacora
from .models import DocumentoProceso, obtener_codigos_rol_efectivos


def validar_firma(valor):
    if isinstance(valor, str):
        try:
            valor = json.loads(valor)
        except (ValueError, TypeError):
            raise ValidationError({'firma': 'Firma inválida.'})
    if not isinstance(valor, list) or not 1 <= len(valor) <= 100:
        raise ValidationError({'firma': 'Dibuje y confirme su firma para este documento.'})
    total = 0
    salida = []
    for trazo in valor:
        if not isinstance(trazo, list) or len(trazo) < 2:
            raise ValidationError({'firma': 'Firma incompleta.'})
        total += len(trazo)
        if total > 10000:
            raise ValidationError({'firma': 'La firma excede el tamaño permitido.'})
        puntos = []
        for punto in trazo:
            if not isinstance(punto, list) or len(punto) != 2 or any(type(v) not in (int, float) or not math.isfinite(v) for v in punto):
                raise ValidationError({'firma': 'Coordenadas inválidas.'})
            if not (0 <= punto[0] <= 600 and 0 <= punto[1] <= 200):
                raise ValidationError({'firma': 'La firma está fuera del área permitida.'})
            puntos.append([round(punto[0], 2), round(punto[1], 2)])
        salida.append(puntos)
    if not any(any(p != t[0] for p in t[1:]) for t in salida):
        raise ValidationError({'firma': 'Dibuje su firma; un punto no es suficiente.'})
    return salida


def emitir_documento(request, expediente, tipo, datos, firma=None):
    from compras.models import SolicitudCompra
    from mantenimiento.models import RequerimientoMantenimiento
    campo = 'compra' if isinstance(expediente, SolicitudCompra) else 'mantenimiento' if isinstance(expediente, RequerimientoMantenimiento) else 'soporte'
    with transaction.atomic():
        documento = DocumentoProceso.objects.create(
            **{campo: expediente}, tipo=tipo, codigo_expediente=expediente.codigo,
            contenido=datos, firma=validar_firma(firma) if firma is not None else [],
            usuario=request.user, nombre_firmante=request.user.nombre_completo,
            roles_firmante=sorted(obtener_codigos_rol_efectivos(request.user)),
        )
        registrar_bitacora(request=request, accion='FIRMAR_DOCUMENTO' if firma is not None else 'EMITIR_DOCUMENTO',
                           modulo='Compras' if campo == 'compra' else 'Mantenimiento' if campo == 'mantenimiento' else 'Soporte Técnico',
                           detalle=f'{expediente.codigo}: {tipo}, documento {documento.pk}.', nivel='INFO')
    return documento


def datos_expediente(obj):
    return {'Expediente': obj.codigo, 'Título': obj.titulo, 'Solicitante': obj.solicitante.nombre_completo,
            'Área': obj.area.nombre if obj.area_id else '', 'Descripción': obj.descripcion}


def documentos_expediente(view, request, pk):
    from rest_framework.response import Response
    obj = view.get_object()
    campo = {'compras': 'compra', 'mantenimiento': 'mantenimiento', 'soporte': 'soporte'}[obj._meta.app_label]
    docs = DocumentoProceso.objects.filter(**{campo: obj}).order_by('creado_en')
    return Response([{'id': d.pk, 'tipo': d.tipo, 'codigo_expediente': d.codigo_expediente,
                      'contenido': d.contenido, 'firma': d.firma, 'usuario_id': d.usuario_id,
                      'nombre_firmante': d.nombre_firmante, 'roles_firmante': d.roles_firmante,
                      'creado_en': d.creado_en} for d in docs])


def pdf_documento(view, request, pk, documento_id):
    from types import SimpleNamespace
    from django.http import HttpResponse
    from django.shortcuts import get_object_or_404
    from soporte.informes_pdf import _documento_pdf
    obj = view.get_object()
    campo = {'compras': 'compra', 'mantenimiento': 'mantenimiento', 'soporte': 'soporte'}[obj._meta.app_label]
    d = get_object_or_404(DocumentoProceso, pk=documento_id, **{campo: obj})
    secciones = [('DATOS DEL EXPEDIENTE', list(d.contenido.items()))]
    secciones.append(('TRAZABILIDAD', [('Usuario autenticado', d.usuario_id), ('Responsable', d.nombre_firmante), ('Rol', ', '.join(d.roles_firmante)), ('Fecha y hora', d.creado_en.isoformat())]))
    datos = _documento_pdf(d.tipo.upper(), 'Documento del expediente SIA', SimpleNamespace(codigo=d.codigo_expediente), secciones,
                           [('Documento', d.pk), ('Expediente', d.codigo_expediente)], firma=d.firma,
                           firmante=d.nombre_firmante, unidad=obj.area.nombre if obj.area_id else obj._meta.app_label.upper())
    respuesta = HttpResponse(datos, content_type='application/pdf')
    respuesta['Content-Disposition'] = f'attachment; filename="documento-sia-{d.pk}.pdf"'
    respuesta['Cache-Control'] = 'private, no-store'
    return respuesta


def documentar(tipo, firma_obligatoria=False, solo_conforme=False, permitir_firma=True):
    """La emisión y la transición se confirman en una sola transacción."""
    def decorador(funcion):
        @wraps(funcion)
        def ejecutar(view, request, pk=None, *args, **kwargs):
            with transaction.atomic():
                obj = view.get_object()
                # Bloquear el expediente evita dos firmas/transiciones simultáneas.
                type(obj).objects.select_for_update().get(pk=obj.pk)
                conforme = request.data.get('conformidad', request.data.get('problema_resuelto', True)) is not False
                firma = request.data.get('firma') if permitir_firma else None
                respuesta = funcion(view, request, pk, *args, **kwargs)
                if 200 <= respuesta.status_code < 300:
                    if firma is not None or (firma_obligatoria and (conforme or not solo_conforme)):
                        firma = validar_firma(firma)
                    obj.refresh_from_db()
                    datos = datos_expediente(obj)
                    for campo in ('diagnostico', 'trabajo_realizado', 'informe_trabajo', 'informe_tecnico', 'informe_final',
                                  'resultado_pruebas', 'observaciones_conformidad', 'observaciones_usuario', 'monto_desembolsado',
                                  'responsable_adquisicion', 'fondos_recibidos_por', 'proveedor', 'monto_real',
                                  'cantidad_recibida', 'responsable_recepcion', 'cantidad_entregada', 'entregado_a'):
                        valor = getattr(obj, campo, None)
                        if valor is not None and valor != '':
                            datos[campo.replace('_', ' ').capitalize()] = str(valor)
                    datos['Resultado'] = 'Conforme' if solo_conforme and conforme else 'No conforme' if solo_conforme else tipo
                    if tipo == 'Recepción de fondos':
                        entrega = DocumentoProceso.objects.filter(compra=obj, tipo='Constancia de desembolso').order_by('-creado_en').first()
                        if entrega:
                            datos['Entregado por'] = entrega.nombre_firmante
                            datos['Fecha de desembolso'] = entrega.creado_en.isoformat()
                    emitir_documento(request, obj, tipo, datos, firma=firma)
                return respuesta
        return ejecutar
    return decorador
