from django.db import migrations


ESTADOS = [
    ("RECIBIDO", "Recibido", True, False),
    ("DERIVADO", "Derivado al auxiliar", False, False),
    ("REVISION_ALMACEN", "En revisión de almacén", False, False),
    ("EN_ESPERA_COMPRA", "En espera de Compra Caja Chica", False, False),
    ("EN_MANTENIMIENTO", "En mantenimiento", False, False),
    ("INFORME_REGISTRADO", "Informe registrado", False, False),
    ("FINALIZADO", "Finalizado", False, True),
    ("ANULADO", "Anulado", False, True),
]


def crear_seed(apps, schema_editor):
    EstadoMantenimiento = apps.get_model("mantenimiento", "EstadoMantenimiento")

    for codigo, nombre, es_inicial, es_terminal in ESTADOS:
        EstadoMantenimiento.objects.get_or_create(
            codigo=codigo,
            defaults={
                "nombre": nombre,
                "es_inicial": es_inicial,
                "es_terminal": es_terminal,
                "activo": True,
            },
        )


def eliminar_seed(apps, schema_editor):
    # No se elimina: es un catálogo operativo, no datos de prueba.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("mantenimiento", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(crear_seed, eliminar_seed),
    ]
