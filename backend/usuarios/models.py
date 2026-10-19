from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


# ==========================================================
# USUARIO
# ==========================================================

class Usuario(AbstractUser):

    email = models.EmailField(
        unique=True,
        verbose_name="Correo institucional"
    )

    nombre_completo = models.CharField(
        max_length=150,
        verbose_name="Nombre completo"
    )

    must_change_password = models.BooleanField(
        default=True,
        verbose_name="Debe cambiar contraseña"
    )

    failed_attempts = models.PositiveSmallIntegerField(
        default=0,
        verbose_name="Intentos fallidos"
    )

    locked_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Bloqueado hasta"
    )

    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="Última IP"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    USERNAME_FIELD = "email"

    REQUIRED_FIELDS = [
        "username",
        "nombre_completo"
    ]

    def __str__(self):

        return (
            f"{self.nombre_completo} - "
            f"{self.email}"
        )


# ==========================================================
# ÁREA
# ==========================================================

class DocumentoProceso(models.Model):
    """Instantánea de un documento emitido; no admite edición por API."""
    compra = models.ForeignKey('compras.SolicitudCompra', on_delete=models.PROTECT, null=True, blank=True, related_name='documentos_sia')
    mantenimiento = models.ForeignKey('mantenimiento.RequerimientoMantenimiento', on_delete=models.PROTECT, null=True, blank=True, related_name='documentos_sia')
    soporte = models.ForeignKey('soporte.Ticket', on_delete=models.PROTECT, null=True, blank=True, related_name='documentos_sia')
    tipo = models.CharField(max_length=80)
    codigo_expediente = models.CharField(max_length=30)
    contenido = models.JSONField(default=dict)
    firma = models.JSONField(default=list)
    usuario = models.ForeignKey('usuarios.Usuario', on_delete=models.PROTECT)
    nombre_firmante = models.CharField(max_length=200)
    roles_firmante = models.JSONField(default=list)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.CheckConstraint(
            condition=(models.Q(compra__isnull=False, mantenimiento__isnull=True, soporte__isnull=True)
                       | models.Q(compra__isnull=True, mantenimiento__isnull=False, soporte__isnull=True)
                       | models.Q(compra__isnull=True, mantenimiento__isnull=True, soporte__isnull=False)),
            name='documento_un_expediente')]


class Area(models.Model):

    codigo = models.CharField(
        max_length=30,
        unique=True
    )

    nombre = models.CharField(
        max_length=100
    )

    descripcion = models.TextField(
        blank=True
    )

    activo = models.BooleanField(
        default=True
    )

    def __str__(self):

        return self.nombre


# ==========================================================
# ROL
# ==========================================================

class Rol(models.Model):

    codigo = models.CharField(
        max_length=50,
        unique=True
    )

    nombre = models.CharField(
        max_length=100
    )

    descripcion = models.TextField(
        blank=True
    )

    es_global = models.BooleanField(
        default=False
    )

    activo = models.BooleanField(
        default=True
    )

    def __str__(self):

        return self.nombre


# ==========================================================
# PERMISO SIGTA
# ==========================================================
#
# Estos permisos determinan:
#
# - qué módulos puede visualizar un rol;
# - qué acciones puede ejecutar;
# - qué opciones aparecen en la interfaz;
# - qué acciones debe aceptar el backend.
#
# Ejemplos:
#
# VER_SOPORTE_TECNICO
# RECIBIR_VALIDAR_TICKET
# CLASIFICAR_PRIORIDAD_SLA
# EVALUAR_EXPEDIENTE
# REGISTRAR_DESEMBOLSO
#
# ==========================================================

class Permiso(models.Model):

    MODULOS = [

        (
            "GENERAL",
            "General"
        ),

        (
            "SOPORTE",
            "Soporte Técnico"
        ),

        (
            "MANTENIMIENTO",
            "Mantenimiento"
        ),

        (
            "COMPRAS",
            "Compras"
        ),

        (
            "ADMINISTRACION",
            "Administración"
        ),

        (
            "AUDITORIA",
            "Auditoría"
        ),

        (
            "CONFIGURACION",
            "Configuración"
        ),

        (
            "AUTOSERVICIO",
            "Portal Solicitante"
        ),
    ]


    codigo = models.CharField(
        max_length=100,
        unique=True
    )

    nombre = models.CharField(
        max_length=150
    )

    descripcion = models.TextField(
        blank=True
    )

    modulo = models.CharField(
        max_length=30,
        choices=MODULOS,
        default="GENERAL"
    )

    activo = models.BooleanField(
        default=True
    )

    creado_en = models.DateTimeField(
        auto_now_add=True
    )

    actualizado_en = models.DateTimeField(
        auto_now=True
    )

    class Meta:

        ordering = [
            "modulo",
            "nombre"
        ]

        verbose_name = "Permiso"

        verbose_name_plural = "Permisos"

    def __str__(self):

        return (
            f"{self.codigo} - "
            f"{self.nombre}"
        )


