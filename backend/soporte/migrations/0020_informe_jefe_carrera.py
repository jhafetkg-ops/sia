from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("soporte", "0019_notificacion_soporte")]
    operations = [
        migrations.AddField(model_name="ticket", name="informe_jefe_carrera", field=models.TextField(blank=True)),
        migrations.AddField(model_name="ticket", name="informe_jefe_carrera_pdf", field=models.FileField(blank=True, null=True, upload_to="soporte/informes_jefe_carrera/%Y/%m/")),
        migrations.AddField(model_name="ticket", name="informe_jefe_carrera_en", field=models.DateTimeField(blank=True, null=True)),
    ]
