from rest_framework.routers import DefaultRouter

from .views import SolicitudCompraViewSet


router = DefaultRouter()

router.register(
    "solicitudes",
    SolicitudCompraViewSet,
    basename="solicitudes-compras"
)

urlpatterns = router.urls