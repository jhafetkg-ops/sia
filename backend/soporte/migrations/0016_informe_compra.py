from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("soporte", "0015_estado_pendiente_informe_final")]
    operations = [migrations.AddField(
        model_name="ticket", name="informe_compra",
        field=models.FileField(upload_to="soporte/informes_compra/%Y/%m/", blank=True, null=True),
    )]
