from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("mantenimiento", "0002_seed_estados")]
    operations = [
        migrations.AddField(model_name="requerimientomantenimiento", name="prioridad_jefatura", field=models.CharField(blank=True, max_length=10)),
        migrations.AddField(model_name="requerimientomantenimiento", name="criterio_prioridad", field=models.TextField(blank=True)),
    ]
