import hashlib
import secrets

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone


class CodigoRecuperacion(models.Model):

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="codigos_recuperacion"
    )

    codigo_hash = models.CharField(
        max_length=64
    )

    creado_en = models.DateTimeField(
        auto_now_add=True
    )

    expira_en = models.DateTimeField()

    usado = models.BooleanField(
        default=False
    )

    verificado = models.BooleanField(
        default=False
    )

    intentos = models.PositiveIntegerField(
        default=0
    )

    ip_solicitud = models.GenericIPAddressField(
        null=True,
        blank=True
    )


    class Meta:
        ordering = [
            "-creado_en"
        ]


    def __str__(self):

        return (
            f"Recuperación "
            f"{self.usuario.email} - "
            f"{self.creado_en}"
        )


    @staticmethod
    def generar_codigo():

        # 000000 - 999999
        return f"{secrets.randbelow(1000000):06d}"


    @staticmethod
    def generar_hash(codigo):

        return hashlib.sha256(
            codigo.encode("utf-8")
        ).hexdigest()


    def comprobar_codigo(
        self,
        codigo
    ):

        return (
            self.codigo_hash
            ==
            self.generar_hash(codigo)
        )


    def esta_vigente(self):

        return (
            not self.usado
            and
            timezone.now()
            <= self.expira_en
        )


    @classmethod
    def crear_para_usuario(
        cls,
        usuario,
        ip=None
    ):

        # Invalidar códigos anteriores
        cls.objects.filter(
            usuario=usuario,
            usado=False
        ).update(
            usado=True
        )


        codigo = cls.generar_codigo()


        registro = cls.objects.create(

            usuario=usuario,

            codigo_hash=
                cls.generar_hash(codigo),

            expira_en=
                timezone.now()
                + timedelta(minutes=10),

            ip_solicitud=ip,
        )


        return registro, codigo