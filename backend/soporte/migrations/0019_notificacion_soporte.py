from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [("soporte", "0018_informe_tecnico_pdf"), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(
            name="NotificacionSoporte",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("tipo", models.CharField(choices=[("EXITO", "Aprobación"), ("RECHAZO", "Rechazo"), ("INFO", "Información")], default="INFO", max_length=10)),
                ("titulo", models.CharField(max_length=160)),
                ("mensaje", models.TextField()),
                ("leida", models.BooleanField(default=False)),
                ("creada_en", models.DateTimeField(auto_now_add=True)),
                ("leida_en", models.DateTimeField(blank=True, null=True)),
                ("destinatario", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notificaciones_soporte", to=settings.AUTH_USER_MODEL)),
                ("ticket", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notificaciones", to="soporte.ticket")),
            ],
            options={"ordering": ["-creada_en"]},
        )
    ]
