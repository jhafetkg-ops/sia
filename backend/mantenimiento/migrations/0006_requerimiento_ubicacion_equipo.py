from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mantenimiento", "0005_estados_bpmn"),
    ]

    operations = [
        migrations.AddField(
            model_name="requerimientomantenimiento",
            name="referencia_ubicacion",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
        migrations.AddField(
            model_name="requerimientomantenimiento",
            name="equipo_afectado",
            field=models.CharField(blank=True, default="", max_length=200),
        ),
    ]
