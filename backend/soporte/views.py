from usuarios.documentos import documentar, documentos_expediente, pdf_documento, validar_firma
from datetime import timedelta
from decimal import Decimal, InvalidOperation

from django.utils import timezone
from django.core.files.base import ContentFile

from rest_framework import (
    status,
    viewsets,
)

from usuarios.authentication import (
    ExpiringTokenAuthentication as TokenAuthentication,
)

from rest_framework.decorators import (
    action,
)

from rest_framework.permissions import (
    IsAuthenticated,
)

from rest_framework.response import Response


from usuarios.models import (
    Area,
    Usuario,
    UsuarioRol,
    RolPermiso,
    obtener_codigos_rol_efectivos,
)

from auditoria.utils import (
    registrar_bitacora,
)

from .models import (
    CategoriaTicket,
    EstadoTicket,
    Ticket,
    NotificacionSoporte,
)

from .serializers import (
    CategoriaTicketSerializer,
    EstadoTicketSerializer,
    TicketSerializer,
    NotificacionSoporteSerializer,
)
from .informes_pdf import informe_final_jefatura, informe_jefe_carrera, informe_requerimiento, informe_tecnico as generar_informe_tecnico


# ==========================================================
# ROLES ADMINISTRATIVOS
# ==========================================================

ROLES_ADMIN = {
    "ADMIN",
    "ADMINISTRADOR",
    "ADMINISTRADOR_SIGTA",
}


def crear_notificacion(destinatario, ticket, tipo, titulo, mensaje):
    if destinatario:
        NotificacionSoporte.objects.create(destinatario=destinatario, ticket=ticket, tipo=tipo, titulo=titulo, mensaje=mensaje)


class NotificacionSoporteViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = NotificacionSoporteSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return NotificacionSoporte.objects.filter(destinatario=self.request.user).select_related("ticket")

    @action(detail=True, methods=["post"], url_path="marcar-leida")
    def marcar_leida(self, request, pk=None):
        notificacion = self.get_object()
        if not notificacion.leida:
            notificacion.leida = True
            notificacion.leida_en = timezone.now()
            notificacion.save(update_fields=["leida", "leida_en"])
        return Response(self.get_serializer(notificacion).data)

    @action(detail=False, methods=["post"], url_path="marcar-todas-leidas")
    def marcar_todas_leidas(self, request):
        self.get_queryset().filter(leida=False).update(leida=True, leida_en=timezone.now())
        return Response({"ok": True})


# ==========================================================
# VALORES POR DEFECTO DEL FORMULARIO SIMPLIFICADO
# ==========================================================
#
# El portal solicitante ya no pide área ni categoría: solo
# título, descripción, tipo (Soporte/Mantenimiento) y foto.
# Estos helpers completan los campos que el modelo Ticket
# sigue requiriendo.
# ==========================================================

def _area_por_defecto():

    return (
        Area.objects
        .filter(activo=True)
        .order_by("id")
        .first()
    )


def _categoria_por_defecto():

    return (
        CategoriaTicket.objects
        .filter(codigo="OTRO", activo=True)
        .first()
        or
        CategoriaTicket.objects
        .filter(activo=True)
        .order_by("id")
        .first()
    )


# ==========================================================
# SLA POR PRIORIDAD
# ==========================================================
#
# Por ahora estos valores forman parte de la lógica del
# sistema. Más adelante los conectaremos con Preferencias.
#
# ==========================================================

SLA_POR_PRIORIDAD = {
    "CRITICA": 4,
    "ALTA": 8,
    "MEDIA": 24,
    "BAJA": 48,
}


# ==========================================================
# ROLES DEL USUARIO
# ==========================================================

def obtener_roles(usuario):

    # Incluye roles delegados temporalmente (Delegar aprobación
    # temporal) además de los roles propios.
    return obtener_codigos_rol_efectivos(usuario)


# ==========================================================
# VERIFICAR ADMIN
# ==========================================================

def es_admin(usuario):

    if (
        not usuario
        or
        not usuario.is_authenticated
    ):
        return False


    if usuario.is_superuser:
        return True


    roles = {
        str(codigo)
        .strip()
        .upper()

        for codigo in obtener_roles(
            usuario
        )
    }


    return bool(
        roles.intersection(
            ROLES_ADMIN
        )
    )


# ==========================================================
# VERIFICAR PERMISO
# ==========================================================

def tiene_permiso(
    usuario,
    codigo_permiso
):

    if es_admin(usuario):
        return True


    codigos_rol = obtener_roles(usuario)


    return (
        RolPermiso.objects
        .filter(
            rol__codigo__in=codigos_rol,
            rol__activo=True,

            permiso__codigo=codigo_permiso,
            permiso__activo=True,

            activo=True,
        )
        .exists()
    )


# ==========================================================
# OPERADOR DE SOPORTE
# ==========================================================

def puede_operar_soporte(
    usuario
):

    if es_admin(usuario):
        return True


    if tiene_permiso(
        usuario,
        "VER_SOPORTE_TECNICO"
    ):
        return True


    # Compatibilidad temporal con roles anteriores.
    roles = obtener_roles(
        usuario
    )


    return (
        "AGENTE" in roles
        or
        "SUPERVISOR_AREA" in roles
    )


# ==========================================================
# RESPUESTA SIN PERMISO
# ==========================================================

def respuesta_sin_permiso(
    codigo_permiso
):

    return Response(
        {
            "ok": False,

            "detalle": (
                "No tiene permiso para realizar "
                "esta actividad."
            ),

            "permiso_requerido":
                codigo_permiso,
        },
        status=status.HTTP_403_FORBIDDEN
    )


# ==========================================================
# BUSCAR ESTADO
# ==========================================================

def obtener_estado(
    codigo
):

    try:

        return EstadoTicket.objects.get(
            codigo=codigo,
            activo=True
        )

    except EstadoTicket.DoesNotExist:

        return None


# ==========================================================
# VALIDAR ESTADO DEL TICKET
# ==========================================================

def validar_estado_ticket(
    ticket,
    estados_permitidos
):

    return (
        ticket.estado.codigo
        in estados_permitidos
    )


# ==========================================================
# RESPUESTA DEL TICKET
# ==========================================================

def respuesta_ticket(
    ticket,
    mensaje,
    codigo_http=status.HTTP_200_OK
):

    serializer = TicketSerializer(
        ticket
    )


    return Response(
        {
            "ok": True,

            "mensaje":
                mensaje,

            "ticket":
                serializer.data,
        },
        status=codigo_http
    )


# ==========================================================
# CALCULAR CUMPLIMIENTO SLA
# ==========================================================

def calcular_sla_cumplido(
    ticket,
    fecha_fin=None
):

    if not ticket.sla_fecha_limite:
        return None


    if fecha_fin is None:

        fecha_fin = timezone.now()


    return (
        fecha_fin
        <=
        ticket.sla_fecha_limite
    )


# ==========================================================
# CATEGORÍAS
# ==========================================================

class CategoriaTicketViewSet(
    viewsets.ReadOnlyModelViewSet
):

    queryset = (
        CategoriaTicket.objects
        .filter(
            activo=True
        )
        .order_by(
            "nombre"
        )
    )

    serializer_class = (
        CategoriaTicketSerializer
    )

    authentication_classes = [
        TokenAuthentication
    ]

    permission_classes = [
        IsAuthenticated
    ]


# ==========================================================
# ESTADOS
# ==========================================================

class EstadoTicketViewSet(
    viewsets.ReadOnlyModelViewSet
):

    queryset = (
        EstadoTicket.objects
        .filter(
            activo=True
        )
        .order_by(
            "id"
        )
    )

    serializer_class = (
        EstadoTicketSerializer
    )

    authentication_classes = [
        TokenAuthentication
    ]

    permission_classes = [
        IsAuthenticated
    ]


# ==========================================================
# TICKETS DE SOPORTE
# ==========================================================

