from datetime import timedelta
import secrets
import string
import unicodedata

from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction

from rest_framework import serializers

from .models import (
    Usuario,
    Rol,
    Area,
    UsuarioRol,
    Permiso,
    RolPermiso,
    InformeJefatura,
    DelegacionAprobacion,
)


def generar_password_temporal(aleatoria=False):
    """Genera la clave temporal sin alterar la clave fija usada en las altas."""
    if not aleatoria:
        return "Temporal2026*"

    grupos = (
        string.ascii_uppercase,
        string.ascii_lowercase,
        string.digits,
        "!@#$%&*",
    )
    caracteres = [secrets.choice(grupo) for grupo in grupos]
    alfabeto = "".join(grupos)
    caracteres.extend(secrets.choice(alfabeto) for _ in range(12))
    secrets.SystemRandom().shuffle(caracteres)
    return "".join(caracteres)


# ==========================================================
# ÁREA
# ==========================================================

class AreaSerializer(serializers.ModelSerializer):

    class Meta:

        model = Area

        fields = [
            "id",
            "codigo",
            "nombre",
            "descripcion",
            "activo",
        ]


    # ======================================================
    # NORMALIZAR CÓDIGO
    # ======================================================

    def validate_codigo(self, value):

        value = (
            value
            .strip()
            .upper()
            .replace(" ", "_")
        )

        queryset = Area.objects.filter(
            codigo__iexact=value
        )


        if self.instance:

            queryset = queryset.exclude(
                pk=self.instance.pk
            )


        if queryset.exists():

            raise serializers.ValidationError(
                "Ya existe un área con este código."
            )


        return value


# ==========================================================
# PERMISO
# ==========================================================

class PermisoSerializer(serializers.ModelSerializer):

    modulo_nombre = serializers.CharField(
        source="get_modulo_display",
        read_only=True
    )


    class Meta:

        model = Permiso

        fields = [
            "id",
            "codigo",
            "nombre",
            "descripcion",
            "modulo",
            "modulo_nombre",
            "activo",
            "creado_en",
            "actualizado_en",
        ]

        read_only_fields = [
            "creado_en",
            "actualizado_en",
        ]


    # ======================================================
    # NORMALIZAR CÓDIGO
    # ======================================================

    def validate_codigo(self, value):

        value = (
            value
            .strip()
            .upper()
            .replace(" ", "_")
        )


        queryset = Permiso.objects.filter(
            codigo__iexact=value
        )


        if self.instance:

            queryset = queryset.exclude(
                pk=self.instance.pk
            )


        if queryset.exists():

            raise serializers.ValidationError(
                "Ya existe un permiso con este código."
            )


        return value


# ==========================================================
# ROL
# ==========================================================

class RolSerializer(serializers.ModelSerializer):

    cantidad_permisos = serializers.SerializerMethodField()

    permisos = serializers.SerializerMethodField()


    class Meta:

        model = Rol

        fields = [
            "id",
            "codigo",
            "nombre",
            "descripcion",
            "es_global",
            "activo",

            # Información adicional
            "cantidad_permisos",
            "permisos",
        ]


    # ======================================================
    # NORMALIZAR CÓDIGO
    # ======================================================

    def validate_codigo(self, value):

        value = (
            value
            .strip()
            .upper()
            .replace(" ", "_")
        )


        queryset = Rol.objects.filter(
            codigo__iexact=value
        )


        if self.instance:

            queryset = queryset.exclude(
                pk=self.instance.pk
            )


        if queryset.exists():

            raise serializers.ValidationError(
                "Ya existe un rol con este código."
            )


        return value


    # ======================================================
    # CANTIDAD DE PERMISOS
    # ======================================================

    def get_cantidad_permisos(self, obj):

        return (
            RolPermiso.objects
            .filter(
                rol=obj,
                activo=True,
                permiso__activo=True
            )
            .count()
        )


    # ======================================================
    # PERMISOS DEL ROL
    # ======================================================

    def get_permisos(self, obj):

        asignaciones = (
            RolPermiso.objects
            .filter(
                rol=obj,
                activo=True,
                permiso__activo=True
            )
            .select_related(
                "permiso"
            )
            .order_by(
                "permiso__modulo",
                "permiso__nombre"
            )
        )


        return [
            {
                "id":
                    asignacion.permiso.id,

                "codigo":
                    asignacion.permiso.codigo,

                "nombre":
                    asignacion.permiso.nombre,

                "descripcion":
                    asignacion.permiso.descripcion,

                "modulo":
                    asignacion.permiso.modulo,

                "modulo_nombre":
                    asignacion.permiso.get_modulo_display(),
            }

            for asignacion in asignaciones
        ]


