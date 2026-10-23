from django.db import migrations


ESTADOS = [
    ("BORRADOR", "Borrador", True, False),
    ("NUEVO", "Nuevo", True, False),
    ("EN_ANALISIS", "En análisis", False, False),
    ("ASIGNADO", "Asignado", False, False),
    ("EN_EJECUCION", "En ejecución", False, False),
    ("EN_VERIFICACION", "En verificación", False, False),
    ("PENDIENTE_CONFORMIDAD", "Pendiente de conformidad", False, False),
    ("CERRADO", "Cerrado", False, True),
    ("RECHAZADO", "Rechazado", False, True),
    ("ANULADO", "Anulado", False, True),
]

CATEGORIAS = [
    ("HARDWARE", "Hardware"),
    ("SOFTWARE", "Software"),
    ("RED", "Redes y conectividad"),
    ("PREVENTIVO", "Mantenimiento preventivo"),
    ("OTRO", "Otro"),
]


def crear_seed(apps, schema_editor):
    EstadoTicket = apps.get_model("soporte", "EstadoTicket")
    CategoriaTicket = apps.get_model("soporte", "CategoriaTicket")

    for codigo, nombre, es_inicial, es_terminal in ESTADOS:
        EstadoTicket.objects.get_or_create(
            codigo=codigo,
            defaults={
                "nombre": nombre,
                "es_inicial": es_inicial,
                "es_terminal": es_terminal,
                "activo": True,
            },
        )

    for codigo, nombre in CATEGORIAS:
        CategoriaTicket.objects.get_or_create(
            codigo=codigo,
            defaults={"nombre": nombre, "activo": True},
        )


def eliminar_seed(apps, schema_editor):
    # No se elimina: son catálogos operativos, no datos de prueba.
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("soporte", "0005_ticket_asignado_en_ticket_clasificado_en_and_more"),
    ]

    operations = [
        migrations.RunPython(crear_seed, eliminar_seed),
    ]
