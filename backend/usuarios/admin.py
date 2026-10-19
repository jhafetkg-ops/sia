from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario

    list_display = (
        'email',
        'nombre_completo',
        'is_active',
        'is_staff',
        'must_change_password',
    )

    search_fields = (
        'email',
        'nombre_completo',
    )

    ordering = ('email',)

    fieldsets = UserAdmin.fieldsets + (
        (
            'SIA',
            {
                'fields': (
                    'nombre_completo',
                    'must_change_password',
                    'failed_attempts',
                    'locked_until',
                    'last_login_ip',
                )
            },
        ),
    )

from .models import Area, Rol, UsuarioRol


@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "nombre",
        "activo",
    )

    search_fields = (
        "codigo",
        "nombre",
    )


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "nombre",
        "es_global",
        "activo",
    )

    search_fields = (
        "codigo",
        "nombre",
    )


@admin.register(UsuarioRol)
class UsuarioRolAdmin(admin.ModelAdmin):
    list_display = (
        "usuario",
        "rol",
        "area",
        "activo",
        "fecha_asignacion",
    )

    list_filter = (
        "rol",
        "area",
        "activo",
    )