# ==========================================================
# ROL - PERMISO
# ==========================================================

class RolPermisoSerializer(serializers.ModelSerializer):

    rol_codigo = serializers.CharField(
        source="rol.codigo",
        read_only=True
    )

    rol_nombre = serializers.CharField(
        source="rol.nombre",
        read_only=True
    )

    permiso_codigo = serializers.CharField(
        source="permiso.codigo",
        read_only=True
    )

    permiso_nombre = serializers.CharField(
        source="permiso.nombre",
        read_only=True
    )

    permiso_modulo = serializers.CharField(
        source="permiso.modulo",
        read_only=True
    )

    permiso_modulo_nombre = serializers.CharField(
        source="permiso.get_modulo_display",
        read_only=True
    )


    class Meta:

        model = RolPermiso

        fields = [
            "id",

            "rol",
            "rol_codigo",
            "rol_nombre",

            "permiso",
            "permiso_codigo",
            "permiso_nombre",
            "permiso_modulo",
            "permiso_modulo_nombre",

            "activo",
            "fecha_asignacion",
        ]

        read_only_fields = [
            "fecha_asignacion",
        ]


    # ======================================================
    # VALIDAR ROL
    # ======================================================

    def validate_rol(self, value):

        if not value.activo:

            raise serializers.ValidationError(
                "No puede asignar permisos a un rol inactivo."
            )


        return value


    # ======================================================
    # VALIDAR PERMISO
    # ======================================================

    def validate_permiso(self, value):

        if not value.activo:

            raise serializers.ValidationError(
                "No puede asignar un permiso inactivo."
            )


        return value


    # ======================================================
    # VALIDAR DUPLICADO
    # ======================================================

    def validate(self, attrs):

        rol = attrs.get(
            "rol"
        )

        permiso = attrs.get(
            "permiso"
        )


        queryset = RolPermiso.objects.filter(
            rol=rol,
            permiso=permiso
        )


        if self.instance:

            queryset = queryset.exclude(
                pk=self.instance.pk
            )


        if queryset.exists():

            raise serializers.ValidationError(
                {
                    "permiso":
                        (
                            "Este permiso ya está "
                            "asignado al rol."
                        )
                }
            )


        return attrs


# ==========================================================
# USUARIO - ROL
# ==========================================================

class UsuarioRolSerializer(serializers.ModelSerializer):

    rol_nombre = serializers.CharField(
        source="rol.nombre",
        read_only=True
    )

    rol_codigo = serializers.CharField(
        source="rol.codigo",
        read_only=True
    )

    area_nombre = serializers.CharField(
        source="area.nombre",
        read_only=True
    )

    area_codigo = serializers.CharField(
        source="area.codigo",
        read_only=True
    )

    permisos = serializers.SerializerMethodField()


    class Meta:

        model = UsuarioRol

        fields = [
            "id",

            "usuario",

            "rol",
            "rol_nombre",
            "rol_codigo",

            "area",
            "area_nombre",
            "area_codigo",

            "permisos",

            "activo",
            "fecha_asignacion",
        ]


    # ======================================================
    # PERMISOS DEL ROL ASIGNADO
    # ======================================================

    def get_permisos(self, obj):

        asignaciones = (
            RolPermiso.objects
            .filter(
                rol=obj.rol,
                activo=True,
                permiso__activo=True
            )
            .select_related(
                "permiso"
            )
            .order_by(
                "permiso__modulo",
                "permiso__nombre"
            )
        )


        return [
            {
                "id":
                    asignacion.permiso.id,

                "codigo":
                    asignacion.permiso.codigo,

                "nombre":
                    asignacion.permiso.nombre,

                "modulo":
                    asignacion.permiso.modulo,
            }

            for asignacion in asignaciones
        ]


# ==========================================================
# USUARIO
# ==========================================================

