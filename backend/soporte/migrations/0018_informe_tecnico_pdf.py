from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("soporte", "0017_informe_final_pdf")]

    operations = [
        migrations.AddField(
            model_name="ticket",
            name="informe_tecnico_pdf",
            field=models.FileField(blank=True, null=True, upload_to="soporte/informes_tecnicos/%Y/%m/"),
        ),
    ]
