import json

from django.http import JsonResponse

from rest_framework.authtoken.models import Token


# ==========================================================
# CAMBIO OBLIGATORIO DE CONTRASEÑA (HU-02)
# ==========================================================
#
# El frontend ya redirige a /cambiar-contrasena cuando
# must_change_password=True, pero eso es solo routing de
# cliente: un pentester puede llamar la API directamente con
# el token y saltarse esa pantalla. Este middleware repite la
# regla en el backend, que es la fuente de verdad real: ningún
# endpoint (salvo los estrictamente necesarios para cambiar la
# contraseña) responde mientras la bandera siga activa.
#
# ==========================================================

RUTAS_EXENTAS = (
    "/api/usuarios/login/",
    "/api/usuarios/mi-contexto/",
    "/api/usuarios/cambiar-password-obligatorio/",
)


class CambioPasswordObligatorioMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        if (
            request.method != "OPTIONS"
            and request.path.startswith("/api/")
            and request.path not in RUTAS_EXENTAS
        ):

            encabezado = request.META.get("HTTP_AUTHORIZATION", "")

            if encabezado.startswith("Token "):

                clave = encabezado.split(" ", 1)[1].strip()

                token = (
                    Token.objects
                    .select_related("user")
                    .filter(key=clave)
                    .first()
                )

                if (
                    token
                    and token.user.is_active
                    and token.user.must_change_password
                ):

                    return JsonResponse(
                        {
                            "ok": False,
                            "detalle": (
                                "Debe cambiar su contraseña antes "
                                "de continuar."
                            ),
                            "must_change_password": True,
                        },
                        status=403,
                    )

        return self.get_response(request)
