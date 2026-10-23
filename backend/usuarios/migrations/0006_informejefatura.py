from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("usuarios", "0005_usuariorol_especialidad_areas"),
    ]

    operations = [
        migrations.CreateModel(
            name="InformeJefatura",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("jefatura", models.CharField(choices=[("UTIC", "UTIC"), ("MANTENIMIENTO", "Mantenimiento"), ("DAF", "DAF")], max_length=20)),
                ("tipo", models.CharField(choices=[("ACTIVIDADES", "Informe de actividades"), ("APROBACION_DAF", "Informe de aprobación DAF")], default="ACTIVIDADES", max_length=20)),
                ("titulo", models.CharField(max_length=200)),
                ("periodo", models.CharField(max_length=30)),
                ("contenido", models.TextField()),
                ("enviado_director", models.BooleanField(default=False)),
                ("creado_en", models.DateTimeField(auto_now_add=True)),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
                ("jefe", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="informes_jefatura", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["-creado_en"]},
        ),
    ]
