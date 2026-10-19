from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("mantenimiento", "0007_merge_20260905_0006")]
    operations = [migrations.AddField(
        model_name="requerimientomantenimiento", name="informe_compra",
        field=models.FileField(upload_to="mantenimiento/informes_compra/%Y/%m/", blank=True, null=True),
    )]
