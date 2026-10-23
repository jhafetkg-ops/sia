from django.db import migrations, models


class Migration(migrations.Migration):
    """El proceso de Caja Chica no contempla una jefatura de la DAF: la
    solicitud llega directamente a la DAF, que verifica requisitos y emite
    la certificación presupuestaria. Por eso desaparecen la jefatura "DAF"
    y el informe de aprobación que solo ella podía elaborar."""

    dependencies = [
        ("usuarios", "0006_informejefatura"),
    ]

    operations = [
        migrations.AlterField(
            model_name="informejefatura",
            name="jefatura",
            field=models.CharField(
                choices=[("UTIC", "UTIC"), ("MANTENIMIENTO", "Mantenimiento")],
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="informejefatura",
            name="tipo",
            field=models.CharField(
                choices=[("ACTIVIDADES", "Informe de actividades")],
                default="ACTIVIDADES",
                max_length=20,
            ),
        ),
    ]