class UsuarioSerializer(serializers.ModelSerializer):

    primer_nombre = serializers.CharField(
        write_only=True, required=False, max_length=80
    )
    segundo_nombre = serializers.CharField(
        write_only=True, required=False, allow_blank=True, max_length=80
    )
    apellido_paterno = serializers.CharField(
        write_only=True, required=False, max_length=80
    )
    apellido_materno = serializers.CharField(
        write_only=True, required=False, max_length=80
    )

    # ======================================================
    # CONTRASEÑA
    # ======================================================

    # Nunca devolvemos la contraseña al frontend.

    password = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=False
    )


    # ======================================================
    # ROL SELECCIONADO POR ADMIN
    # ======================================================

    rol_id = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True
    )


    # ======================================================
    # ÁREA SELECCIONADA POR ADMIN
    # ======================================================

    area_id = serializers.IntegerField(
        write_only=True,
        required=False,
        allow_null=True
    )

    especialidad = serializers.CharField(
        write_only=True,
        required=False,
        allow_blank=True,
        max_length=80,
    )


    # ======================================================
    # INFORMACIÓN PARA FRONTEND
    # ======================================================

    roles = serializers.SerializerMethodField()

    permisos = serializers.SerializerMethodField()


    class Meta:

        model = Usuario

        fields = [
            "id",
            "username",
            "email",
            "nombre_completo",
            "password",
            "primer_nombre",
            "segundo_nombre",
            "apellido_paterno",
            "apellido_materno",

            "is_active",
            "must_change_password",

            "failed_attempts",
            "locked_until",

            "last_login",
            "last_login_ip",

            "created_at",
            "updated_at",

            # Datos usados por ADMIN
            "rol_id",
            "area_id",
            "especialidad",

            # Información devuelta
            "roles",
            "permisos",
        ]


        # ==================================================
        # CAMPOS CONTROLADOS POR SIGTA
        # ==================================================

        read_only_fields = [
            "username",

            "failed_attempts",
            "locked_until",

            "last_login",
            "last_login_ip",

            "created_at",
            "updated_at",

            "permisos",
        ]


    # ======================================================
    # MOSTRAR ROLES DEL USUARIO
    # ======================================================

    def get_roles(self, obj):

        asignaciones = (
            UsuarioRol.objects
            .filter(
                usuario=obj,
                activo=True,
                rol__activo=True
            )
            .select_related(
                "rol",
                "area"
            )
            .order_by(
                "rol__nombre"
            )
        )


        return [
            {
                "id":
                    asignacion.id,

                "rol_id":
                    asignacion.rol.id,

                "rol_codigo":
                    asignacion.rol.codigo,

                "rol_nombre":
                    asignacion.rol.nombre,

                "es_global":
                    asignacion.rol.es_global,

                "area_id": (
                    asignacion.area.id
                    if asignacion.area
                    else None
                ),

                "area_codigo": (
                    asignacion.area.codigo
                    if asignacion.area
                    else None
                ),

                "area_nombre": (
                    asignacion.area.nombre
                    if asignacion.area
                    else None
                ),

                "especialidad": asignacion.especialidad,
            }

            for asignacion in asignaciones
        ]


    # ======================================================
    # MOSTRAR PERMISOS EFECTIVOS DEL USUARIO
    # ======================================================

    def get_permisos(self, obj):

        """
        Los permisos del usuario se obtienen
        a través de sus roles activos:

        Usuario
          -> UsuarioRol
          -> Rol
          -> RolPermiso
          -> Permiso

        Si el usuario tiene más de un rol,
        se eliminan permisos duplicados.
        """

        codigos_roles = (
            UsuarioRol.objects
            .filter(
                usuario=obj,
                activo=True,
                rol__activo=True
            )
            .values_list(
                "rol_id",
                flat=True
            )
        )


        permisos = (
            Permiso.objects
            .filter(
                activo=True,
                roles_asignados__rol_id__in=codigos_roles,
                roles_asignados__activo=True
            )
            .distinct()
            .order_by(
                "modulo",
                "nombre"
            )
        )


        return [
            {
                "id":
                    permiso.id,

                "codigo":
                    permiso.codigo,

                "nombre":
                    permiso.nombre,

                "descripcion":
                    permiso.descripcion,

                "modulo":
                    permiso.modulo,

                "modulo_nombre":
                    permiso.get_modulo_display(),
            }

            for permiso in permisos
        ]


    # ======================================================
    # VALIDAR CORREO
    # ======================================================

    @staticmethod
    def normalizar_correo(texto):
        texto = unicodedata.normalize("NFKD", texto.strip().lower())
        return "".join(
            caracter for caracter in texto
            if caracter.isascii() and caracter.isalnum()
        )

    def construir_correo(self, primer_nombre, apellido_paterno, apellido_materno):
        primero = self.normalizar_correo(primer_nombre)
        paterno = self.normalizar_correo(apellido_paterno)
        materno = self.normalizar_correo(apellido_materno)

        if not primero or not paterno or not materno:
            raise serializers.ValidationError({
                "nombre_completo": "Ingrese el primer nombre y ambos apellidos."
            })

        return f"{primero[0]}{paterno}{materno[0]}@emi.edu.bo"

    def validate_email(self, value):

        value = (
            value
            .strip()
            .lower()
        )


        # --------------------------------------------------
        # CORREO INSTITUCIONAL
        # --------------------------------------------------

        if not value.endswith(
            "@emi.edu.bo"
        ):

            raise serializers.ValidationError(
                (
                    "Debe utilizar un correo "
                    "institucional @emi.edu.bo."
                )
            )


        queryset = Usuario.objects.filter(
            email__iexact=value
        )


        # Si estamos editando,
        # excluir al mismo usuario.

        if self.instance:

            queryset = queryset.exclude(
                pk=self.instance.pk
            )


        if queryset.exists():

            raise serializers.ValidationError(
                (
                    "El correo institucional "
                    "ya está registrado."
                )
            )


        return value


    # ======================================================
    # VALIDAR CONTRASEÑA TEMPORAL
    # ======================================================
    #
    # El correo del solicitante (ADMIN) le fija esta contraseña
    # a un tercero, así que debe cumplir la misma política de
    # complejidad (AUTH_PASSWORD_VALIDATORS) que cualquier otra
    # contraseña del sistema — de lo contrario un ADMIN podría
    # crear cuentas con contraseñas triviales.
    # ======================================================

    def validate_password(self, value):

        try:
            password_validation.validate_password(value, user=self.instance)
        except DjangoValidationError as error:
            raise serializers.ValidationError(list(error.messages))

        return value


    # ======================================================
    # VALIDAR NOMBRE
    # ======================================================

    def validate_nombre_completo(
        self,
        value
    ):

        value = value.strip()


        if len(value) < 3:

            raise serializers.ValidationError(
                "Ingrese un nombre completo válido."
            )


        return value


    # ======================================================
    # OBTENER ROL
    # ======================================================

    def obtener_rol(
        self,
        rol_id
    ):

        try:

            return Rol.objects.get(
                pk=rol_id,
                activo=True
            )


        except Rol.DoesNotExist:

            raise serializers.ValidationError(
                {
                    "rol_id":
                        (
                            "El rol seleccionado "
                            "no existe o está inactivo."
                        )
                }
            )


    # ======================================================
    # OBTENER ÁREA SEGÚN ROL
    # ======================================================

    def obtener_area(
        self,
        rol,
        area_id
    ):

        # --------------------------------------------------
        # ROL GLOBAL
        # --------------------------------------------------

        if rol.codigo in {"ADMIN", "SUPERUSER", "DIRECTOR", "SOLICITANTE"}:

            return None


        # --------------------------------------------------
        # ROL POR ÁREA
        # --------------------------------------------------

        if not area_id:

            raise serializers.ValidationError(
                {
                    "area_id":
                        (
                            "Debe seleccionar un área "
                            "para este rol."
                        )
                }
            )

        try:
            return Area.objects.get(pk=area_id, activo=True)
        except Area.DoesNotExist:
            raise serializers.ValidationError({
                "area_id": "El área seleccionada no existe o está inactiva."
            })


    def validar_especialidad(self, rol, area, especialidad):
        roles_tecnicos = {
            "ESPECIALISTA",
            "AUXILIAR_SERVICIOS_GENERALES",
            "DAF",
            "ENCARGADO_COMPRAS_ALMACEN",
            "TESORERIA",
        }
        if rol.codigo not in roles_tecnicos:
            return ""

        permitidas = {
            "UTIC": {"REDES", "HARDWARE_COMPUTADORAS", "SISTEMAS_CENTRALIZADOS_DATOS", "EQUIPOS_AUXILIARES"},
            "MANTENIMIENTO": {"CHOFER", "TECNICO_MANTENIMIENTO"},
            "DAF": {"TECNICO_DAF", "ALMACEN_COMPRAS", "TESORERIA"},
        }.get(area.codigo if area else "", set())

        if especialidad not in permitidas:
            raise serializers.ValidationError({
                "especialidad": "Seleccione una especialidad válida para el área indicada."
            })
        return especialidad


    # ======================================================
    # CREAR USUARIO
    # ======================================================

    @transaction.atomic
    def create(
        self,
        validated_data
    ):

        password = validated_data.pop("password", None)
        primer_nombre = validated_data.pop("primer_nombre", "").strip()
        segundo_nombre = validated_data.pop("segundo_nombre", "").strip()
        apellido_paterno = validated_data.pop("apellido_paterno", "").strip()
        apellido_materno = validated_data.pop("apellido_materno", "").strip()


        rol_id = validated_data.pop(
            "rol_id",
            None
        )


        area_id = validated_data.pop(
            "area_id",
            None
        )

        especialidad = validated_data.pop("especialidad", "").strip()


        # --------------------------------------------------
        # CONTRASEÑA TEMPORAL
        # --------------------------------------------------

        if not password:

            raise serializers.ValidationError(
                {
                    "password":
                        (
                            "La contraseña temporal "
                            "es obligatoria."
                        )
                }
            )


        # --------------------------------------------------
        # ROL OBLIGATORIO
        # --------------------------------------------------

        if not primer_nombre or not apellido_paterno or not apellido_materno:
            raise serializers.ValidationError({
                "nombre_completo": "El primer nombre y ambos apellidos son obligatorios."
            })

        if password != generar_password_temporal():
            raise serializers.ValidationError({
                "password": "La contraseña temporal generada no es válida."
            })

        if not rol_id:

            raise serializers.ValidationError(
                {
                    "rol_id":
                        "Debe seleccionar un rol."
                }
            )


        # --------------------------------------------------
        # RESOLVER ROL Y ÁREA
        # ANTES DE CREAR EL USUARIO
        #
        # Esto evita crear parcialmente un usuario
        # si el rol o área son inválidos.
        # --------------------------------------------------

        rol = self.obtener_rol(
            rol_id
        )


        area = self.obtener_area(
            rol,
            area_id
        )

        especialidad = self.validar_especialidad(rol, area, especialidad)


        # --------------------------------------------------
        # PREPARAR CORREO
        # --------------------------------------------------

        email = self.construir_correo(
            primer_nombre, apellido_paterno, apellido_materno
        )

        if Usuario.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError({
                "email": "El correo institucional generado ya está registrado."
            })


        validated_data[
            "email"
        ] = email


        # --------------------------------------------------
        # GENERAR USERNAME AUTOMÁTICAMENTE
        # --------------------------------------------------

        username_base = (
            email.split("@")[0]
        )


        username = (
            username_base
        )


        contador = 1


        while Usuario.objects.filter(
            username=username
        ).exists():

            username = (
                f"{username_base}{contador}"
            )

            contador += 1


        # --------------------------------------------------
        # CREAR USUARIO
        # --------------------------------------------------

        usuario = Usuario(
            username=username,
            **validated_data
        )


        usuario.set_password(
            password
        )


        # HU-02:
        # cambio obligatorio en primer ingreso.

        usuario.must_change_password = True


        usuario.is_active = True


        usuario.save()
        usuario._password_temporal = password


        # --------------------------------------------------
        # ASIGNAR ROL Y ÁREA
        # --------------------------------------------------

        UsuarioRol.objects.create(
            usuario=usuario,
            rol=rol,
            area=area,
            especialidad=especialidad,
            activo=True
        )


        return usuario

    def to_representation(self, instance):
        datos = super().to_representation(instance)
        password_temporal = getattr(instance, "_password_temporal", None)
        if password_temporal:
            datos["password_temporal"] = password_temporal
        return datos


    # ======================================================
    # MODIFICAR USUARIO
    # ======================================================

    @transaction.atomic
    def update(
        self,
        instance,
        validated_data
    ):

        password = validated_data.pop(
            "password",
            None
        )

        validated_data.pop("primer_nombre", None)
        validated_data.pop("segundo_nombre", None)
        validated_data.pop("apellido_paterno", None)
        validated_data.pop("apellido_materno", None)


        rol_id = validated_data.pop(
            "rol_id",
            None
        )


        area_id = validated_data.pop(
            "area_id",
            None
        )

        especialidad = validated_data.pop("especialidad", "").strip()


        # --------------------------------------------------
        # SI SE ESTÁ CAMBIANDO EL ROL,
        # VALIDAMOS ANTES DE MODIFICAR.
        # --------------------------------------------------

        rol = None

        area = None


        if rol_id:

            rol = self.obtener_rol(
                rol_id
            )


            area = self.obtener_area(
                rol,
                area_id
            )

            especialidad = self.validar_especialidad(rol, area, especialidad)


        # --------------------------------------------------
        # MODIFICAR DATOS BÁSICOS
        # --------------------------------------------------

        for atributo, valor in (
            validated_data.items()
        ):

            setattr(
                instance,
                atributo,
                valor
            )


        # --------------------------------------------------
        # NUEVA CONTRASEÑA TEMPORAL
        # --------------------------------------------------

        if password:

            instance.set_password(
                password
            )


            instance.must_change_password = True


        instance.save()


        # --------------------------------------------------
        # MODIFICAR ROL PRINCIPAL
        # --------------------------------------------------

        if rol:

            # Desactivar las asignaciones actuales.

            UsuarioRol.objects.filter(
                usuario=instance,
                activo=True
            ).update(
                activo=False
            )


            # ------------------------------------------------
            # REUTILIZAR UNA ASIGNACIÓN ANTIGUA SI EXISTE
            #
            # Esto evita violar la restricción única
            # usuario + rol + área cuando el usuario vuelve
            # a un rol que ya había tenido anteriormente.
            # ------------------------------------------------

            asignacion_existente = (
                UsuarioRol.objects
                .filter(
                    usuario=instance,
                    rol=rol,
                    area=area
                )
                .first()
            )


            if asignacion_existente:

                asignacion_existente.activo = True
                asignacion_existente.especialidad = especialidad

                asignacion_existente.save(
                    update_fields=[
                        "activo",
                        "especialidad",
                    ]
                )


            else:

                UsuarioRol.objects.create(
                    usuario=instance,
                    rol=rol,
                    area=area,
                    especialidad=especialidad,
                    activo=True
                )

        return instance


