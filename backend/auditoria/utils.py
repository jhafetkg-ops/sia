from .models import Bitacora


def obtener_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR")

    if forwarded:
        return forwarded.split(",")[0].strip()

    return request.META.get("REMOTE_ADDR")


def registrar_bitacora(
    request,
    accion,
    modulo,
    detalle="",
    nivel="INFO",
    usuario=None,
):
    """
    Registra una acción importante dentro de SIGTA.
    """

    usuario_registro = usuario

    if usuario_registro is None:
        try:
            if request.user.is_authenticated:
                usuario_registro = request.user
        except Exception:
            usuario_registro = None

    Bitacora.objects.create(
        usuario=usuario_registro,
        accion=accion,
        modulo=modulo,
        detalle=detalle,
        nivel=nivel,
        ip=obtener_ip(request),
    )