from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    EstadoMantenimientoViewSet,
    RequerimientoMantenimientoViewSet,
)


router = DefaultRouter()

router.register(
    r"estados",
    EstadoMantenimientoViewSet,
    basename="estado-mantenimiento"
)

router.register(
    r"requerimientos",
    RequerimientoMantenimientoViewSet,
    basename="requerimiento-mantenimiento"
)


urlpatterns = [
    path(
        "",
        include(router.urls)
    ),
]