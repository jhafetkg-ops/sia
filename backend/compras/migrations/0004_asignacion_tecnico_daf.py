from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("compras", "0003_solicitudcompra_componente_verificado_and_more"),
    ]

    operations = [
        migrations.AddField(model_name="solicitudcompra", name="tecnico_daf", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="expedientes_daf_asignados", to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name="solicitudcompra", name="validado_por_jefe_daf", field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="expedientes_daf_validados", to=settings.AUTH_USER_MODEL)),
        migrations.AddField(model_name="solicitudcompra", name="prioridad_daf", field=models.CharField(blank=True, choices=[("BAJA", "Baja"), ("MEDIA", "Media"), ("ALTA", "Alta"), ("URGENTE", "Urgente")], max_length=10)),
        migrations.AddField(model_name="solicitudcompra", name="criterio_prioridad_daf", field=models.TextField(blank=True)),
        migrations.AddField(model_name="solicitudcompra", name="asignado_daf_en", field=models.DateTimeField(blank=True, null=True)),
    ]
