from django.db import migrations, models


def avanzar_expedientes_certificados(apps, schema_editor):
    """El BPMN de Caja Chica lleva la certificación de la DAF directamente a
    la autorización del Director: Tesorería solo desembolsa. Los expedientes
    que esperaban la verificación de Tesorería pasan a esperar al Director."""

    SolicitudCompra = apps.get_model("compras", "SolicitudCompra")

    SolicitudCompra.objects.filter(
        estado="CERTIFICADO_PENDIENTE_VERIFICACION"
    ).update(estado="VERIFICADO_PENDIENTE_AUTORIZACION")


def revertir(apps, schema_editor):
    # No se puede distinguir qué expedientes venían del estado anterior.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("compras", "0004_asignacion_tecnico_daf"),
    ]

    operations = [
        migrations.RunPython(avanzar_expedientes_certificados, revertir),
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
                    ("DESCARGO_PENDIENTE_LIQUIDACION", "Descargo pendiente de liquidación"),
                    ("CERRADO_ARCHIVADO", "Cerrado y archivado"),
                    ("RECHAZADO", "Rechazado"),
                    ("ANULADO", "Anulado"),
                ],
                default="CREADO_PENDIENTE_DAF",
                max_length=50,
            ),
        ),
    ]
