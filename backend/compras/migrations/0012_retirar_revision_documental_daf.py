from django.db import migrations, models


def restaurar_expedientes_observados(apps, schema_editor):
    SolicitudCompra = apps.get_model("compras", "SolicitudCompra")
    SolicitudCompra.objects.filter(
        estado="OBSERVADO_DOCUMENTACION_DAF"
    ).update(estado="EVALUADO_PENDIENTE_CERTIFICACION")


class Migration(migrations.Migration):

    dependencies = [
        ("compras", "0011_revision_documental_daf"),
    ]

    operations = [
        migrations.RunPython(restaurar_expedientes_observados, migrations.RunPython.noop),
        migrations.RemoveField(model_name="solicitudcompra", name="documentos_aprobados_por"),
        migrations.RemoveField(model_name="solicitudcompra", name="documentos_aprobados_en"),
        migrations.RemoveField(model_name="solicitudcompra", name="observacion_documentacion_daf"),
        migrations.AlterField(
            model_name="solicitudcompra",
            name="estado",
            field=models.CharField(
                choices=[
                    ("CREADO_PENDIENTE_DAF", "Creado - pendiente DAF"),
                    ("EVALUADO_PENDIENTE_CERTIFICACION", "Evaluado - pendiente de certificación"),
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
    ]
