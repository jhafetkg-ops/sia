from django.core.management.base import BaseCommand
from django.db import transaction

from usuarios.models import (
    Rol,
    Permiso,
    RolPermiso,
    UsuarioRol,
    Area,
)


class Command(BaseCommand):

    help = (
        "Crea roles, permisos y asignaciones "
        "iniciales de SIA según los procesos definidos."
    )

    # ======================================================
    # ROLES BASE DEL SISTEMA
    # ======================================================
    #
    # IMPORTANTE:
    # - No elimina roles existentes.
    # - No elimina AUDITOR, SUPERVISOR_AREA ni AGENTE.
    # - Solo crea los roles que todavía no existan.
    #
    # ======================================================

    ROLES_BASE = [

        {
            "codigo": "ADMIN",
            "nombre": "Director",
            "descripcion": (
                "Administra usuarios, roles, permisos, áreas, "
                "auditoría y configuración general de SIA."
            ),
            "es_global": True,
        },

        {
            "codigo": "SUPERUSER",
            "nombre": "Admin",
            "descripcion": (
                "Administración técnica del sistema: usuarios, "
                "roles y permisos, auditoría, correo SMTP y "
                "preferencias. No opera los procesos de negocio "
                "(Soporte, Mantenimiento, Compras) que sí ve ADMIN."
            ),
            "es_global": True,
        },

        {
            "codigo": "SOLICITANTE",
            "nombre": "Usuario",
            "descripcion": (
                "Registra y realiza seguimiento a sus "
                "requerimientos institucionales."
            ),
            "es_global": False,
        },

        {
            "codigo": "JEFE_UTIC",
            "nombre": "Jefe UTIC",
            "descripcion": (
                "Recibe y valida tickets, clasifica prioridad "
                "y SLA y designa especialistas responsables."
            ),
            "es_global": True,
        },

        {
            "codigo": "ESPECIALISTA",
            "nombre": "Técnico de Soporte Técnico",
            "descripcion": (
                "Realiza inspección técnica, diagnóstico, "
                "reparación, instalación y pruebas técnicas."
            ),
            "es_global": False,
        },

        {
            "codigo": "SERVICIOS_GENERALES",
            "nombre": "Jefe Mantenimiento",
            "descripcion": (
                "Recibe los requerimientos de mantenimiento "
                "y los deriva al auxiliar correspondiente."
            ),
            "es_global": False,
        },

        {
            "codigo": "AUXILIAR_SERVICIOS_GENERALES",
            "nombre": "Técnico de Mantenimiento",
            "descripcion": (
                "Ejecuta mantenimiento, verifica reposición "
                "de almacén y realiza informe y fotograma."
            ),
            "es_global": False,
        },

        {
            "codigo": "DAF",
            "nombre": "Dirección de Asuntos Financieros",
            "descripcion": (
                "Recibe la solicitud de compra, verifica que cumpla los "
                "requisitos (informe, proforma y POA) y, cuando cumple, "
                "emite la certificación presupuestaria."
            ),
            "es_global": True,
        },

        {
            "codigo": "TESORERIA",
            "nombre": "Técnico de Tesorería",
            "descripcion": (
                "Verifica expedientes y registra "
                "el desembolso correspondiente."
            ),
            "es_global": True,
        },

        {
            "codigo": "DIRECTOR",
            "nombre": "Director",
            "descripcion": (
                "Autoriza el gasto y registra "
                "el visto bueno correspondiente."
            ),
            "es_global": True,
        },

        {
            "codigo": "ENCARGADO_COMPRAS_ALMACEN",
            "nombre": "Técnico de Almacén y Compras",
            "descripcion": (
                "Realiza la compra, registra movimientos "
                "de almacén y entrega los productos."
            ),
            "es_global": False,
        },
    ]

    # ======================================================
    # PERMISOS
    # ======================================================

    PERMISOS = [

        # ==================================================
        # GENERAL
        # ==================================================

        {
            "codigo": "VER_DASHBOARD_ADMIN",
            "nombre": "Ver dashboard administrativo",
            "descripcion": (
                "Permite visualizar el panel general "
                "de administración de SIA."
            ),
            "modulo": "GENERAL",
        },

        # ==================================================
        # AUTOSERVICIO
        # ==================================================

        {
            "codigo": "VER_PORTAL_SOLICITANTE",
            "nombre": "Ver Portal Solicitante",
            "descripcion": (
                "Permite acceder al portal de "
                "requerimientos del solicitante."
            ),
            "modulo": "AUTOSERVICIO",
        },

        {
            "codigo": "REGISTRAR_REQUERIMIENTO",
            "nombre": "Registrar requerimiento",
            "descripcion": (
                "Permite iniciar un nuevo requerimiento "
                "y seleccionar el proceso correspondiente."
            ),
            "modulo": "AUTOSERVICIO",
        },

        {
            "codigo": "VER_MIS_REQUERIMIENTOS",
            "nombre": "Ver mis requerimientos",
            "descripcion": (
                "Permite consultar los requerimientos "
                "registrados por el usuario."
            ),
            "modulo": "AUTOSERVICIO",
        },

        # ==================================================
        # SOPORTE TÉCNICO
        # ==================================================

        {
            "codigo": "VER_SOPORTE_TECNICO",
            "nombre": "Ver Soporte Técnico",
            "descripcion": (
                "Permite acceder al módulo "
                "de Soporte Técnico."
            ),
            "modulo": "SOPORTE",
        },

        {
            "codigo": "REGISTRAR_TICKET",
            "nombre": "Registrar ticket",
            "descripcion": (
                "Permite registrar un ticket "
                "de Soporte Técnico."
            ),
            "modulo": "SOPORTE",
        },

        {
            "codigo": "CARGAR_EVIDENCIA",
            "nombre": "Cargar evidencia",
            "descripcion": (
                "Permite cargar evidencia asociada "
                "a un ticket de Soporte Técnico."
            ),
            "modulo": "SOPORTE",
        },

        {
            "codigo": "RECIBIR_VALIDAR_TICKET",
            "nombre": "Recibir Ticket y validar Ticket",
            "descripcion": (
                "Permite recibir y validar la información "
                "registrada en un ticket."
            ),
            "modulo": "SOPORTE",
        },

        {
            "codigo": "CLASIFICAR_PRIORIDAD_SLA",
            "nombre": "Clasificar prioridad y asignar SLA",
            "descripcion": (
                "Permite clasificar la prioridad "
                "y asignar SLA al ticket."
            ),
            "modulo": "SOPORTE",
        },

        {
            "codigo": "DESIGNAR_REVISION",
            "nombre": (
                "Designar revisión al equipo "
                "de especialistas"
            ),
            "descripcion": (
                "Permite designar al especialista responsable "
                "y especialistas de apoyo."
            ),
            "modulo": "SOPORTE",
        },

        {
            "codigo": "REALIZAR_INSPECCION_DIAGNOSTICO",
            "nombre": (
                "Realizar inspección técnica "
                "y diagnóstico"
            ),
            "descripcion": (
                "Permite registrar la inspección técnica "
                "y el diagnóstico correspondiente."
            ),
            "modulo": "SOPORTE",
        },

        {
            "codigo": "REALIZAR_REPARACION_INSTALACION",
            "nombre": (
                "Realizar reparación o instalación "
                "del equipo y registrar"
            ),
            "descripcion": (
                "Permite registrar la reparación, "
                "configuración o instalación realizada."
            ),
            "modulo": "SOPORTE",
        },

        {
            "codigo": "REALIZAR_PRUEBAS_TECNICAS",
            "nombre": "Realizar pruebas técnicas",
            "descripcion": (
                "Permite registrar pruebas técnicas "
                "posteriores a la intervención."
            ),
            "modulo": "SOPORTE",
        },

        {
            "codigo": "VERIFICAR_FUNCIONAMIENTO",
            "nombre": "Verificar funcionamiento",
            "descripcion": (
                "Permite al Jefe de UTIC verificar el funcionamiento "
                "del equipo tras la intervención y decidir si el "
                "problema quedó resuelto."
            ),
            "modulo": "SOPORTE",
        },

        {
            "codigo": "INFORMAR_CONFORMIDAD",
            "nombre": "Informar conformidad",
            "descripcion": (
                "Permite al solicitante informar "
                "la conformidad con la solución."
            ),
            "modulo": "SOPORTE",
        },

        {
            "codigo": "ELABORAR_VALIDAR_INFORME_FINAL",
            "nombre": "Elaborar y validar informe final",
            "descripcion": (
                "Permite elaborar y validar "
                "el informe técnico final."
            ),
            "modulo": "SOPORTE",
        },

        {
            "codigo": "RECIBIR_INFORME_ACTIVIDADES",
            "nombre": "Recibir informe de actividades",
            "descripcion": (
                "Permite a la Dirección tomar conocimiento del informe "
                "final de actividades que eleva la jefatura al cerrar "
                "un ticket."
            ),
            "modulo": "SOPORTE",
        },

        {
            "codigo": "SOLICITAR_REQUERIMIENTO_COMPONENTE",
            "nombre": "Solicitar requerimiento de componente",
            "descripcion": (
                "Permite al Especialista pedir la compra de un "
                "componente (con cotización) cuando el ticket "
                "lo requiere, para que Jefe UTIC evalúe si es "
                "viable."
            ),
            "modulo": "SOPORTE",
        },

        {
            "codigo": "AUTORIZAR_SOLICITUD_COMPRA_TI",
            "nombre": "Evaluar viabilidad de compra de TI",
            "descripcion": (
                "Permite al Jefe de UTIC evaluar si el "
                "requerimiento de componente de un ticket es "
                "viable y, de serlo, derivarlo al subproceso "
                "de Compra Caja Chica."
            ),
            "modulo": "SOPORTE",
        },

        # ==================================================
        # MANTENIMIENTO
        # ==================================================

        {
            "codigo": "VER_MANTENIMIENTO",
            "nombre": "Ver Mantenimiento",
            "descripcion": (
                "Permite acceder al módulo "
                "de Mantenimiento."
            ),
            "modulo": "MANTENIMIENTO",
        },

        {
            "codigo": "REGISTRAR_REQUERIMIENTO_MANTENIMIENTO",
            "nombre": "Registrar requerimiento de mantenimiento",
            "descripcion": (
                "Permite registrar un requerimiento "
                "destinado a Servicios Generales."
            ),
            "modulo": "MANTENIMIENTO",
        },

        {
            "codigo": "DERIVAR_A_AUXILIAR",
            "nombre": "Derivar a su auxiliar",
            "descripcion": (
                "Permite derivar el requerimiento "
                "al auxiliar de Servicios Generales."
            ),
            "modulo": "MANTENIMIENTO",
        },

        {
            "codigo": "VERIFICAR_REPOSICION_ALMACEN",
            "nombre": "Verificar reposición de almacén",
            "descripcion": (
                "Permite determinar si el mantenimiento "
                "requiere reposición desde almacén."
            ),
            "modulo": "MANTENIMIENTO",
        },

        {
            "codigo": "REALIZAR_MANTENIMIENTO",
            "nombre": "Realizar mantenimiento",
            "descripcion": (
                "Permite registrar la ejecución "
                "del mantenimiento."
            ),
            "modulo": "MANTENIMIENTO",
        },

        {
            "codigo": "ENTREGAR_PRODUCTO_A_AUXILIAR",
            "nombre": (
                "Entregar producto al auxiliar "
                "de Servicios Generales"
            ),
            "descripcion": (
                "Permite registrar la entrega "
                "del producto desde almacén."
            ),
            "modulo": "MANTENIMIENTO",
        },

        {
            "codigo": "REALIZAR_INFORME_FOTOGRAMA",
            "nombre": "Realizar informe y fotograma",
            "descripcion": (
                "Permite registrar el informe "
                "y fotograma del trabajo realizado."
            ),
            "modulo": "MANTENIMIENTO",
        },

        {
            "codigo": "DERIVAR_COMPRA_CAJA_CHICA",
            "nombre": "Derivar a Compra Caja Chica",
            "descripcion": (
                "Permite derivar el requerimiento "
                "al subproceso de Compra Caja Chica."
            ),
            "modulo": "MANTENIMIENTO",
        },

        {
            "codigo": "RECIBIR_REPORTE_MENSUAL_MANTENIMIENTO",
            "nombre": "Recibir reporte mensual de mantenimiento",
            "descripcion": (
                "Permite al Director tomar conocimiento del "
                "consolidado mensual de mantenimientos finalizados."
            ),
            "modulo": "MANTENIMIENTO",
        },

        # ==================================================
        # COMPRAS
        # ==================================================

        {
            "codigo": "VER_COMPRAS",
            "nombre": "Ver Compras",
            "descripcion": (
                "Permite acceder al módulo de Compras."
            ),
            "modulo": "COMPRAS",
        },

        {
            "codigo": "CARGAR_EXPEDIENTE",
            "nombre": "Cargar expediente",
            "descripcion": (
                "Permite cargar el expediente "
                "para iniciar el proceso de compra."
            ),
            "modulo": "COMPRAS",
        },

        {
            "codigo": "EVALUAR_EXPEDIENTE",
            "nombre": "Evaluar expediente",
            "descripcion": (
                "Permite a DAF evaluar "
                "el expediente recibido."
            ),
            "modulo": "COMPRAS",
        },

        {
            "codigo": "CERTIFICAR_PRESUPUESTO",
            "nombre": "Emitir certificación presupuestaria",
            "descripcion": (
                "Permite registrar la certificación "
                "presupuestaria correspondiente."
            ),
            "modulo": "COMPRAS",
        },

        {
            "codigo": "DAR_VISTO_BUENO",
            "nombre": "Dar visto bueno",
            "descripcion": (
                "Permite al Director registrar "
                "el visto bueno."
            ),
            "modulo": "COMPRAS",
        },

        {
            "codigo": "REGISTRAR_DESEMBOLSO",
            "nombre": "Registrar desembolso",
            "descripcion": (
                "Permite a Tesorería registrar "
                "el desembolso correspondiente."
            ),
            "modulo": "COMPRAS",
        },

        {
            "codigo": "REALIZAR_COMPRA",
            "nombre": "Realizar compra",
            "descripcion": (
                "Permite registrar la compra realizada."
            ),
            "modulo": "COMPRAS",
        },

        {
            "codigo": "REGISTRAR_ENTRADA_SALIDA_ALMACEN",
            "nombre": "Registrar entrada y salida de almacén",
            "descripcion": (
                "Permite registrar los movimientos "
                "del producto en almacén."
            ),
            "modulo": "COMPRAS",
        },

        {
            "codigo": "ENTREGAR_PRODUCTO",
            "nombre": "Entregar producto",
            "descripcion": (
                "Permite registrar la entrega del producto "
                "a la Unidad Solicitante."
            ),
            "modulo": "COMPRAS",
        },

        {
            "codigo": "REGISTRAR_DESCARGO",
            "nombre": "Registrar descargo",
            "descripcion": (
                "Permite registrar factura, "
                "acta de conformidad y fotograma."
            ),
            "modulo": "COMPRAS",
        },

        {
            "codigo": "CERRAR_ARCHIVAR_EXPEDIENTE",
            "nombre": "Cerrar y archivar expediente",
            "descripcion": (
                "Permite a Tesorería verificar el descargo final "
                "y archivar el expediente de forma inmutable."
            ),
            "modulo": "COMPRAS",
        },

        # ==================================================
        # ADMINISTRACIÓN
        # ==================================================

        {
            "codigo": "GESTIONAR_USUARIOS",
            "nombre": "Gestionar usuarios",
            "descripcion": (
                "Permite crear, modificar, activar "
                "e inactivar usuarios."
            ),
            "modulo": "ADMINISTRACION",
        },

        {
            "codigo": "GESTIONAR_ROLES_PERMISOS",
            "nombre": "Gestionar roles y permisos",
            "descripcion": (
                "Permite administrar roles, permisos "
                "y sus relaciones."
            ),
            "modulo": "ADMINISTRACION",
        },

        {
            "codigo": "GESTIONAR_AREAS",
            "nombre": "Gestionar áreas",
            "descripcion": (
                "Permite administrar áreas institucionales."
            ),
            "modulo": "ADMINISTRACION",
        },

        {
            "codigo": "CONSULTAR_TICKETS",
            "nombre": "Consultar tickets",
            "descripcion": (
                "Permite consultar el listado administrativo "
                "de tickets."
            ),
            "modulo": "ADMINISTRACION",
        },

        # ==================================================
        # AUDITORÍA
        # ==================================================

        {
            "codigo": "CONSULTAR_BITACORA",
            "nombre": "Consultar auditoría",
            "descripcion": (
                "Permite consultar el historial "
                "de acciones de SIA."
            ),
            "modulo": "AUDITORIA",
        },

        # ==================================================
        # CONFIGURACIÓN
        # ==================================================

        {
            "codigo": "CONFIGURAR_SMTP",
            "nombre": "Configurar correo SMTP",
            "descripcion": (
                "Permite modificar la configuración "
                "del correo institucional."
            ),
            "modulo": "CONFIGURACION",
        },

        {
            "codigo": "CONFIGURAR_PREFERENCIAS",
            "nombre": "Configurar preferencias",
            "descripcion": (
                "Permite modificar parámetros "
                "generales de SIA."
            ),
            "modulo": "CONFIGURACION",
        },
    ]

    # ======================================================
    # PERMISOS POR ROL
    # ======================================================

    PERMISOS_POR_ROL = {

        # ADMINISTRADOR
        "ADMIN": "__TODOS__",

        # SUPERUSUARIO: administración técnica del sistema,
        # separada de los procesos de negocio que ve ADMIN.
        "SUPERUSER": [
            "GESTIONAR_USUARIOS",
            "GESTIONAR_ROLES_PERMISOS",
            "CONSULTAR_BITACORA",
            "CONFIGURAR_SMTP",
            "CONFIGURAR_PREFERENCIAS",
        ],

        # AUDITOR QUE YA EXISTE
        "AUDITOR": [
            "CONSULTAR_BITACORA",
        ],

        # AGENTE (rol heredado, formalizado: equivalente a
        # ESPECIALISTA para efectos de visibilidad de Soporte;
        # sigue siendo elegible como técnico asignado).
        "AGENTE": [
            "VER_SOPORTE_TECNICO",
        ],

        # SUPERVISOR_AREA (rol heredado, formalizado: acceso de
        # solo visibilidad a Soporte, ya no por bypass de código).
        "SUPERVISOR_AREA": [
            "VER_SOPORTE_TECNICO",
        ],

        # SOLICITANTE
        "SOLICITANTE": [
            "VER_PORTAL_SOLICITANTE",
            "REGISTRAR_REQUERIMIENTO",
            "VER_MIS_REQUERIMIENTOS",
            "REGISTRAR_TICKET",
            "CARGAR_EVIDENCIA",
            "INFORMAR_CONFORMIDAD",
            "REGISTRAR_REQUERIMIENTO_MANTENIMIENTO",
            "CARGAR_EXPEDIENTE",
            "REGISTRAR_DESCARGO",
        ],

        # JEFE UTIC
        "JEFE_UTIC": [
            "VER_SOPORTE_TECNICO",
            "RECIBIR_VALIDAR_TICKET",
            "CLASIFICAR_PRIORIDAD_SLA",
            "DESIGNAR_REVISION",
            "AUTORIZAR_SOLICITUD_COMPRA_TI",
            "VERIFICAR_FUNCIONAMIENTO",
            "ELABORAR_VALIDAR_INFORME_FINAL",
            "CONSULTAR_TICKETS",
        ],

        # ESPECIALISTA
        "ESPECIALISTA": [
            "VER_SOPORTE_TECNICO",
            "REALIZAR_INSPECCION_DIAGNOSTICO",
            "SOLICITAR_REQUERIMIENTO_COMPONENTE",
            "REALIZAR_REPARACION_INSTALACION",
            "REALIZAR_PRUEBAS_TECNICAS",
        ],

        # SERVICIOS GENERALES
        "SERVICIOS_GENERALES": [
            "VER_MANTENIMIENTO",
            "DERIVAR_A_AUXILIAR",
            "RECIBIR_REPORTE_MENSUAL_MANTENIMIENTO",
        ],

        # AUXILIAR DE SERVICIOS GENERALES
        "AUXILIAR_SERVICIOS_GENERALES": [
            "VER_MANTENIMIENTO",
            "VERIFICAR_REPOSICION_ALMACEN",
            "REALIZAR_MANTENIMIENTO",
            "REALIZAR_INFORME_FOTOGRAMA",
            "DERIVAR_COMPRA_CAJA_CHICA",
        ],

        # DAF (Dirección de Asuntos Financieros)
        "DAF": [
            "VER_COMPRAS",
            "EVALUAR_EXPEDIENTE",
            "CERTIFICAR_PRESUPUESTO",
        ],

        # TESORERÍA: en el BPMN de Caja Chica su única tarea es
        # "DESEMBOLZAR DINERO", una vez que el Director autoriza.
        "TESORERIA": [
            "VER_COMPRAS",
            "REGISTRAR_DESEMBOLSO",
        ],

        # DIRECTOR
        "DIRECTOR": [
            "VER_COMPRAS",
            "DAR_VISTO_BUENO",
            "RECIBIR_INFORME_ACTIVIDADES",
            "VER_MANTENIMIENTO",
            "RECIBIR_REPORTE_MENSUAL_MANTENIMIENTO",
            "VER_SOPORTE_TECNICO",
        ],

        # ENCARGADO DE COMPRAS Y ALMACÉN
        "ENCARGADO_COMPRAS_ALMACEN": [
            "VER_COMPRAS",
            "VER_MANTENIMIENTO",
            "REALIZAR_COMPRA",
            "REGISTRAR_ENTRADA_SALIDA_ALMACEN",
            "ENTREGAR_PRODUCTO",
            "ENTREGAR_PRODUCTO_A_AUXILIAR",
        ],
    }

    # ======================================================
    # EJECUTAR
    # ======================================================

    @transaction.atomic
    def handle(self, *args, **options):

        self.stdout.write("")

        self.stdout.write(
            self.style.WARNING(
                "Configurando roles y permisos SIA..."
            )
        )

        # ==================================================
        # 1. CREAR ROLES BASE
        # ==================================================

        roles_creados = 0
        roles_existentes = 0

        for datos in self.ROLES_BASE:

            rol, creado = Rol.objects.get_or_create(
                codigo=datos["codigo"],
                defaults={
                    "nombre": datos["nombre"],
                    "descripcion": datos["descripcion"],
                    "es_global": datos["es_global"],
                    "activo": True,
                }
            )

            if creado:

                roles_creados += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Rol creado: {rol.codigo}"
                    )
                )

            else:

                roles_existentes += 1

                # No destruimos ni reemplazamos
                # configuraciones ya existentes.
                campos_actualizados = []
                if rol.nombre != datos["nombre"]:
                    rol.nombre = datos["nombre"]
                    campos_actualizados.append("nombre")

                if not rol.activo:
                    rol.activo = True
                    campos_actualizados.append("activo")

                if campos_actualizados:
                    rol.save(update_fields=campos_actualizados)

        self.stdout.write("")

        self.stdout.write(
            f"Roles nuevos: {roles_creados}"
        )

        self.stdout.write(
            f"Roles ya existentes: {roles_existentes}"
        )

        # La institución no tiene un Jefe de carrera en este proceso: el
        # informe de actividades lo recibe únicamente la Dirección.
        Rol.objects.filter(codigo="JEFE_CARRERA").update(activo=False)

        RolPermiso.objects.filter(rol__codigo="JEFE_CARRERA").update(activo=False)

        # El proceso no contempla una verificación de Tesorería previa a la
        # autorización del Director: el permiso se desactiva en lugar de
        # borrarse para conservar el historial de la bitácora.
        Permiso.objects.filter(
            codigo="VERIFICAR_EXPEDIENTE_TESORERIA"
        ).update(activo=False)

        RolPermiso.objects.filter(
            permiso__codigo="VERIFICAR_EXPEDIENTE_TESORERIA"
        ).update(activo=False)

        # El proceso de Caja Chica no contempla una jefatura de la DAF:
        # la solicitud llega directamente a la DAF. El rol se conserva
        # inactivo para no perder el historial ya registrado con él.
        rol_jefe_daf = Rol.objects.filter(codigo="JEFE_DAF").first()

        if rol_jefe_daf:

            if rol_jefe_daf.activo:
                rol_jefe_daf.activo = False
                rol_jefe_daf.save(update_fields=["activo"])

            RolPermiso.objects.filter(rol=rol_jefe_daf, activo=True).update(activo=False)

            UsuarioRol.objects.filter(rol=rol_jefe_daf, activo=True).update(activo=False)

            self.stdout.write(
                self.style.WARNING(
                    "Rol JEFE_DAF desactivado: la DAF recibe la solicitud directamente."
                )
            )

        for codigo, nombre in (
            ("DAF", "DAF"),
            ("MANTENIMIENTO", "Mantenimiento"),
            ("UTIC", "UTIC"),
        ):
            Area.objects.update_or_create(
                codigo=codigo,
                defaults={"nombre": nombre, "activo": True},
            )

        # ==================================================
        # 2. CREAR / ACTUALIZAR PERMISOS
        # ==================================================

        permisos_creados = 0
        permisos_actualizados = 0

        for datos in self.PERMISOS:

            permiso, creado = (
                Permiso.objects.update_or_create(
                    codigo=datos["codigo"],
                    defaults={
                        "nombre": datos["nombre"],
                        "descripcion": datos["descripcion"],
                        "modulo": datos["modulo"],
                        "activo": True,
                    }
                )
            )

            if creado:
                permisos_creados += 1
            else:
                permisos_actualizados += 1

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                f"Permisos creados: {permisos_creados}"
            )
        )

        self.stdout.write(
            f"Permisos actualizados: {permisos_actualizados}"
        )

        # ==================================================
        # 3. ASIGNAR PERMISOS A ROLES
        # ==================================================

        asignaciones_creadas = 0
        asignaciones_reactivadas = 0

        for codigo_rol, permisos_rol in (
            self.PERMISOS_POR_ROL.items()
        ):

            try:

                rol = Rol.objects.get(
                    codigo__iexact=codigo_rol
                )

            except Rol.DoesNotExist:

                self.stdout.write(
                    self.style.WARNING(
                        f"Rol no encontrado: {codigo_rol}"
                    )
                )

                continue

            # ==============================================
            # ADMIN = TODOS LOS PERMISOS
            # ==============================================

            if permisos_rol == "__TODOS__":

                permisos = (
                    Permiso.objects
                    .filter(
                        activo=True
                    )
                )

            else:

                permisos = (
                    Permiso.objects
                    .filter(
                        codigo__in=permisos_rol,
                        activo=True
                    )
                )

            RolPermiso.objects.filter(
                rol=rol,
                activo=True,
            ).exclude(
                permiso__in=permisos,
            ).update(activo=False)

            for permiso in permisos:

                asignacion, creado = (
                    RolPermiso.objects.get_or_create(
                        rol=rol,
                        permiso=permiso,
                        defaults={
                            "activo": True
                        }
                    )
                )

                if creado:

                    asignaciones_creadas += 1

                elif not asignacion.activo:

                    asignacion.activo = True

                    asignacion.save(
                        update_fields=[
                            "activo"
                        ]
                    )

                    asignaciones_reactivadas += 1

        # ==================================================
        # RESULTADO
        # ==================================================

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                (
                    "Asignaciones Rol-Permiso creadas: "
                    f"{asignaciones_creadas}"
                )
            )
        )

        self.stdout.write(
            (
                "Asignaciones Rol-Permiso reactivadas: "
                f"{asignaciones_reactivadas}"
            )
        )

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Roles y permisos SIA configurados correctamente."
            )
        )

        self.stdout.write("")
