# Generated manually for the DAF documentary-review gate.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("compras", "0009_solicitudcompra_comprobante_desembolso_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AlterField(
            model_name="solicitudcompra",
            name="estado",
            field=models.CharField(
                choices=[
                    ("CREADO_PENDIENTE_DAF", "Creado - pendiente DAF"),
                    ("EVALUADO_PENDIENTE_CERTIFICACION", "Evaluado - pendiente de certificación"),
                    ("OBSERVADO_DOCUMENTACION_DAF", "Observado por documentación - pendiente de corrección"),
                    ("VERIFICADO_PENDIENTE_AUTORIZACION", "Certificado - pendiente de autorización"),
                    ("APROBADO_PARA_DESEMBOLSO", "Aprobado para desembolso"),
                    ("FONDOS_DESEMBOLSADOS", "Fondos desembolsados"),
                    ("COMPRA_REGISTRADA", "Compra realizada - pendiente de entrega"),
                    ("COMPRADO_Y_ENTREGADO", "Comprado y entregado"),
                    ("DESCARGO_PENDIENTE_LIQUIDACION", "Acta firmada - pendiente de recepción"),
                    ("CERRADO_ARCHIVADO", "Cerrado y archivado"),
                    ("RECHAZADO", "Rechazado"),
                    ("ANULADO", "Anulado"),
                ],
                default="CREADO_PENDIENTE_DAF",
                max_length=50,
            ),
        ),
        migrations.AddField(
            model_name="solicitudcompra",
            name="documentos_aprobados_en",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="solicitudcompra",
            name="documentos_aprobados_por",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="expedientes_documentos_aprobados_daf", to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="solicitudcompra",
            name="observacion_documentacion_daf",
            field=models.TextField(blank=True),
        ),
    ]
