from django.core.management.base import BaseCommand
from django.db import transaction

from usuarios.models import Rol, Usuario, UsuarioRol


# Contraseña única para TODAS las cuentas de prueba: en
# desarrollo tener una distinta por rol solo obligaba a ir a
# buscarla al archivo de credenciales en cada cambio de usuario.
# Cumple AUTH_PASSWORD_VALIDATORS (mayúscula, minúscula, número,
# carácter especial y 8 caracteres), así que las cuentas con
# must_change_password también pueden fijarla de nuevo.
# Solo para entorno local; nunca para una instalación real.

CLAVE_PRUEBA = "Hola123*"


class Command(BaseCommand):

    help = (
        "Crea/actualiza las cuentas de prueba de SIA para "
        "los roles que todavía no tenían credenciales en "
        "CREDENCIALES_PRUEBA.md, y una cuenta nueva pendiente "
        "de cambio de contraseña para probar HU-01/HU-02."
    )

    USUARIOS = [
        {
            "email": "superuser@emi.edu.bo",
            "nombre_completo": "Admin",
            "rol": "SUPERUSER",
            "password": CLAVE_PRUEBA,
            "must_change_password": False,
        },
        {
            "email": "admin@emi.edu.bo",
            "nombre_completo": "Director",
            "rol": "ADMIN",
            "password": CLAVE_PRUEBA,
            "must_change_password": False,
        },
        {
            "email": "jefe.utic@emi.edu.bo",
            "nombre_completo": "Jefe UTIC",
            "rol": "JEFE_UTIC",
            "password": CLAVE_PRUEBA,
            "must_change_password": False,
        },
        {
            "email": "servicios.generales@emi.edu.bo",
            "nombre_completo": "Jefe Mantenimiento",
            "rol": "SERVICIOS_GENERALES",
            "password": CLAVE_PRUEBA,
            "must_change_password": False,
        },
        {
            "email": "daf@emi.edu.bo",
            "nombre_completo": "Técnico de la DAF",
            "rol": "DAF",
            "password": CLAVE_PRUEBA,
            "must_change_password": False,
        },
        {
            "email": "almacen@emi.edu.bo",
            "nombre_completo": "Técnico de Almacén y Compras",
            "rol": "ENCARGADO_COMPRAS_ALMACEN",
            "password": CLAVE_PRUEBA,
            "must_change_password": False,
        },
        {
            "email": "tesoreria@emi.edu.bo",
            "nombre_completo": "Técnico de Tesorería",
            "rol": "TESORERIA",
            "password": CLAVE_PRUEBA,
            "must_change_password": False,
        },
        {
            "email": "especialista@emi.edu.bo",
            "nombre_completo": "Técnico de Soporte Técnico",
            "rol": "ESPECIALISTA",
            "password": CLAVE_PRUEBA,
            "must_change_password": False,
        },
        {
            "email": "auxiliar.sg@emi.edu.bo",
            "nombre_completo": "Técnico de Mantenimiento",
            "rol": "AUXILIAR_SERVICIOS_GENERALES",
            "password": CLAVE_PRUEBA,
            "must_change_password": False,
        },
        {
            "email": "solicitante@emi.edu.bo",
            "nombre_completo": "Usuario",
            "rol": "SOLICITANTE",
            "password": CLAVE_PRUEBA,
            "must_change_password": False,
        },
        {
            "email": "nuevo.ingreso@emi.edu.bo",
            "nombre_completo": "Usuario Recien Creado",
            "rol": "SOLICITANTE",
            "password": CLAVE_PRUEBA,
            "must_change_password": True,
        },
    ]

    @transaction.atomic
    def handle(self, *args, **options):

        for datos in self.USUARIOS:

            rol = Rol.objects.get(codigo=datos["rol"])

            usuario, creado = Usuario.objects.get_or_create(
                email=datos["email"],
                defaults={
                    "username": datos["email"].split("@")[0],
                    "nombre_completo": datos["nombre_completo"],
                    "is_active": True,
                },
            )

            usuario.set_password(datos["password"])
            usuario.nombre_completo = datos["nombre_completo"]
            usuario.must_change_password = datos["must_change_password"]
            usuario.is_active = True
            usuario.failed_attempts = 0
            usuario.locked_until = None
            usuario.save()

            # El esqueleto oficial define un único perfil por cuenta.
            UsuarioRol.objects.filter(
                usuario=usuario,
                activo=True,
            ).exclude(rol=rol).update(activo=False)

            asignacion = UsuarioRol.objects.filter(
                usuario=usuario,
                rol=rol,
                area=None,
            ).first()
            if asignacion:
                if not asignacion.activo:
                    asignacion.activo = True
                    asignacion.save(update_fields=["activo"])
            else:
                UsuarioRol.objects.create(
                    usuario=usuario,
                    rol=rol,
                    area=None,
                    activo=True,
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f"{'Creado' if creado else 'Actualizado'}: "
                    f"{usuario.email} ({datos['rol']})"
                )
            )

        self.stdout.write(self.style.SUCCESS("Cuentas de prueba listas."))
