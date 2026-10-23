from django.db import migrations


def crear_seed(apps, schema_editor):
    EstadoTicket = apps.get_model("soporte", "EstadoTicket")

    EstadoTicket.objects.get_or_create(
        codigo="CERRADO_SIN_COMPRA",
        defaults={
            "nombre": "Cerrado sin compra",
            "es_inicial": False,
            "es_terminal": True,
            "activo": True,
        },
    )


def eliminar_seed(apps, schema_editor):
    # No se elimina: es un catálogo operativo, no datos de prueba.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("soporte", "0007_ticket_estado_compra_componente_and_more"),
    ]

    operations = [
        migrations.RunPython(crear_seed, eliminar_seed),
    ]
