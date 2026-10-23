from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("compras", "0001_initial")]
    operations = [
        migrations.AddField(model_name="solicitudcompra", name="informe", field=models.FileField(blank=True, null=True, upload_to="compras/expedientes/informes/")),
        migrations.AddField(model_name="solicitudcompra", name="poa", field=models.FileField(blank=True, null=True, upload_to="compras/expedientes/poa/")),
        migrations.AddField(model_name="solicitudcompra", name="pedido", field=models.FileField(blank=True, null=True, upload_to="compras/expedientes/pedidos/")),
        migrations.AddField(model_name="solicitudcompra", name="proforma", field=models.FileField(blank=True, null=True, upload_to="compras/expedientes/proformas/")),
        migrations.AddField(model_name="solicitudcompra", name="certificacion_presupuestaria", field=models.FileField(blank=True, null=True, upload_to="compras/certificaciones/")),
        migrations.AddField(model_name="solicitudcompra", name="factura", field=models.FileField(blank=True, null=True, upload_to="compras/descargos/facturas/")),
        migrations.AddField(model_name="solicitudcompra", name="acta_conformidad", field=models.FileField(blank=True, null=True, upload_to="compras/descargos/actas/")),
        migrations.AddField(model_name="solicitudcompra", name="fotograma", field=models.FileField(blank=True, null=True, upload_to="compras/descargos/fotogramas/")),
        migrations.AddField(model_name="solicitudcompra", name="motivo_rechazo", field=models.TextField(blank=True)),
        migrations.AddField(model_name="solicitudcompra", name="monto_desembolsado", field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
        migrations.AddField(model_name="solicitudcompra", name="responsable_adquisicion", field=models.CharField(blank=True, max_length=150)),
        migrations.AddField(model_name="solicitudcompra", name="monto_real", field=models.DecimalField(blank=True, decimal_places=2, max_digits=12, null=True)),
        migrations.AddField(model_name="solicitudcompra", name="proveedor", field=models.CharField(blank=True, max_length=180)),
        migrations.AddField(model_name="solicitudcompra", name="cerrado_inmutable", field=models.BooleanField(default=False)),
        migrations.AlterField(model_name="solicitudcompra", name="estado", field=models.CharField(choices=[("CREADO_PENDIENTE_DAF", "Creado - pendiente DAF"), ("EVALUADO_PENDIENTE_CERTIFICACION", "Evaluado - pendiente de certificación"), ("CERTIFICADO_PENDIENTE_VERIFICACION", "Certificado - pendiente de verificación"), ("VERIFICADO_PENDIENTE_AUTORIZACION", "Verificado - pendiente de autorización"), ("APROBADO_PARA_DESEMBOLSO", "Aprobado para desembolso"), ("FONDOS_DESEMBOLSADOS", "Fondos desembolsados"), ("COMPRA_REGISTRADA", "Compra realizada - pendiente de entrega"), ("COMPRADO_Y_ENTREGADO", "Comprado y entregado"), ("DESCARGO_PENDIENTE_LIQUIDACION", "Descargo pendiente de liquidación"), ("CERRADO_ARCHIVADO", "Cerrado y archivado"), ("NUEVO", "Nuevo"), ("EN_COTIZACION", "En cotización"), ("EN_APROBACION", "En aprobación"), ("APROBADO", "Aprobado"), ("ORDEN_EMITIDA", "Orden emitida"), ("EN_TRANSITO", "En tránsito"), ("RECIBIDO", "Recibido"), ("EN_VERIFICACION", "En verificación"), ("CERRADO", "Cerrado"), ("RECHAZADO", "Rechazado"), ("ANULADO", "Anulado")], default="CREADO_PENDIENTE_DAF", max_length=50)),
    ]
