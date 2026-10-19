from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import (
    CategoriaTicketViewSet,
    EstadoTicketViewSet,
    TicketViewSet,
    NotificacionSoporteViewSet,
)


router = DefaultRouter()

router.register(
    r"categorias",
    CategoriaTicketViewSet,
    basename="categoria-soporte"
)

router.register(r"notificaciones", NotificacionSoporteViewSet, basename="notificacion-soporte")

router.register(
    r"estados",
    EstadoTicketViewSet,
    basename="estado-soporte"
)

router.register(
    r"tickets",
    TicketViewSet,
    basename="ticket-soporte"
)


urlpatterns = [
    path(
        "",
        include(router.urls)
    ),
]