# ==========================================================
# DELEGACIÓN TEMPORAL DE APROBACIÓN
# ==========================================================

class InformeJefaturaSerializer(serializers.ModelSerializer):
    jefe_nombre = serializers.CharField(source="jefe.nombre_completo", read_only=True)

    class Meta:
        model = InformeJefatura
        fields = ["id", "jefe", "jefe_nombre", "jefatura", "tipo", "titulo", "periodo", "contenido", "enviado_director", "creado_en", "actualizado_en"]
        read_only_fields = ["jefe", "creado_en", "actualizado_en"]


class DelegacionAprobacionSerializer(serializers.ModelSerializer):

    delegante_nombre = serializers.CharField(
        source="delegante.nombre_completo",
        read_only=True
    )

    delegado_nombre = serializers.CharField(
        source="delegado.nombre_completo",
        read_only=True
    )

    rol_codigo = serializers.CharField(
        source="rol.codigo",
        read_only=True
    )

    rol_nombre = serializers.CharField(
        source="rol.nombre",
        read_only=True
    )

    vigente = serializers.SerializerMethodField()


    class Meta:

        model = DelegacionAprobacion

        fields = [
            "id",
            "delegante",
            "delegante_nombre",
            "delegado",
            "delegado_nombre",
            "rol",
            "rol_codigo",
            "rol_nombre",
            "vigencia_desde",
            "vigencia_hasta",
            "motivo",
            "activo",
            "vigente",
            "creado_en",
        ]

        read_only_fields = [
            "delegante",
            "activo",
            "creado_en",
        ]

    def get_vigente(self, obj):
        return obj.esta_vigente()

    def validate(self, attrs):

        rol = attrs.get("rol") or getattr(self.instance, "rol", None)

        if rol and rol.codigo not in DelegacionAprobacion.ROLES_DELEGABLES:
            raise serializers.ValidationError({
                "rol": (
                    "Solo se puede delegar temporalmente un rol de "
                    "aprobación (Director, DAF, Tesorería o Jefe de UTIC)."
                )
            })

        desde = attrs.get("vigencia_desde")
        hasta = attrs.get("vigencia_hasta")

        if desde and hasta and desde >= hasta:
            raise serializers.ValidationError({
                "vigencia_hasta": "Debe ser posterior a la fecha de inicio."
            })

        # "Temporal" tiene un límite: sin tope, una delegación
        # podría usarse como una puerta trasera permanente
        # disfrazada de ausencia corta.
        if desde and hasta and (hasta - desde) > timedelta(days=90):
            raise serializers.ValidationError({
                "vigencia_hasta": (
                    "Una delegación temporal no puede superar los 90 días. "
                    "Si necesita más tiempo, cree una nueva delegación al vencer."
                )
            })

        delegado = attrs.get("delegado")
        request = self.context.get("request")

        if request and delegado and delegado.id == request.user.id:
            raise serializers.ValidationError({
                "delegado": "No puede delegarse su propio rol a sí mismo."
            })

        return attrs


        return instance
