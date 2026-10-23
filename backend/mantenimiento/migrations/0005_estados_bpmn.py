from django.db import migrations


NUEVOS = [
    ("VALIDADO", "Validado - pendiente de clasificación", False, False),
    ("RECHAZADO", "Ticket no procede", False, True),
    ("CERRADO_SIN_COMPRA", "Cerrado sin compra", False, True),
    ("CONFORMIDAD_INFORMADA", "Conformidad informada", False, False),
]


def crear(apps, schema_editor):
    """Estados que el BPMN de Mantenimiento exige y que no existían:
    la validación previa del ticket, sus dos cierres sin atención y la
    conformidad anterior al informe final."""

    EstadoMantenimiento = apps.get_model("mantenimiento", "EstadoMantenimiento")

    for codigo, nombre, inicial, terminal in NUEVOS:
        EstadoMantenimiento.objects.update_or_create(
            codigo=codigo,
            defaults={
                "nombre": nombre,
                "es_inicial": inicial,
                "es_terminal": terminal,
                "activo": True,
            },
        )


def borrar(apps, schema_editor):
    EstadoMantenimiento = apps.get_model("mantenimiento", "EstadoMantenimiento")
    EstadoMantenimiento.objects.filter(
        codigo__in=[c for c, _, _, _ in NUEVOS]
    ).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("mantenimiento", "0004_flujo_bpmn_mantenimiento"),
    ]

    operations = [migrations.RunPython(crear, borrar)]
