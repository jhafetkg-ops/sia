from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.core.mail import EmailMultiAlternatives

from django.utils import timezone


from rest_framework import status

from rest_framework.decorators import (
    api_view,
    permission_classes,
)

from rest_framework.permissions import (
    AllowAny,
)

from rest_framework.response import Response


from auditoria.utils import registrar_bitacora

from usuarios.models import Usuario

from .models import CodigoRecuperacion


# ==========================================================
# AUXILIARES
# ==========================================================

def obtener_ip(request):

    forwarded = request.META.get(
        "HTTP_X_FORWARDED_FOR"
    )

    if forwarded:
        return forwarded.split(",")[0].strip()

    return request.META.get(
        "REMOTE_ADDR"
    )


def validar_password(password, usuario=None):

    # Delega en AUTH_PASSWORD_VALIDATORS (incluye
    # ComplejidadPasswordValidator) para no duplicar la
    # política de contraseñas en un tercer lugar del proyecto.
    try:
        password_validation.validate_password(password, user=usuario)
    except DjangoValidationError as error:
        return " ".join(error.messages)

    return None


# ==========================================================
# ENVIAR CORREO
# ==========================================================

def enviar_codigo_correo(
    usuario,
    codigo
):

    asunto = (
        "SIA - Código de recuperación"
    )


    texto = f"""
SIA - Escuela Militar de Ingeniería

Hola {usuario.nombre_completo}:

Se solicitó recuperar la contraseña de su cuenta SIA.

Código de verificación:

{codigo}

Este código tiene una vigencia de 10 minutos.

Si usted no realizó esta solicitud, puede ignorar este mensaje.

SIA
Escuela Militar de Ingeniería
Unidad Académica Santa Cruz
"""


    html = f"""
    <div style="
        font-family:Arial,Helvetica,sans-serif;
        max-width:600px;
        margin:auto;
        color:#17324a;
    ">

        <div style="
            background:#073b6f;
            padding:24px;
            border-bottom:5px solid #f2c400;
        ">

            <h1 style="
                color:white;
                margin:0;
                font-size:28px;
            ">
                SIA
            </h1>

            <p style="
                color:#dce8f2;
                margin:5px 0 0;
            ">
                Escuela Militar de Ingeniería
            </p>

        </div>


        <div style="
            padding:28px;
            background:#ffffff;
            border:1px solid #e0e7ed;
        ">

            <h2 style="
                color:#17324a;
            ">
                Recuperación de contraseña
            </h2>


            <p>
                Hola
                <strong>
                    {usuario.nombre_completo}
                </strong>,
            </p>


            <p>
                Recibimos una solicitud para
                recuperar el acceso a su cuenta
                de SIA.
            </p>


            <div style="
                margin:25px 0;
                padding:22px;
                background:#f4f7f9;
                border-left:5px solid #f2c400;
                text-align:center;
            ">

                <span style="
                    color:#71818f;
                    font-size:12px;
                ">
                    CÓDIGO DE VERIFICACIÓN
                </span>

                <div style="
                    margin-top:8px;
                    color:#073b6f;
                    font-size:34px;
                    font-weight:bold;
                    letter-spacing:8px;
                ">
                    {codigo}
                </div>

            </div>


            <p>
                El código tendrá una vigencia
                de <strong>10 minutos</strong>.
            </p>


            <p style="
                color:#71818f;
                font-size:12px;
            ">
                Si usted no realizó esta
                solicitud, ignore este correo.
            </p>

        </div>


        <div style="
            padding:15px;
            background:#f4f6f8;
            text-align:center;
            color:#7e8b96;
            font-size:11px;
        ">

            SIA · EMI Santa Cruz

        </div>

    </div>
    """


    correo = EmailMultiAlternatives(
        subject=asunto,

        body=texto,

        to=[
            usuario.email
        ]
    )


    correo.attach_alternative(
        html,
        "text/html"
    )


    correo.send(
        fail_silently=False
    )


