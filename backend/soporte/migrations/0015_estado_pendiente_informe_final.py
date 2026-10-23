from django.db import migrations


def crear_estado(apps, schema_editor):
    EstadoTicket = apps.get_model("soporte", "EstadoTicket")
    EstadoTicket.objects.get_or_create(
        codigo="PENDIENTE_INFORME_FINAL",
        defaults={
            "nombre": "Pendiente de informe final",
            "descripcion": "El solicitante confirmó conformidad y la Jefatura UTIC debe validar el informe final.",
            "es_inicial": False,
            "es_terminal": False,
            "activo": True,
        },
    )


class Migration(migrations.Migration):
    dependencies = [("soporte", "0014_expediente_soporte_integral")]
    operations = [migrations.RunPython(crear_estado, migrations.RunPython.noop)]
