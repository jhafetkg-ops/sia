import re

from django.core.exceptions import ValidationError


class ComplejidadPasswordValidator:
    """Exige mayúscula, minúscula, número y carácter especial.
    Se registra en AUTH_PASSWORD_VALIDATORS para que la MISMA
    política aplique en todos los puntos donde se fija una
    contraseña: alta de usuario por ADMIN, cambio obligatorio
    de primer ingreso y recuperación de contraseña."""

    def validate(self, password, user=None):

        errores = []

        if not re.search(r"[A-Z]", password):
            errores.append("Debe incluir al menos una letra mayúscula.")

        if not re.search(r"[a-z]", password):
            errores.append("Debe incluir al menos una letra minúscula.")

        if not re.search(r"\d", password):
            errores.append("Debe incluir al menos un número.")

        if not re.search(r"[^\w\s]", password):
            errores.append("Debe incluir al menos un carácter especial.")

        if errores:
            raise ValidationError(errores)

    def get_help_text(self):
        return (
            "La contraseña debe incluir mayúscula, minúscula, "
            "número y carácter especial."
        )