# ==========================================================
# PASO 1
# SOLICITAR CÓDIGO
# ==========================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def solicitar_codigo(request):

    email = (
        request.data
        .get("email", "")
        .strip()
        .lower()
    )


    if not email:

        return Response(
            {
                "ok": False,
                "mensaje":
                    "Ingrese su correo institucional."
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    try:

        usuario = Usuario.objects.get(
            email__iexact=email
        )

    except Usuario.DoesNotExist:

        # No revelar si existe o no
        return Response(
            {
                "ok": True,

                "mensaje":
                    (
                        "Si el correo se encuentra "
                        "registrado, recibirá un código "
                        "de recuperación."
                    )
            },
            status=status.HTTP_200_OK
        )


    if not usuario.is_active:

        return Response(
            {
                "ok": False,

                "mensaje":
                    (
                        "La cuenta se encuentra "
                        "inactiva. Contacte al "
                        "administrador."
                    )
            },
            status=status.HTTP_403_FORBIDDEN
        )


    registro, codigo = (
        CodigoRecuperacion
        .crear_para_usuario(
            usuario=usuario,
            ip=obtener_ip(request)
        )
    )


    try:

        enviar_codigo_correo(
            usuario,
            codigo
        )

    except Exception as error:

        registro.delete()

        print(
            "ERROR DE CORREO:",
            error
        )

        return Response(
            {
                "ok": False,

                "mensaje":
                    (
                        "No fue posible enviar el "
                        "correo. Revise la "
                        "configuración SMTP."
                    )
            },
            status=status.HTTP_503_SERVICE_UNAVAILABLE
        )


    registrar_bitacora(
        request=request,

        usuario=usuario,

        accion=
            "SOLICITUD_RECUPERACION",

        modulo=
            "Autenticación",

        detalle=
            (
                "El usuario solicitó un "
                "código para recuperar "
                "su contraseña."
            ),

        nivel="SECURITY",
    )


    return Response(
        {
            "ok": True,

            "mensaje":
                (
                    "Se envió un código de "
                    "verificación al correo "
                    "institucional."
                ),

            "email":
                usuario.email,
        },
        status=status.HTTP_200_OK
    )


# ==========================================================
# PASO 2
# VERIFICAR CÓDIGO
# ==========================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def verificar_codigo(request):

    email = (
        request.data
        .get("email", "")
        .strip()
        .lower()
    )

    codigo = (
        request.data
        .get("codigo", "")
        .strip()
    )


    if not email or not codigo:

        return Response(
            {
                "ok": False,

                "mensaje":
                    (
                        "Correo y código "
                        "son obligatorios."
                    )
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    try:

        usuario = Usuario.objects.get(
            email__iexact=email
        )

    except Usuario.DoesNotExist:

        return Response(
            {
                "ok": False,
                "mensaje":
                    "Código inválido."
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    registro = (
        CodigoRecuperacion.objects
        .filter(
            usuario=usuario,
            usado=False
        )
        .order_by("-creado_en")
        .first()
    )


    if not registro:

        return Response(
            {
                "ok": False,

                "mensaje":
                    (
                        "No existe una solicitud "
                        "de recuperación activa."
                    )
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    if timezone.now() > registro.expira_en:

        registro.usado = True

        registro.save(
            update_fields=[
                "usado"
            ]
        )

        return Response(
            {
                "ok": False,

                "mensaje":
                    (
                        "El código ha expirado. "
                        "Solicite uno nuevo."
                    )
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    if registro.intentos >= 5:

        registro.usado = True

        registro.save(
            update_fields=[
                "usado"
            ]
        )

        return Response(
            {
                "ok": False,

                "mensaje":
                    (
                        "Se superó el número "
                        "máximo de intentos."
                    )
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    if not registro.comprobar_codigo(
        codigo
    ):

        registro.intentos += 1

        registro.save(
            update_fields=[
                "intentos"
            ]
        )


        registrar_bitacora(
            request=request,

            usuario=usuario,

            accion=
                "CODIGO_RECUPERACION_INVALIDO",

            modulo="Autenticación",

            detalle=
                (
                    "Se ingresó un código "
                    "de recuperación incorrecto."
                ),

            nivel="SECURITY",
        )


        return Response(
            {
                "ok": False,

                "mensaje":
                    "El código ingresado es incorrecto."
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    registro.verificado = True

    registro.save(
        update_fields=[
            "verificado"
        ]
    )


    registrar_bitacora(
        request=request,

        usuario=usuario,

        accion=
            "CODIGO_RECUPERACION_VALIDADO",

        modulo="Autenticación",

        detalle=
            (
                "El código de recuperación "
                "fue validado correctamente."
            ),

        nivel="SECURITY",
    )


    return Response(
        {
            "ok": True,

            "mensaje":
                "Código verificado correctamente."
        },
        status=status.HTTP_200_OK
    )


# ==========================================================
# PASO 3
# CREAR NUEVA CONTRASEÑA
# ==========================================================

@api_view(["POST"])
@permission_classes([AllowAny])
def restablecer_password(request):

    email = (
        request.data
        .get("email", "")
        .strip()
        .lower()
    )

    nueva_password = (
        request.data
        .get("nueva_password", "")
    )

    confirmar_password = (
        request.data
        .get("confirmar_password", "")
    )


    if (
        not email
        or
        not nueva_password
        or
        not confirmar_password
    ):

        return Response(
            {
                "ok": False,
                "mensaje":
                    "Todos los campos son obligatorios."
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    if (
        nueva_password
        != confirmar_password
    ):

        return Response(
            {
                "ok": False,

                "mensaje":
                    "Las contraseñas no coinciden."
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    error = validar_password(
        nueva_password
    )


    if error:

        return Response(
            {
                "ok": False,
                "mensaje": error
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    try:

        usuario = Usuario.objects.get(
            email__iexact=email
        )

    except Usuario.DoesNotExist:

        return Response(
            {
                "ok": False,
                "mensaje":
                    "Solicitud inválida."
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    registro = (
        CodigoRecuperacion.objects
        .filter(
            usuario=usuario,
            usado=False,
            verificado=True
        )
        .order_by("-creado_en")
        .first()
    )


    if not registro:

        return Response(
            {
                "ok": False,

                "mensaje":
                    (
                        "Primero debe verificar "
                        "el código enviado a "
                        "su correo."
                    )
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    if not registro.esta_vigente():

        return Response(
            {
                "ok": False,
                "mensaje":
                    "La solicitud ha expirado."
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    if usuario.check_password(
        nueva_password
    ):

        return Response(
            {
                "ok": False,

                "mensaje":
                    (
                        "La nueva contraseña "
                        "debe ser diferente "
                        "a la anterior."
                    )
            },
            status=status.HTTP_400_BAD_REQUEST
        )


    # CAMBIAR CONTRASEÑA
    usuario.set_password(
        nueva_password
    )


    # Ya no se considera primer ingreso
    usuario.must_change_password = False


    # Quitar bloqueo
    usuario.failed_attempts = 0
    usuario.locked_until = None


    usuario.save(
        update_fields=[
            "password",
            "must_change_password",
            "failed_attempts",
            "locked_until",
        ]
    )


    registro.usado = True

    registro.save(
        update_fields=[
            "usado"
        ]
    )


    # Invalidar tokens anteriores
    try:

        usuario.auth_token.delete()

    except Exception:
        pass


    registrar_bitacora(
        request=request,

        usuario=usuario,

        accion=
            "CAMBIO_CONTRASENA_RECUPERACION",

        modulo="Autenticación",

        detalle=
            (
                "El usuario restableció "
                "su contraseña mediante "
                "verificación por correo."
            ),

        nivel="SECURITY",
    )


    return Response(
        {
            "ok": True,

            "mensaje":
                (
                    "Su contraseña fue "
                    "actualizada correctamente."
                )
        },
        status=status.HTTP_200_OK
    )