from django.urls import (
    path,
    include,
)

from rest_framework.routers import (
    DefaultRouter,
)

from .views import (
    AreaViewSet,
    RolViewSet,
    UsuarioViewSet,
    UsuarioRolViewSet,
    PermisoViewSet,
    RolPermisoViewSet,
    DelegacionAprobacionViewSet,
    InformeJefaturaViewSet,
    login_view,
    mi_contexto,
    mi_perfil,
    usuarios_por_rol,
    buscar_usuario_por_email,
    cambiar_password_obligatorio,
)


# ==========================================================
# ROUTER
# ==========================================================

router = DefaultRouter()


# ==========================================================
# ÁREAS
# ==========================================================

router.register(
    r"areas",
    AreaViewSet,
    basename="area"
)


# ==========================================================
# ROLES
# ==========================================================

router.register(
    r"roles",
    RolViewSet,
    basename="rol"
)


# ==========================================================
# PERMISOS
# ==========================================================

router.register(
    r"permisos",
    PermisoViewSet,
    basename="permiso"
)


# ==========================================================
# ROL - PERMISO
# ==========================================================

router.register(
    r"rol-permisos",
    RolPermisoViewSet,
    basename="rol-permiso"
)


# ==========================================================
# USUARIOS
# ==========================================================

router.register(
    r"usuarios",
    UsuarioViewSet,
    basename="usuario"
)


# ==========================================================
# USUARIO - ROL
# ==========================================================

router.register(
    r"usuario-roles",
    UsuarioRolViewSet,
    basename="usuario-rol"
)


# ==========================================================
# DELEGACIÓN TEMPORAL DE APROBACIÓN
# ==========================================================

router.register(
    r"delegaciones",
    DelegacionAprobacionViewSet,
    basename="delegacion-aprobacion"
)

router.register(
    r"informes-jefatura",
    InformeJefaturaViewSet,
    basename="informe-jefatura"
)


# ==========================================================
# URLS ESPECIALES
# ==========================================================

urlpatterns = [

    # ------------------------------------------------------
    # LOGIN
    # ------------------------------------------------------

    path(
        "login/",
        login_view,
        name="login"
    ),


    # ------------------------------------------------------
    # CONTEXTO DEL USUARIO AUTENTICADO
    # ------------------------------------------------------
    #
    # Devuelve:
    #
    # usuario
    # roles
    # áreas
    # permisos
    #
    # GET /api/usuarios/mi-contexto/
    #
    # ------------------------------------------------------

    path(
        "mi-contexto/",
        mi_contexto,
        name="mi-contexto"
    ),

    path(
        "mi-perfil/",
        mi_perfil,
        name="mi-perfil"
    ),


    # ------------------------------------------------------
    # USUARIOS POR ROL (SELECTORES OPERATIVOS)
    # ------------------------------------------------------

    path(
        "usuarios-por-rol/",
        usuarios_por_rol,
        name="usuarios-por-rol"
    ),

    path(
        "buscar-usuario/",
        buscar_usuario_por_email,
        name="buscar-usuario"
    ),


    # ------------------------------------------------------
    # CAMBIO OBLIGATORIO DE CONTRASEÑA
    # ------------------------------------------------------

    path(
        "cambiar-password-obligatorio/",
        cambiar_password_obligatorio,
        name="cambiar-password-obligatorio"
    ),


    # ------------------------------------------------------
    # ROUTER DRF
    # ------------------------------------------------------

    path(
        "",
        include(
            router.urls
        )
    ),
]