# ==========================================================
# RELACIÓN ROL - PERMISO
# ==========================================================
#
# Un rol puede tener muchos permisos.
#
# Ejemplo:
#
# JEFE_UTIC
#
#   VER_SOPORTE_TECNICO
#   RECIBIR_VALIDAR_TICKET
#   CLASIFICAR_PRIORIDAD_SLA
#   DESIGNAR_REVISION
#
# ==========================================================

class RolPermiso(models.Model):

    rol = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE,
        related_name="permisos_asignados"
    )

    permiso = models.ForeignKey(
        Permiso,
        on_delete=models.PROTECT,
        related_name="roles_asignados"
    )

    activo = models.BooleanField(
        default=True
    )

    fecha_asignacion = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "rol",
                    "permiso"
                ],
                name="unique_rol_permiso"
            )
        ]

        verbose_name = "Permiso del rol"

        verbose_name_plural = "Permisos de los roles"

    def __str__(self):

        return (
            f"{self.rol.codigo} - "
            f"{self.permiso.codigo}"
        )


# ==========================================================
# RELACIÓN USUARIO - ROL - ÁREA
# ==========================================================

class UsuarioRol(models.Model):

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="roles_asignados"
    )

    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        related_name="usuarios_asignados"
    )

    area = models.ForeignKey(
        Area,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="usuarios_roles"
    )

    especialidad = models.CharField(
        max_length=80,
        blank=True,
        default=""
    )

    activo = models.BooleanField(
        default=True
    )

    fecha_asignacion = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:

        constraints = [

            models.UniqueConstraint(
                fields=[
                    "usuario",
                    "rol",
                    "area"
                ],
                name="unique_usuario_rol_area"
            )
        ]

        verbose_name = "Rol del usuario"

        verbose_name_plural = "Roles de los usuarios"

    def __str__(self):

        area = (
            self.area.nombre
            if self.area
            else "GLOBAL"
        )

        return (
            f"{self.usuario.email} - "
            f"{self.rol.codigo} - "
            f"{area}"
        )


# ==========================================================
# INFORMES DE JEFATURA AL DIRECTOR
# ==========================================================

class InformeJefatura(models.Model):
    JEFATURAS = [("UTIC", "UTIC"), ("MANTENIMIENTO", "Mantenimiento")]
    TIPOS = [("ACTIVIDADES", "Informe de actividades")]

    jefe = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="informes_jefatura")
    jefatura = models.CharField(max_length=20, choices=JEFATURAS)
    tipo = models.CharField(max_length=20, choices=TIPOS, default="ACTIVIDADES")
    titulo = models.CharField(max_length=200)
    periodo = models.CharField(max_length=30)
    contenido = models.TextField()
    enviado_director = models.BooleanField(default=False)
    creado_en = models.DateTimeField(auto_now_add=True)
    actualizado_en = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado_en"]


# ==========================================================
# DELEGACIÓN TEMPORAL DE APROBACIÓN
# ==========================================================
#
# Caso de uso "Delegar aprobación temporal" (Módulo 1
# Identidad): permite a un actor que aprueba/autoriza algo
# en el sistema (DIRECTOR, DAF, TESORERIA, JEFE_UTIC) ceder
# temporalmente su rol a otro usuario mientras está ausente,
# sin necesidad de que ADMIN intervenga.
#
# ==========================================================

class DelegacionAprobacion(models.Model):

    ROLES_DELEGABLES = [
        "DIRECTOR",
        "DAF",
        "TESORERIA",
        "JEFE_UTIC",
    ]

    delegante = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="delegaciones_otorgadas"
    )

    delegado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="delegaciones_recibidas"
    )

    rol = models.ForeignKey(
        Rol,
        on_delete=models.PROTECT,
        related_name="delegaciones"
    )

    vigencia_desde = models.DateTimeField()

    vigencia_hasta = models.DateTimeField()

    motivo = models.CharField(
        max_length=255,
        blank=True
    )

    activo = models.BooleanField(
        default=True
    )

    creado_en = models.DateTimeField(
        auto_now_add=True
    )

    def esta_vigente(self):

        ahora = timezone.now()

        return (
            self.activo
            and self.vigencia_desde <= ahora <= self.vigencia_hasta
        )

    def __str__(self):

        return (
            f"{self.delegante.email} -> "
            f"{self.delegado.email} ({self.rol.codigo})"
        )


# ==========================================================
# ROLES EFECTIVOS (DIRECTOS + DELEGADOS)
# ==========================================================
#
# Punto único usado por todas las apps (usuarios, compras,
# mantenimiento, soporte) para calcular qué roles puede
# ejercer un usuario en este momento: los suyos propios más
# los que le hayan delegado temporalmente y sigan vigentes.
#
# ==========================================================

def obtener_codigos_rol_efectivos(usuario):

    if not usuario or not usuario.is_authenticated:
        return []

    directos = set(
        UsuarioRol.objects
        .filter(usuario=usuario, activo=True, rol__activo=True)
        .values_list("rol__codigo", flat=True)
    )

    ahora = timezone.now()

    delegados = set(
        DelegacionAprobacion.objects
        .filter(
            delegado=usuario,
            activo=True,
            vigencia_desde__lte=ahora,
            vigencia_hasta__gte=ahora,
            rol__activo=True,
        )
        .values_list("rol__codigo", flat=True)
    )

    return list(directos | delegados)
