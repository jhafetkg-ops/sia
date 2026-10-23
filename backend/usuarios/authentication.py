from django.conf import settings
from django.utils import timezone

from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed


class ExpiringTokenAuthentication(TokenAuthentication):
    """Mismo esquema `Token <key>` de DRF, pero con vida máxima
    de sesión (SESION_TOKEN_HORAS_VALIDEZ). Un token expirado se
    elimina y obliga a iniciar sesión de nuevo: reduce la ventana
    de uso de un token robado o de una sesión olvidada abierta."""

    def authenticate_credentials(self, key):

        usuario, token = super().authenticate_credentials(key)

        if not usuario.is_active:
            raise AuthenticationFailed("Usuario inactivo o eliminado.")

        horas_validez = getattr(settings, "SESION_TOKEN_HORAS_VALIDEZ", 12)
        limite = token.created + timezone.timedelta(hours=horas_validez)

        if timezone.now() > limite:
            token.delete()
            raise AuthenticationFailed(
                "La sesión expiró por seguridad. Inicie sesión nuevamente."
            )

        return (usuario, token)
