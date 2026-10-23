from django.db import migrations, models


def crear_areas_oficiales(apps, schema_editor):
    Area = apps.get_model("usuarios", "Area")
    for codigo, nombre in (
        ("DAF", "DAF"),
        ("MANTENIMIENTO", "Mantenimiento"),
        ("UTIC", "UTIC"),
    ):
        Area.objects.update_or_create(
            codigo=codigo,
            defaults={"nombre": nombre, "activo": True},
        )


class Migration(migrations.Migration):
    dependencies = [("usuarios", "0004_delegacionaprobacion")]

    operations = [
        migrations.AddField(
            model_name="usuariorol",
            name="especialidad",
            field=models.CharField(blank=True, default="", max_length=80),
        ),
        migrations.RunPython(crear_areas_oficiales, migrations.RunPython.noop),
    ]