class TicketViewSet(
    viewsets.ModelViewSet
):

    @action(detail=True, methods=['get'], url_path='documentos')
    def documentos(self, request, pk=None):
        return documentos_expediente(self, request, pk)

    def finalize_response(self, request, response, *args, **kwargs):
        from usuarios.archivos import firmar_urls
        if hasattr(response, 'data'):
            response.data = firmar_urls(response.data, request)
        return super().finalize_response(request, response, *args, **kwargs)

    @action(detail=True, methods=['get'], url_path=r'documentos/(?P<documento_id>[0-9]+)/pdf')
    def documento_pdf(self, request, pk=None, documento_id=None):
        return pdf_documento(self, request, pk, documento_id)

    serializer_class = (
        TicketSerializer
    )

    authentication_classes = [
        TokenAuthentication
    ]

    permission_classes = [
        IsAuthenticated
    ]


    # ======================================================
    # CONSULTA
    # ======================================================

    def get_queryset(self):

        usuario = (
            self.request.user
        )


        queryset = (
            Ticket.objects
            .select_related(
                "solicitante",
                "tecnico_asignado",
                "area",
                "categoria",
                "estado",
            )
            .prefetch_related(
                "especialistas_apoyo"
            )
            .order_by(
                "-creado_en"
            )
        )


        if self.action == "list" and self.request.query_params.get("propias") == "1":
            return queryset.filter(solicitante=usuario)

        if es_admin(usuario):
            return queryset


        roles = obtener_roles(usuario)

        # La bandeja del Especialista tiene una única fuente de verdad:
        # solamente órdenes asignadas a él o en las que participa como apoyo.
        if (
            set(roles).intersection({"ESPECIALISTA", "AGENTE"})
            and not set(roles).intersection({"JEFE_UTIC", "SUPERVISOR_AREA"})
        ):
            from django.db.models import Q
            return queryset.filter(
                Q(tecnico_asignado=usuario) | Q(especialistas_apoyo=usuario)
            ).distinct()


        if puede_operar_soporte(
            usuario
        ):
            return queryset


        return queryset.filter(
            solicitante=usuario
        )


    # ======================================================
    # CREAR / REGISTRAR TICKET
    # ======================================================

    def create(
        self,
        request,
        *args,
        **kwargs
    ):

        if not (
            es_admin(
                request.user
            )
            or
            tiene_permiso(
                request.user,
                "REGISTRAR_TICKET"
            )
        ):

            return respuesta_sin_permiso(
                "REGISTRAR_TICKET"
            )


        serializer = self.get_serializer(
            data=request.data
        )


        serializer.is_valid(
            raise_exception=True
        )


        # BPMN: el ticket debe describir el problema, la ubicación y el
        # equipo involucrado; las evidencias se adjuntan "si corresponde".
        if not str(serializer.validated_data.get("ubicacion", "")).strip():

            return Response(
                {"ubicacion": "Indique la ubicación donde se presenta el problema."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not str(serializer.validated_data.get("equipo_afectado", "")).strip():

            return Response(
                {"equipo_afectado": "Indique el equipo involucrado."},
                status=status.HTTP_400_BAD_REQUEST
            )


        extra = {}

        if not serializer.validated_data.get("area"):

            area_defecto = _area_por_defecto()

            if area_defecto is None:
                return Response(
                    {"detalle": "No hay áreas registradas en el sistema."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            extra["area"] = area_defecto

        if not serializer.validated_data.get("categoria"):

            categoria_defecto = _categoria_por_defecto()

            if categoria_defecto is None:
                return Response(
                    {"detalle": "No hay categorías de ticket registradas en el sistema."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            extra["categoria"] = categoria_defecto


        ticket = serializer.save(**extra)


        registrar_bitacora(
            request=request,
            accion="REGISTRAR_TICKET",
            modulo="Soporte Técnico",
            detalle=(
                f"Se registró el ticket "
                f"{ticket.codigo}: "
                f"{ticket.titulo}."
            ),
            nivel="INFO",
        )


        return respuesta_ticket(
            ticket,
            "Ticket registrado correctamente.",
            status.HTTP_201_CREATED
        )


    # ======================================================
    # MODIFICAR TICKET
    # ======================================================

    def partial_update(
        self,
        request,
        *args,
        **kwargs
    ):

        ticket = self.get_object()

        usuario = request.user


        # --------------------------------------------------
        # SOLICITANTE
        # --------------------------------------------------

        if (
            ticket.solicitante_id
            ==
            usuario.id
        ):

            if (
                ticket.estado.codigo
                not in [
                    "BORRADOR",
                    "NUEVO",
                ]
            ):

                return Response(
                    {
                        "detalle": (
                            "El ticket ya está siendo "
                            "atendido y no puede modificarse."
                        )
                    },
                    status=
                        status.HTTP_400_BAD_REQUEST
                )


        # --------------------------------------------------
        # PERSONAL DE SOPORTE
        # --------------------------------------------------

        elif not puede_operar_soporte(
            usuario
        ):

            return Response(
                {
                    "detalle": (
                        "No tiene permiso para "
                        "modificar este ticket."
                    )
                },
                status=
                    status.HTTP_403_FORBIDDEN
            )


        respuesta = (
            super()
            .partial_update(
                request,
                *args,
                **kwargs
            )
        )


        registrar_bitacora(
            request=request,
            accion="MODIFICAR_TICKET_SOPORTE",
            modulo="Soporte Técnico",
            detalle=(
                f"Se modificó el ticket "
                f"{ticket.codigo}."
            ),
            nivel="INFO",
        )


        return respuesta


    # ======================================================
    # ANULAR TICKET
    # ======================================================

    def destroy(
        self,
        request,
        *args,
        **kwargs
    ):

        ticket = self.get_object()

        usuario = request.user


        if (
            ticket.solicitante_id
            !=
            usuario.id
        ):

            return Response(
                {
                    "detalle": (
                        "Solo el solicitante puede "
                        "anular este ticket."
                    )
                },
                status=
                    status.HTTP_403_FORBIDDEN
            )


        if (
            ticket.estado.codigo
            not in [
                "BORRADOR",
                "NUEVO",
            ]
        ):

            return Response(
                {
                    "detalle": (
                        "El ticket ya está en atención "
                        "y no puede anularse."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        estado_anulado = obtener_estado(
            "ANULADO"
        )


        if not estado_anulado:

            return Response(
                {
                    "detalle":
                        "No existe el estado ANULADO."
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        ticket.estado = estado_anulado

        ticket.activo = False


        ticket.save(
            update_fields=[
                "estado",
                "activo",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion="ANULAR_TICKET_SOPORTE",
            modulo="Soporte Técnico",
            detalle=(
                f"Se anuló el ticket "
                f"{ticket.codigo}."
            ),
            nivel="WARNING",
        )


        return Response(
            {
                "ok": True,

                "mensaje":
                    "Ticket anulado correctamente."
            },
            status=status.HTTP_200_OK
        )


    # ======================================================
    # 1. RECIBIR TICKET Y VALIDAR TICKET
    # ======================================================
    #
    # Actor: Jefe de UTIC
    #
    # NUEVO -> EN_ANALISIS
    #
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="validar-ticket"
    )
    def validar_ticket(
        self,
        request,
        pk=None
    ):

        if not tiene_permiso(
            request.user,
            "RECIBIR_VALIDAR_TICKET"
        ):

            return respuesta_sin_permiso(
                "RECIBIR_VALIDAR_TICKET"
            )


        ticket = self.get_object()


        if not validar_estado_ticket(
            ticket,
            ["NUEVO"]
        ):

            return Response(
                {
                    "detalle": (
                        "Solo los tickets NUEVOS "
                        "pueden recibirse y validarse."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        # --------------------------------------------------
        # BPMN: "¿Es válido el ticket?" -> rama NO
        # --------------------------------------------------

        es_valido = request.data.get("es_valido", True)

        if es_valido is False:

            motivo = str(request.data.get("motivo_rechazo", "")).strip()

            if not motivo:

                return Response(
                    {"motivo_rechazo": "Debe indicar el motivo del rechazo."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            estado_rechazado = obtener_estado("RECHAZADO")

            if not estado_rechazado:

                return Response(
                    {"detalle": "No existe el estado RECHAZADO."},
                    status=status.HTTP_400_BAD_REQUEST
                )

            ticket.estado = estado_rechazado
            ticket.criterio_tecnico = motivo
            ticket.validado_en = timezone.now()
            ticket.activo = False

            ticket.save(
                update_fields=[
                    "estado",
                    "criterio_tecnico",
                    "validado_en",
                    "activo",
                    "actualizado_en",
                ]
            )

            crear_notificacion(
                ticket.solicitante, ticket, "RECHAZO",
                f"{ticket.codigo} · Ticket no validado",
                motivo,
            )

            registrar_bitacora(
                request=request,
                accion="RECHAZAR_TICKET",
                modulo="Soporte Técnico",
                detalle=f"Se rechazó el ticket {ticket.codigo}: {motivo}.",
                nivel="WARNING",
            )

            return respuesta_ticket(
                ticket,
                "Ticket rechazado y devuelto al solicitante."
            )


        estado_destino = obtener_estado(
            "EN_ANALISIS"
        )


        if not estado_destino:

            return Response(
                {
                    "detalle": (
                        "No existe el estado "
                        "EN_ANALISIS."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        ticket.estado = estado_destino

        ticket.validado_en = timezone.now()


        ticket.save(
            update_fields=[
                "estado",
                "validado_en",
                "actualizado_en",
            ]
        )

        crear_notificacion(
            ticket.solicitante, ticket, "EXITO",
            f"{ticket.codigo} · Ticket validado",
            "Jefatura UTIC validó su solicitud. El ticket continuará a clasificación y asignación técnica.",
        )


        registrar_bitacora(
            request=request,
            accion="RECIBIR_VALIDAR_TICKET",
            modulo="Soporte Técnico",
            detalle=(
                f"Se recibió y validó el ticket "
                f"{ticket.codigo}."
            ),
            nivel="INFO",
        )


        return respuesta_ticket(
            ticket,
            "Ticket recibido y validado correctamente."
        )


    # ======================================================
    # 2. CLASIFICAR PRIORIDAD Y ASIGNAR SLA
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="clasificar-prioridad"
    )
    def clasificar_prioridad(
        self,
        request,
        pk=None
    ):

        if not tiene_permiso(
            request.user,
            "CLASIFICAR_PRIORIDAD_SLA"
        ):

            return respuesta_sin_permiso(
                "CLASIFICAR_PRIORIDAD_SLA"
            )


        ticket = self.get_object()


        if not validar_estado_ticket(
            ticket,
            ["EN_ANALISIS"]
        ):

            return Response(
                {
                    "detalle": (
                        "El ticket debe encontrarse "
                        "EN_ANALISIS."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        prioridad = (
            str(
                request.data.get(
                    "prioridad",
                    ""
                )
            )
            .strip()
            .upper()
        )


        if prioridad not in SLA_POR_PRIORIDAD:

            return Response(
                {
                    "prioridad": (
                        "Seleccione BAJA, MEDIA, "
                        "ALTA o CRITICA."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        criterio_tecnico = (
            str(
                request.data.get(
                    "criterio_tecnico",
                    ""
                )
            )
            .strip()
        )


        if not criterio_tecnico:

            return Response(
                {
                    "criterio_tecnico": (
                        "Debe registrar el criterio "
                        "técnico de clasificación."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        ahora = timezone.now()

        horas_sla = (
            SLA_POR_PRIORIDAD[
                prioridad
            ]
        )


        fecha_limite = (
            ahora
            +
            timedelta(
                hours=horas_sla
            )
        )


        ticket.prioridad = prioridad

        ticket.criterio_tecnico = (
            criterio_tecnico
        )

        ticket.sla_horas = (
            horas_sla
        )

        ticket.sla_fecha_limite = (
            fecha_limite
        )

        ticket.sla_cumplido = None

        ticket.clasificado_en = (
            ahora
        )


        ticket.save(
            update_fields=[
                "prioridad",
                "criterio_tecnico",
                "sla_horas",
                "sla_fecha_limite",
                "sla_cumplido",
                "clasificado_en",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion="CLASIFICAR_PRIORIDAD_SLA",
            modulo="Soporte Técnico",
            detalle=(
                f"Se clasificó el ticket "
                f"{ticket.codigo} como "
                f"{prioridad}. "
                f"SLA asignado: "
                f"{horas_sla} horas."
            ),
            nivel="INFO",
        )


        return respuesta_ticket(
            ticket,
            (
                f"Prioridad {prioridad} registrada. "
                f"SLA asignado: {horas_sla} horas."
            )
        )


    # ======================================================
    # 3. DESIGNAR REVISIÓN AL ESPECIALISTA
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="designar-revision"
    )
    def designar_revision(
        self,
        request,
        pk=None
    ):

        if not tiene_permiso(
            request.user,
            "DESIGNAR_REVISION"
        ):

            return respuesta_sin_permiso(
                "DESIGNAR_REVISION"
            )


        ticket = self.get_object()


        if not validar_estado_ticket(
            ticket,
            ["EN_ANALISIS"]
        ):

            return Response(
                {
                    "detalle": (
                        "El ticket debe encontrarse "
                        "EN_ANALISIS."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        if not ticket.prioridad:

            return Response(
                {
                    "detalle": (
                        "Primero debe clasificar "
                        "la prioridad y asignar SLA."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        tecnico_id = request.data.get(
            "tecnico_id"
        )


        if not tecnico_id:

            return Response(
                {
                    "tecnico_id": (
                        "Debe seleccionar al "
                        "especialista responsable."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        try:

            tecnico = Usuario.objects.get(
                pk=tecnico_id,
                is_active=True
            )

        except Usuario.DoesNotExist:

            return Response(
                {
                    "tecnico_id": (
                        "El especialista seleccionado "
                        "no existe o está inactivo."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        tiene_rol_especialista = (
            UsuarioRol.objects
            .filter(
                usuario=tecnico,
                activo=True,
                rol__activo=True,
                rol__codigo__in=[
                    "ESPECIALISTA",
                    "AGENTE",
                ]
            )
            .exists()
        )


        if not tiene_rol_especialista:

            return Response(
                {
                    "tecnico_id": (
                        "El usuario seleccionado no "
                        "posee el rol Especialista."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        estado_asignado = obtener_estado(
            "ASIGNADO"
        )


        if not estado_asignado:

            return Response(
                {
                    "detalle":
                        "No existe el estado ASIGNADO."
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        ahora = timezone.now()


        ticket.tecnico_asignado = tecnico

        ticket.estado = estado_asignado

        ticket.asignado_en = ahora


        ticket.save(
            update_fields=[
                "tecnico_asignado",
                "estado",
                "asignado_en",
                "actualizado_en",
            ]
        )


        apoyo_ids = request.data.get(
            "especialistas_apoyo",
            []
        )


        if isinstance(
            apoyo_ids,
            list
        ):

            especialistas = (
                Usuario.objects
                .filter(
                    id__in=apoyo_ids,
                    is_active=True,
                    roles_asignados__activo=True,
                    roles_asignados__rol__codigo__in=[
                        "ESPECIALISTA",
                        "AGENTE",
                    ]
                )
                .distinct()
            )


            ticket.especialistas_apoyo.set(
                especialistas
            )


        registrar_bitacora(
            request=request,
            accion="DESIGNAR_REVISION",
            modulo="Soporte Técnico",
            detalle=(
                f"Se designó a "
                f"{tecnico.nombre_completo} "
                f"como responsable del ticket "
                f"{ticket.codigo}."
            ),
            nivel="INFO",
        )


        return respuesta_ticket(
            ticket,
            "Especialista designado correctamente."
        )


    # ======================================================
    # 4. REALIZAR INSPECCIÓN TÉCNICA Y DIAGNÓSTICO
    # ======================================================

    @action(detail=True, methods=["post"], url_path="iniciar-atencion")
    def iniciar_atencion(self, request, pk=None):
        if not tiene_permiso(request.user, "REALIZAR_INSPECCION_DIAGNOSTICO"):
            return respuesta_sin_permiso("REALIZAR_INSPECCION_DIAGNOSTICO")
        ticket = self.get_object()
        if validar_estado_ticket(ticket, ["EN_DIAGNOSTICO"]):
            return respuesta_ticket(
                ticket,
                "La orden ya fue recibida. Puede registrar el diagnóstico.",
            )
        if not validar_estado_ticket(ticket, ["ASIGNADO"]):
            return Response(
                {
                    "detalle": (
                        "La orden ya avanzó y no está pendiente de recepción. "
                        f"Estado actual: {ticket.estado.nombre}."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not (es_admin(request.user) or ticket.tecnico_asignado_id == request.user.id):
            return Response(
                {"detalle": "Solo el especialista asignado puede recibir esta orden."},
                status=status.HTTP_403_FORBIDDEN,
            )
        estado_diagnostico = obtener_estado("EN_DIAGNOSTICO")
        if not estado_diagnostico:
            return Response(
                {"detalle": "No existe el estado EN_DIAGNOSTICO."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        ticket.estado = estado_diagnostico
        ticket.inicio_atencion_en = timezone.now()
        ticket.save(update_fields=["estado", "inicio_atencion_en", "actualizado_en"])
        registrar_bitacora(
            request=request, accion="ORDEN_RECIBIDA", modulo="Soporte Técnico",
            detalle=f"El especialista recibió la orden {ticket.codigo} e inició la atención.",
            nivel="INFO",
        )
        return respuesta_ticket(ticket, "Orden recibida. Puede registrar el diagnóstico.")

    @action(
        detail=True,
        methods=["post"],
        url_path="registrar-diagnostico"
    )
    def registrar_diagnostico(
        self,
        request,
        pk=None
    ):

        if not tiene_permiso(
            request.user,
            "REALIZAR_INSPECCION_DIAGNOSTICO"
        ):

            return respuesta_sin_permiso(
                "REALIZAR_INSPECCION_DIAGNOSTICO"
            )


        ticket = self.get_object()


        if not validar_estado_ticket(ticket, ["ASIGNADO", "EN_DIAGNOSTICO"]):

            if validar_estado_ticket(ticket, ["EN_EJECUCION"]) and ticket.diagnostico:
                return respuesta_ticket(
                    ticket,
                    "El diagnóstico ya fue registrado correctamente.",
                )

            return Response(
                {
                    "detalle": (
                        "El ticket debe estar asignado o en diagnóstico. "
                        f"Estado actual: {ticket.estado.nombre}."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        if not (
            es_admin(
                request.user
            )
            or
            ticket.tecnico_asignado_id
            ==
            request.user.id
        ):

            return Response(
                {
                    "detalle": (
                        "Solo el especialista asignado "
                        "puede registrar el diagnóstico."
                    )
                },
                status=
                    status.HTTP_403_FORBIDDEN
            )


        diagnostico = (
            str(
                request.data.get(
                    "diagnostico",
                    ""
                )
            )
            .strip()
        )


        plan_solucion = (
            str(
                request.data.get(
                    "plan_solucion",
                    ""
                )
            )
            .strip()
        )


        if not diagnostico:

            return Response(
                {
                    "diagnostico":
                        "Debe registrar el diagnóstico."
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        estado_ejecucion = obtener_estado(
            "EN_EJECUCION"
        )


        if not estado_ejecucion:

            return Response(
                {
                    "detalle": (
                        "No existe el estado "
                        "EN_EJECUCION."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        ahora = timezone.now()


        ticket.diagnostico = diagnostico

        ticket.plan_solucion = (
            plan_solucion
        )

        ticket.observaciones_diagnostico = str(
            request.data.get("observaciones_diagnostico", "")
        ).strip()

        if "requiere_compra" in request.data:
            valor_compra = request.data.get("requiere_compra")
            if isinstance(valor_compra, str):
                valor_compra = valor_compra.lower() in {"true", "1", "si", "sí"}
            ticket.requiere_compra = bool(valor_compra)

        evidencia_diagnostico = request.FILES.get("evidencia_diagnostico")
        if evidencia_diagnostico:
            ticket.evidencia_diagnostico = evidencia_diagnostico

        ticket.estado = (
            estado_ejecucion
        )

        if not ticket.inicio_atencion_en:
            ticket.inicio_atencion_en = ahora


        ticket.save(
            update_fields=[
                "diagnostico",
                "plan_solucion",
                "observaciones_diagnostico",
                "requiere_compra",
                "evidencia_diagnostico",
                "estado",
                "inicio_atencion_en",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion="REALIZAR_INSPECCION_DIAGNOSTICO",
            modulo="Soporte Técnico",
            detalle=(
                f"Se registró la inspección y "
                f"diagnóstico del ticket "
                f"{ticket.codigo}."
            ),
            nivel="INFO",
        )


        return respuesta_ticket(
            ticket,
            "Inspección y diagnóstico registrados correctamente."
        )


    # ======================================================
    # 4.b SOLICITAR REQUERIMIENTO DE COMPONENTE (Especialista)
    # ======================================================
    #
    # BPMN: "¿Requiere compra?" -> SÍ -> "Realizar
    # requerimiento" (Especialistas), con las características
    # del componente y su cotización. Este paso solo levanta
    # el pedido; todavía no genera ningún expediente de
    # compra — eso depende de que Jefe UTIC lo evalúe como
    # viable en el siguiente paso.
    #
    # ======================================================

    @action(detail=True, methods=["post"], url_path="guardar-borrador-requerimiento")
    def guardar_borrador_requerimiento(self, request, pk=None):
        if not tiene_permiso(request.user, "SOLICITAR_REQUERIMIENTO_COMPONENTE"):
            return respuesta_sin_permiso("SOLICITAR_REQUERIMIENTO_COMPONENTE")

        ticket = self.get_object()
        if not validar_estado_ticket(ticket, ["EN_EJECUCION"]):
            return Response(
                {"detalle": "El ticket debe encontrarse EN_EJECUCION."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if not (es_admin(request.user) or ticket.tecnico_asignado_id == request.user.id):
            return Response(
                {"detalle": "Solo el especialista asignado puede guardar el borrador."},
                status=status.HTTP_403_FORBIDDEN,
            )
        if ticket.estado_compra_componente not in ["", "BORRADOR"]:
            return Response(
                {"detalle": "El requerimiento ya fue enviado y no puede editarse."},
                status=status.HTTP_409_CONFLICT,
            )

        ticket.requiere_compra = True
        ticket.estado_compra_componente = "BORRADOR"
        ticket.componente_requerido = str(request.data.get("componente_requerido", "")).strip()
        ticket.especificaciones_tecnicas = str(request.data.get("especificaciones_tecnicas", "")).strip()
        ticket.justificacion_compra = str(request.data.get("justificacion_compra", "")).strip()
        ticket.proveedor_cotizacion = str(request.data.get("proveedor_cotizacion", "")).strip()
        try:
            ticket.cantidad_componente = max(1, int(request.data.get("cantidad_componente") or 1))
            costo = request.data.get("costo_estimado")
            ticket.costo_estimado = Decimal(str(costo)) if costo not in (None, "") else None
        except (ValueError, TypeError, InvalidOperation):
            return Response({"detalle": "Cantidad o costo estimado inválido."}, status=status.HTTP_400_BAD_REQUEST)
        if request.FILES.get("informe_compra"):
            ticket.informe_compra = request.FILES["informe_compra"]
        cotizacion = request.FILES.get("cotizacion_archivo")
        if cotizacion:
            ticket.cotizacion_archivo = cotizacion
        ticket.save(update_fields=[
            "requiere_compra", "estado_compra_componente", "componente_requerido",
            "especificaciones_tecnicas", "justificacion_compra", "proveedor_cotizacion",
            "cantidad_componente", "costo_estimado", "cotizacion_archivo", "informe_compra", "actualizado_en",
        ])
        registrar_bitacora(
            request=request, accion="BORRADOR_REQUERIMIENTO_COMPONENTE",
            modulo="Soporte Técnico", detalle=f"Se guardó el borrador de compra del ticket {ticket.codigo}.",
            nivel="INFO",
        )
        return respuesta_ticket(ticket, "Borrador de requerimiento guardado.")

    @action(
        detail=True,
        methods=["post"],
        url_path="solicitar-requerimiento-componente"
    )
    def solicitar_requerimiento_componente(
        self,
        request,
        pk=None
    ):

        if not tiene_permiso(
            request.user,
            "SOLICITAR_REQUERIMIENTO_COMPONENTE"
        ):

            return respuesta_sin_permiso(
                "SOLICITAR_REQUERIMIENTO_COMPONENTE"
            )


        ticket = self.get_object()


        if not validar_estado_ticket(
            ticket,
            ["EN_EJECUCION"]
        ):

            return Response(
                {
                    "detalle": (
                        "El ticket debe encontrarse "
                        "EN_EJECUCION."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )


        if not (
            es_admin(request.user)
            or
            ticket.tecnico_asignado_id == request.user.id
        ):

            return Response(
                {
                    "detalle": (
                        "Solo el especialista asignado "
                        "puede solicitar el componente."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )


        if ticket.estado_compra_componente not in ["", "BORRADOR"]:

            return Response(
                {
                    "detalle": (
                        "Este ticket ya tiene un "
                        "requerimiento de componente "
                        "en curso."
                    )
                },
                status=status.HTTP_409_CONFLICT
            )


        componente = str(request.data.get("componente_requerido", "")).strip()
        especificaciones = str(request.data.get("especificaciones_tecnicas", "")).strip()
        justificacion = str(request.data.get("justificacion_compra", "")).strip()
        proveedor = str(request.data.get("proveedor_cotizacion", "")).strip()

        if not componente:

            return Response(
                {"componente_requerido": "Debe indicar el componente requerido."},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not especificaciones:
            return Response(
                {"especificaciones_tecnicas": "Debe registrar las características técnicas."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not justificacion:
            return Response(
                {"justificacion_compra": "Debe justificar el requerimiento."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            cantidad = int(request.data.get("cantidad_componente") or 1)
            if cantidad < 1:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {"cantidad_componente": "La cantidad debe ser mayor a cero."},
                status=status.HTTP_400_BAD_REQUEST,
            )


        costo_estimado = request.data.get("costo_estimado")

        try:
            costo_estimado = (
                Decimal(str(costo_estimado))
                if costo_estimado not in (None, "")
                else None
            )

        except InvalidOperation:

            return Response(
                {"costo_estimado": "Monto estimado inválido."},
                status=status.HTTP_400_BAD_REQUEST
            )


        ticket.requiere_compra = True
        ticket.cantidad_componente = cantidad
        ticket.componente_requerido = componente
        ticket.especificaciones_tecnicas = especificaciones
        ticket.justificacion_compra = justificacion
        ticket.proveedor_cotizacion = proveedor
        ticket.costo_estimado = costo_estimado
        cotizacion_compra = request.FILES.get("cotizacion_archivo") or ticket.cotizacion_archivo
        if not cotizacion_compra:
            return Response({"detalle": "Adjunte la cotización antes de enviar a jefatura."}, status=400)
        ticket.informe_compra.save(
            f"informe-requerimiento-{ticket.codigo}.pdf",
            ContentFile(informe_requerimiento(ticket)),
            save=False,
        )
        ticket.estado_compra_componente = "SOLICITADA"

        # BPMN: el requerimiento viaja con su cotización adjunta.
        cotizacion = request.FILES.get("cotizacion_archivo")

        if cotizacion:
            ticket.cotizacion_archivo = cotizacion

        ticket.save(
            update_fields=[
                "requiere_compra",
                "cantidad_componente",
                "componente_requerido",
                "especificaciones_tecnicas",
                "justificacion_compra",
                "proveedor_cotizacion",
                "costo_estimado",
                "estado_compra_componente",
                "cotizacion_archivo", "informe_compra",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion="SOLICITAR_REQUERIMIENTO_COMPONENTE",
            modulo="Soporte Técnico",
            detalle=(
                f"Se solicitó el componente '{componente}' "
                f"con cotización para el ticket "
                f"{ticket.codigo}. Pendiente de evaluación "
                f"de viabilidad por Jefe UTIC."
            ),
            nivel="INFO",
        )


        return respuesta_ticket(
            ticket,
            "Requerimiento de componente enviado a Jefe UTIC para evaluar viabilidad."
        )


    # ======================================================
    # 4.c EVALUAR VIABILIDAD DE COMPRA (Jefe UTIC)
    # ======================================================
    #
    # BPMN: "Recibir requerimiento y cotización" ->
    # "¿Es viable la compra?" -> NO: "Comunicar no
    # viabilidad" / "Cerrado sin compra". SÍ: "Elevar el
    # informe" y generar el expediente, que a partir de ahí
    # sigue el subproceso normal de Compra Caja Chica —
    # incluido el visto bueno del Director ya implementado
    # en ese módulo (no se duplica acá).
    #
    # ======================================================

    @action(detail=True, methods=["post"], url_path="completar-expediente")
    def completar_expediente(self, request, pk=None):
        if not tiene_permiso(request.user, "AUTORIZAR_SOLICITUD_COMPRA_TI"):
            return Response({"detalle": "Solo la jefatura de la sección puede completar el expediente."}, status=403)
        from compras.expediente import completar_expediente_origen
        return completar_expediente_origen(request, self.get_object(), "ticket_soporte")

    @action(detail=True, methods=["get"], url_path="informe-requerimiento-pdf")
    def informe_requerimiento_pdf(self, request, pk=None):
        from compras.informes_origen import visualizar_informe_tecnico
        return visualizar_informe_tecnico(self.get_object())

    @action(detail=True, methods=["post"], url_path="validar-viabilidad-compra")
    def validar_viabilidad_compra(self, request, pk=None):
        if not tiene_permiso(request.user, "AUTORIZAR_SOLICITUD_COMPRA_TI"):
            return respuesta_sin_permiso("AUTORIZAR_SOLICITUD_COMPRA_TI")
        ticket = self.get_object()
        if ticket.estado_compra_componente != "SOLICITADA" or ticket.codigo_compra_vinculada:
            return Response({"detalle": "La compra no está pendiente de validación."}, status=400)
        from compras.informes_origen import asegurar_informe_tecnico
        asegurar_informe_tecnico(ticket)
        if not ticket.cotizacion_archivo:
            return Response({"detalle": "El requerimiento del técnico debe incluir su informe generado y la cotización."}, status=400)
        ticket.estado_compra_componente = "VIABLE"
        ticket.save(update_fields=["estado_compra_componente", "actualizado_en"])
        return Response({"mensaje": "Viabilidad validada. Adjunte el POA y el proveído para elevar la compra."})

    @action(
        detail=True,
        methods=["post"],
        url_path="evaluar-viabilidad-compra"
    )
    def evaluar_viabilidad_compra(
        self,
        request,
        pk=None
    ):

        if not tiene_permiso(
            request.user,
            "AUTORIZAR_SOLICITUD_COMPRA_TI"
        ):

            return respuesta_sin_permiso(
                "AUTORIZAR_SOLICITUD_COMPRA_TI"
            )


        ticket = self.get_object()


        if ticket.estado_compra_componente not in ["SOLICITADA", "VIABLE"]:

            return Response(
                {
                    "detalle": (
                        "Este ticket no tiene un "
                        "requerimiento de componente "
                        "pendiente de evaluación o validación final."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )


        viable = request.data.get("viable")
        if isinstance(viable, str):
            viable = {"true": True, "false": False}.get(viable.lower())

        if viable not in [True, False]:

            return Response(
                {"viable": "Debe indicar True o False."},
                status=status.HTTP_400_BAD_REQUEST
            )


        # --------------------------------------------------
        # NO ES VIABLE -> cerrado sin compra
        # --------------------------------------------------

        if viable is False:

            motivo = str(request.data.get("motivo_no_viable", "")).strip()

            if not motivo:

                return Response(
                    {
                        "motivo_no_viable": (
                            "Debe indicar el motivo de "
                            "no viabilidad."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )


            estado_cerrado_sin_compra = obtener_estado(
                "CERRADO_SIN_COMPRA"
            )

            if not estado_cerrado_sin_compra:

                return Response(
                    {
                        "detalle": (
                            "No existe el estado "
                            "CERRADO_SIN_COMPRA."
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )


            ticket.estado_compra_componente = "NO_VIABLE"
            ticket.motivo_no_viable = motivo
            ticket.estado = estado_cerrado_sin_compra
            ticket.activo = False

            # Si el expediente ya fue creado pero aún estaba incompleto,
            # se conserva para auditoría y se anula; nunca se elimina.
            if ticket.codigo_compra_vinculada:
                from compras.models import SolicitudCompra
                solicitud = SolicitudCompra.objects.filter(
                    codigo=ticket.codigo_compra_vinculada
                ).first()
                if solicitud and solicitud.estado not in [
                    "COMPRA_REGISTRADA",
                    "COMPRADO_Y_ENTREGADO",
                    "DESCARGO_PENDIENTE_LIQUIDACION",
                    "CERRADO_ARCHIVADO",
                ]:
                    solicitud.estado = "ANULADO"
                    solicitud.motivo_rechazo = motivo
                    solicitud.save(
                        update_fields=["estado", "motivo_rechazo", "actualizado_en"]
                    )

            ticket.save(
                update_fields=[
                    "estado_compra_componente",
                    "motivo_no_viable",
                    "estado",
                    "activo",
                    "actualizado_en",
                ]
            )

            crear_notificacion(
                ticket.tecnico_asignado, ticket, "RECHAZO",
                f"{ticket.codigo} · Compra no viable",
                motivo,
            )


            registrar_bitacora(
                request=request,
                accion="EVALUAR_VIABILIDAD_COMPRA",
                modulo="Soporte Técnico",
                detalle=(
                    f"Se determinó que la compra para el "
                    f"ticket {ticket.codigo} no es viable: "
                    f"{motivo}"
                ),
                nivel="WARNING",
            )


            return respuesta_ticket(
                ticket,
                "Compra no viable. El ticket se cerró sin compra."
            )


        # --------------------------------------------------
        # ES VIABLE -> generar expediente de compra
        # --------------------------------------------------

        # Import local para evitar dependencia circular a nivel
        # de módulo entre soporte y compras.
        from compras.models import SolicitudCompra

        from compras.informes_origen import asegurar_informe_tecnico
        informe = asegurar_informe_tecnico(ticket)
        proforma = ticket.cotizacion_archivo
        poa = request.FILES.get("poa")
        pedido = request.FILES.get("pedido")
        if not all((informe, proforma, poa, pedido)):
            return Response({"detalle": "Para elevar a DAF se requieren informe técnico, cotización, POA y proveído de jefatura."}, status=400)

        solicitud = SolicitudCompra.objects.create(
            codigo=SolicitudCompra.generar_codigo(),
            titulo=f"Componente para ticket {ticket.codigo}",
            descripcion=ticket.especificaciones_tecnicas or ticket.componente_requerido,
            solicitante=ticket.tecnico_asignado or ticket.solicitante,
            area=ticket.area,
            tipo="COMPONENTE",
            cantidad=ticket.cantidad_componente,
            especificaciones=ticket.especificaciones_tecnicas or ticket.componente_requerido,
            justificacion=ticket.justificacion_compra or f"Requerido para atender el ticket de soporte {ticket.codigo}.",
            monto_estimado=ticket.costo_estimado,
            estado="CREADO_PENDIENTE_DAF",
            origen_modulo="SOPORTE",
            ticket_soporte=ticket,
            informe=informe, proforma=proforma, poa=poa, pedido=pedido,
        )

        ticket.estado_compra_componente = "VIABLE"
        ticket.codigo_compra_vinculada = solicitud.codigo

        ticket.save(
            update_fields=[
                "estado_compra_componente",
                "codigo_compra_vinculada",
                "actualizado_en",
            ]
        )

        crear_notificacion(
            ticket.tecnico_asignado, ticket, "EXITO",
            f"{ticket.codigo} · Compra aprobada",
            f"Jefatura UTIC aprobó el requerimiento. Se generó el expediente {solicitud.codigo}.",
        )


        registrar_bitacora(
            request=request,
            accion="AUTORIZAR_SOLICITUD_COMPRA_TI",
            modulo="Soporte Técnico",
            detalle=(
                f"Se autorizó la compra de "
                f"'{ticket.componente_requerido}' "
                f"para el ticket {ticket.codigo}. "
                f"Expediente vinculado: {solicitud.codigo}."
            ),
            nivel="INFO",
        )


        return respuesta_ticket(
            ticket,
            f"Solicitud de compra {solicitud.codigo} generada y vinculada al ticket."
        )


    # ======================================================
    # 5. REALIZAR REPARACIÓN O INSTALACIÓN Y REGISTRAR
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="registrar-intervencion"
    )
    def registrar_intervencion(
        self,
        request,
        pk=None
    ):

        if not tiene_permiso(
            request.user,
            "REALIZAR_REPARACION_INSTALACION"
        ):

            return respuesta_sin_permiso(
                "REALIZAR_REPARACION_INSTALACION"
            )


        ticket = self.get_object()


        if not validar_estado_ticket(
            ticket,
            ["EN_EJECUCION"]
        ):

            return Response(
                {
                    "detalle": (
                        "El ticket debe encontrarse "
                        "EN_EJECUCION."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        if not (
            es_admin(
                request.user
            )
            or
            ticket.tecnico_asignado_id
            ==
            request.user.id
        ):

            return Response(
                {
                    "detalle": (
                        "Solo el especialista asignado "
                        "puede registrar la intervención."
                    )
                },
                status=
                    status.HTTP_403_FORBIDDEN
            )


        if ticket.estado_compra_componente == "SOLICITADA":

            return Response(
                {
                    "detalle": (
                        "El ticket tiene un requerimiento "
                        "de componente pendiente de "
                        "evaluación de viabilidad por "
                        "Jefe UTIC."
                    )
                },
                status=status.HTTP_409_CONFLICT
            )

        # El flujo técnico permanece en pausa mientras el componente
        # recorre el subproceso de compra: solo se reanuda cuando
        # Almacén registra el despacho (estado ENTREGADA).
        if ticket.estado_compra_componente == "VIABLE":

            return Response(
                {
                    "detalle": (
                        "El componente todavía no fue entregado por "
                        "Almacén. El expediente de compra "
                        f"{ticket.codigo_compra_vinculada or 'vinculado'} "
                        "sigue en proceso."
                    )
                },
                status=status.HTTP_409_CONFLICT
            )


        solucion = (
            str(
                request.data.get(
                    "solucion",
                    ""
                )
            )
            .strip()
        )


        if not solucion:

            return Response(
                {
                    "solucion": (
                        "Debe registrar la reparación, "
                        "instalación o intervención realizada."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        ticket.solucion = solucion

        ticket.acciones_realizadas = str(
            request.data.get("acciones_realizadas", "")
        ).strip()
        ticket.componentes_utilizados = str(
            request.data.get("componentes_utilizados", "")
        ).strip()
        evidencia_intervencion = request.FILES.get("evidencia_intervencion")
        if evidencia_intervencion:
            ticket.evidencia_intervencion = evidencia_intervencion


        ticket.save(
            update_fields=[
                "solucion",
                "acciones_realizadas",
                "componentes_utilizados",
                "evidencia_intervencion",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion="REALIZAR_REPARACION_INSTALACION",
            modulo="Soporte Técnico",
            detalle=(
                f"Se registró la intervención "
                f"del ticket {ticket.codigo}."
            ),
            nivel="INFO",
        )


        return respuesta_ticket(
            ticket,
            "Intervención técnica registrada correctamente."
        )


    # ======================================================
    # 6. REALIZAR PRUEBAS TÉCNICAS
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="pruebas-tecnicas"
    )
    @documentar('Informe técnico de soporte', firma_obligatoria=True)
    def pruebas_tecnicas(
        self,
        request,
        pk=None
    ):

        if not tiene_permiso(
            request.user,
            "REALIZAR_PRUEBAS_TECNICAS"
        ):

            return respuesta_sin_permiso(
                "REALIZAR_PRUEBAS_TECNICAS"
            )


        ticket = self.get_object()


        if not validar_estado_ticket(
            ticket,
            ["EN_EJECUCION"]
        ):

            return Response(
                {
                    "detalle": (
                        "El ticket debe encontrarse "
                        "EN_EJECUCION."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        if not ticket.solucion:

            return Response(
                {
                    "detalle": (
                        "Primero debe registrar "
                        "la intervención técnica."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        resultado = (
            str(
                request.data.get(
                    "resultado_pruebas",
                    ""
                )
            )
            .strip()
        )


        if not resultado:

            return Response(
                {
                    "resultado_pruebas": (
                        "Debe registrar el resultado "
                        "de las pruebas técnicas."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )

        funciona_tecnicamente = request.data.get("funciona_tecnicamente", True)
        if isinstance(funciona_tecnicamente, str):
            normalizado = funciona_tecnicamente.strip().lower()
            funciona_tecnicamente = True if normalizado in {"true", "1", "si", "sí"} else False if normalizado in {"false", "0", "no"} else funciona_tecnicamente
        if funciona_tecnicamente not in [True, False]:
            return Response(
                {"funciona_tecnicamente": "Debe indicar True o False."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if funciona_tecnicamente is False:
            ticket.resultado_pruebas = resultado
            ticket.rework_count += 1
            evidencia_pruebas = request.FILES.get("evidencia_pruebas")
            if evidencia_pruebas:
                ticket.evidencia_pruebas = evidencia_pruebas
            ticket.save(update_fields=[
                "resultado_pruebas", "rework_count", "evidencia_pruebas", "actualizado_en",
            ])
            registrar_bitacora(
                request=request, accion="PRUEBAS_TECNICAS_NO_CONFORMES",
                modulo="Soporte Técnico",
                detalle=f"Las pruebas del ticket {ticket.codigo} no fueron satisfactorias; continúa en ejecución.",
                nivel="WARNING",
            )
            return respuesta_ticket(ticket, "Pruebas no satisfactorias. La orden continúa en atención técnica.")


        estado_verificacion = obtener_estado(
            "PENDIENTE_CONFORMIDAD"
        )


        if not estado_verificacion:

            return Response(
                {
                    "detalle": (
                        "No existe el estado "
                        "PENDIENTE_CONFORMIDAD."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        ahora = timezone.now()


        ticket.resultado_pruebas = (
            resultado
        )

        # BPMN: "Registrar informe al Jefe de UTIC". Es el descargo del
        # especialista, distinto del informe final que la jefatura
        # elabora y valida una vez cerrado el ticket.
        informe_tecnico = (
            str(
                request.data.get(
                    "informe_tecnico",
                    ""
                )
            )
            .strip()
        )

        if not informe_tecnico:
            return Response(
                {"informe_tecnico": "Debe registrar el informe técnico."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ticket.informe_tecnico = informe_tecnico

        ticket.informe_tecnico_pdf.save(
            f"informe-tecnico-{ticket.codigo}.pdf",
            ContentFile(generar_informe_tecnico(ticket, informe_tecnico, validar_firma(request.data.get("firma")), request.user.nombre_completo)),
            save=False,
        )

        evidencia_pruebas = request.FILES.get("evidencia_pruebas")
        if evidencia_pruebas:
            ticket.evidencia_pruebas = evidencia_pruebas

        ticket.estado = (
            estado_verificacion
        )

        ticket.pruebas_en = (
            ahora
        )


        ticket.save(
            update_fields=[
                "resultado_pruebas",
                "informe_tecnico",
                "informe_tecnico_pdf",
                "evidencia_pruebas",
                "estado",
                "pruebas_en",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion="REALIZAR_PRUEBAS_TECNICAS",
            modulo="Soporte Técnico",
            detalle=(
                f"Se registraron las pruebas y el informe técnico "
                f"del ticket {ticket.codigo}. Quedó pendiente de "
                "verificación por el solicitante."
            ),
            nivel="INFO",
        )


        return respuesta_ticket(
            ticket,
            "Informe técnico enviado. Pendiente de conformidad del solicitante."
        )


    # ======================================================
    # 7. VERIFICAR FUNCIONAMIENTO
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="verificar-funcionamiento"
    )
    def verificar_funcionamiento(
        self,
        request,
        pk=None
    ):

        if not tiene_permiso(
            request.user,
            "VERIFICAR_FUNCIONAMIENTO"
        ):

            return respuesta_sin_permiso(
                "VERIFICAR_FUNCIONAMIENTO"
            )


        ticket = self.get_object()

        if ticket.solicitante_id != request.user.id:
            return Response(
                {"detalle": "Solo el solicitante propietario puede verificar este ticket."},
                status=status.HTTP_403_FORBIDDEN,
            )


        if not validar_estado_ticket(
            ticket,
            ["EN_VERIFICACION"]
        ):

            return Response(
                {
                    "detalle": (
                        "El ticket debe encontrarse "
                        "EN_VERIFICACION."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        funciona = request.data.get(
            "funciona_correctamente"
        )


        if funciona not in [
            True,
            False,
        ]:

            return Response(
                {
                    "funciona_correctamente": (
                        "Debe indicar True o False."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        ahora = timezone.now()


        # --------------------------------------------------
        # NO CONFORME TÉCNICAMENTE
        # --------------------------------------------------

        if funciona is False:

            estado_ejecucion = obtener_estado(
                "EN_EJECUCION"
            )


            if not estado_ejecucion:

                return Response(
                    {
                        "detalle": (
                            "No existe el estado "
                            "EN_EJECUCION."
                        )
                    },
                    status=
                        status.HTTP_400_BAD_REQUEST
                )


            ticket.rework_count += 1

            ticket.estado = (
                estado_ejecucion
            )

            ticket.verificado_en = (
                ahora
            )


            ticket.save(
                update_fields=[
                    "rework_count",
                    "estado",
                    "verificado_en",
                    "actualizado_en",
                ]
            )


            registrar_bitacora(
                request=request,
                accion="VERIFICACION_NO_CONFORME",
                modulo="Soporte Técnico",
                detalle=(
                    f"El ticket {ticket.codigo} "
                    f"requiere nueva intervención."
                ),
                nivel="WARNING",
            )


            return respuesta_ticket(
                ticket,
                (
                    "La verificación no fue conforme. "
                    "El ticket volvió a ejecución."
                )
            )


        # --------------------------------------------------
        # FUNCIONAMIENTO CORRECTO
        # --------------------------------------------------

        estado_conformidad = obtener_estado(
            "PENDIENTE_CONFORMIDAD"
        )


        if not estado_conformidad:

            return Response(
                {
                    "detalle": (
                        "No existe el estado "
                        "PENDIENTE_CONFORMIDAD."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        ticket.estado = (
            estado_conformidad
        )

        ticket.verificado_en = (
            ahora
        )


        ticket.save(
            update_fields=[
                "estado",
                "verificado_en",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion="VERIFICAR_FUNCIONAMIENTO",
            modulo="Soporte Técnico",
            detalle=(
                f"Se verificó el funcionamiento "
                f"del ticket {ticket.codigo}. "
                f"Pendiente de conformidad."
            ),
            nivel="INFO",
        )


        return respuesta_ticket(
            ticket,
            (
                "Funcionamiento verificado. "
                "El ticket quedó pendiente "
                "de conformidad del solicitante."
            )
        )


    # ======================================================
    # 8. INFORMAR CONFORMIDAD
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="informar-conformidad"
    )
    @documentar('Conformidad del solicitante', solo_conforme=True, permitir_firma=False)
    def informar_conformidad(
        self,
        request,
        pk=None
    ):

        ticket = self.get_object()


        if (
            ticket.solicitante_id
            !=
            request.user.id
        ):

            return Response(
                {
                    "detalle": (
                        "Solo el solicitante del ticket "
                        "puede informar la conformidad."
                    )
                },
                status=
                    status.HTTP_403_FORBIDDEN
            )


        if not tiene_permiso(
            request.user,
            "INFORMAR_CONFORMIDAD"
        ):

            return respuesta_sin_permiso(
                "INFORMAR_CONFORMIDAD"
            )


        if not validar_estado_ticket(
            ticket,
            ["PENDIENTE_CONFORMIDAD"]
        ):

            return Response(
                {
                    "detalle": (
                        "El ticket todavía no está "
                        "pendiente de conformidad."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        conformidad = request.data.get(
            "conformidad"
        )


        observaciones = (
            str(
                request.data.get(
                    "observaciones",
                    ""
                )
            )
            .strip()
        )


        if conformidad not in [
            True,
            False,
        ]:

            return Response(
                {
                    "conformidad": (
                        "Debe indicar True o False."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        ahora = timezone.now()


        # --------------------------------------------------
        # NO CONFORMIDAD
        # --------------------------------------------------

        if conformidad is False:

            if not observaciones:
                return Response(
                    {"observaciones": "Debe indicar por qué el problema continúa."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            estado_ejecucion = obtener_estado(
                "EN_EJECUCION"
            )


            if not estado_ejecucion:

                return Response(
                    {
                        "detalle":
                            "No existe EN_EJECUCION."
                    },
                    status=
                        status.HTTP_400_BAD_REQUEST
                )


            ticket.conformidad_usuario = (
                False
            )

            ticket.observaciones_usuario = (
                observaciones
            )

            ticket.conformidad_en = (
                ahora
            )

            ticket.rework_count += 1

            ticket.estado = (
                estado_ejecucion
            )


            ticket.save(
                update_fields=[
                    "conformidad_usuario",
                    "observaciones_usuario",
                    "conformidad_en",
                    "rework_count",
                    "estado",
                    "actualizado_en",
                ]
            )


            registrar_bitacora(
                request=request,
                accion="INFORMAR_NO_CONFORMIDAD",
                modulo="Soporte Técnico",
                detalle=(
                    f"El solicitante informó "
                    f"no conformidad en "
                    f"{ticket.codigo}."
                ),
                nivel="WARNING",
            )


            return respuesta_ticket(
                ticket,
                (
                    "No conformidad registrada. "
                    "El ticket regresó a ejecución."
                )
            )


        # --------------------------------------------------
        # CONFORMIDAD
        # --------------------------------------------------

        estado_cerrado = obtener_estado(
            "PENDIENTE_INFORME_FINAL"
        )


        if not estado_cerrado:

            return Response(
                {
                    "detalle":
                        "No existe el estado PENDIENTE_INFORME_FINAL."
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        ticket.conformidad_usuario = (
            True
        )

        ticket.observaciones_usuario = (
            observaciones
        )

        ticket.conformidad_en = (
            ahora
        )

        ticket.estado = (
            estado_cerrado
        )

        ticket.sla_cumplido = (
            calcular_sla_cumplido(
                ticket,
                ahora
            )
        )


        ticket.save(
            update_fields=[
                "conformidad_usuario",
                "observaciones_usuario",
                "conformidad_en",
                "estado",
                "sla_cumplido",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion="INFORMAR_CONFORMIDAD",
            modulo="Soporte Técnico",
            detalle=(
                f"El solicitante informó "
                f"conformidad en el ticket {ticket.codigo}. "
                "Quedó pendiente de informe final. "
                f"SLA cumplido: "
                f"{ticket.sla_cumplido}."
            ),
            nivel="INFO",
        )


        return respuesta_ticket(
            ticket,
            "Conformidad registrada. Ticket pendiente de informe final."
        )


    # ======================================================
    # 10. RECIBIR INFORME DE ACTIVIDADES
    # ======================================================
    #
    # BPMN: la jefatura eleva el informe y la Dirección lo recibe.
    # Con ese acuse el proceso del ticket llega a su evento final.
    #
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="recibir-informe"
    )
    def recibir_informe(
        self,
        request,
        pk=None
    ):

        if not tiene_permiso(
            request.user,
            "RECIBIR_INFORME_ACTIVIDADES"
        ):

            return respuesta_sin_permiso(
                "RECIBIR_INFORME_ACTIVIDADES"
            )


        ticket = self.get_object()


        if not ticket.informe_elevado_en:

            return Response(
                {
                    "detalle": (
                        "La jefatura todavía no elevó el informe "
                        "final de este ticket."
                    )
                },
                status=status.HTTP_409_CONFLICT
            )


        roles = obtener_roles(request.user)

        if not (
            "DIRECTOR" in roles
            or es_admin(request.user)
        ):

            return Response(
                {
                    "detalle": (
                        "Solo la Dirección puede recibir el informe "
                        "de actividades."
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )


        if ticket.informe_recibido_director_en:

            return Response(
                {"detalle": "Usted ya recibió este informe."},
                status=status.HTTP_409_CONFLICT
            )


        ahora = timezone.now()

        ticket.informe_recibido_director_en = ahora
        ticket.proceso_finalizado_en = ahora

        ticket.save(
            update_fields=[
                "informe_recibido_director_en",
                "proceso_finalizado_en",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion="RECIBIR_INFORME_ACTIVIDADES",
            modulo="Soporte Técnico",
            detalle=(
                f"La Dirección recibió el informe de actividades del "
                f"ticket {ticket.codigo}."
            ),
            nivel="INFO",
        )


        if ticket.proceso_finalizado_en:

            registrar_bitacora(
                request=request,
                accion="FINALIZAR_PROCESO_TICKET",
                modulo="Soporte Técnico",
                detalle=(
                    f"El informe del ticket {ticket.codigo} fue recibido: "
                    "el proceso quedó formalmente cerrado."
                ),
                nivel="INFO",
            )


        return respuesta_ticket(
            ticket,
            (
                "Informe recibido. El proceso del ticket quedó cerrado."
                if ticket.proceso_finalizado_en
                else "Informe recibido correctamente."
            )
        )


    # ======================================================
    # 9. ELABORAR Y VALIDAR INFORME FINAL
    # ======================================================
    #
    # BPMN: "Elaborar y enviar informe final" (Líder de TI),
    # último paso antes de archivar el expediente del ticket.
    #
    # ======================================================

    @action(
        detail=True,
        methods=["post"],
        url_path="elaborar-informe-final"
    )
    @documentar('Informe final de soporte', firma_obligatoria=True)
    def elaborar_informe_final(
        self,
        request,
        pk=None
    ):

        if not tiene_permiso(
            request.user,
            "ELABORAR_VALIDAR_INFORME_FINAL"
        ):

            return respuesta_sin_permiso(
                "ELABORAR_VALIDAR_INFORME_FINAL"
            )


        ticket = self.get_object()


        if not validar_estado_ticket(
            ticket,
            ["PENDIENTE_INFORME_FINAL", "CERRADO"]
        ):

            return Response(
                {
                    "detalle": (
                        "El ticket debe tener conformidad del solicitante "
                        "antes de elaborar el informe final."
                    )
                },
                status=
                    status.HTTP_400_BAD_REQUEST
            )


        informe = str(request.data.get("informe_final", "")).strip()

        if not informe:

            return Response(
                {"informe_final": "Debe elaborar el informe final."},
                status=status.HTTP_400_BAD_REQUEST
            )

        campos_tecnicos = {
            "diagnóstico": ticket.diagnostico,
            "plan de solución": ticket.plan_solucion,
            "intervención realizada": ticket.solucion,
            "resultado de pruebas": ticket.resultado_pruebas,
            "informe del técnico": ticket.informe_tecnico,
        }
        faltantes = [
            nombre for nombre, valor in campos_tecnicos.items()
            if not str(valor or "").strip()
        ]
        if faltantes:
            return Response(
                {"detalle": "No se puede elevar un informe incompleto. Falta: " + ", ".join(faltantes) + "."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ahora = timezone.now()

        estado_cerrado = obtener_estado("CERRADO")

        if not estado_cerrado:
            return Response(
                {"detalle": "No existe el estado CERRADO."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        from usuarios.models import DocumentoProceso
        if ticket.conformidad_usuario is not True:
            return Response({'detalle': 'El solicitante debe registrar su conformidad.'}, status=status.HTTP_400_BAD_REQUEST)
        if not DocumentoProceso.objects.filter(soporte=ticket, tipo='Informe técnico de soporte', usuario_id=ticket.tecnico_asignado_id).exclude(firma=[]).exists():
            return Response({'detalle': 'El técnico debe firmar su informe antes de elevar el informe final.'}, status=status.HTTP_400_BAD_REQUEST)
        ticket.informe_final = informe
        ticket.informe_final_pdf.save(
            f"informe-final-{ticket.codigo}.pdf",
            ContentFile(informe_final_jefatura(ticket, informe, validar_firma(request.data.get("firma")), request.user.nombre_completo)),
            save=False,
        )
        ticket.estado = estado_cerrado
        ticket.cerrado_en = ahora

        # BPMN: tras validar el informe, la jefatura lo eleva y una
        # compuerta paralela lo distribuye al Director y al Jefe de
        # carrera. El proceso solo termina cuando ambos lo reciben.
        ticket.informe_elevado_en = ahora

        ticket.save(
            update_fields=[
                "informe_final",
                "informe_final_pdf",
                "estado",
                "cerrado_en",
                "informe_elevado_en",
                "actualizado_en",
            ]
        )


        registrar_bitacora(
            request=request,
            accion="ELABORAR_VALIDAR_INFORME_FINAL",
            modulo="Soporte Técnico",
            detalle=f"Se elaboró y validó el informe final del ticket {ticket.codigo}.",
            nivel="INFO",
        )


        registrar_bitacora(
            request=request,
            accion="ELEVAR_INFORME_ACTIVIDADES",
            modulo="Soporte Técnico",
            detalle=(
                f"El informe final del ticket {ticket.codigo} fue elevado "
                "a la Dirección para su conocimiento."
            ),
            nivel="INFO",
        )


        return respuesta_ticket(
            ticket,
            "Informe final validado y elevado a la Dirección."
        )

    @action(detail=True, methods=["post"], url_path="elaborar-informe-jefe-carrera")
    def elaborar_informe_jefe_carrera(self, request, pk=None):
        ticket = self.get_object()
        if not (es_admin(request.user) or ticket.solicitante_id == request.user.id):
            return Response({"detalle": "Solo el solicitante responsable puede elaborar este informe."}, status=403)
        if not ticket.informe_final_pdf:
            return Response({"detalle": "Jefatura UTIC todavía no elevó el informe final."}, status=409)
        if ticket.informe_jefe_carrera_en:
            return Response({"detalle": "El informe del jefe de carrera ya fue enviado."}, status=409)
        contenido = str(request.data.get("informe_jefe_carrera", "")).strip()
        if not contenido:
            return Response({"informe_jefe_carrera": "Debe completar el informe final."}, status=400)
        ticket.informe_jefe_carrera = contenido
        ticket.informe_jefe_carrera_pdf.save(
            f"informe-jefe-carrera-{ticket.codigo}.pdf",
            ContentFile(informe_jefe_carrera(ticket, contenido)), save=False,
        )
        ticket.informe_jefe_carrera_en = timezone.now()
        ticket.save(update_fields=["informe_jefe_carrera", "informe_jefe_carrera_pdf", "informe_jefe_carrera_en", "actualizado_en"])
        registrar_bitacora(request=request, accion="ELEVAR_INFORME_JEFE_CARRERA", modulo="Soporte Técnico", detalle=f"Se elevó a Dirección el informe del jefe de carrera del ticket {ticket.codigo}.", nivel="INFO")
        return respuesta_ticket(ticket, "Informe del jefe de carrera generado y enviado a Dirección.")
