from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("soporte", "0016_informe_compra")]
    operations = [
        migrations.AddField(
            model_name="ticket",
            name="informe_final_pdf",
            field=models.FileField(
                upload_to="soporte/informes_finales/%Y/%m/",
                blank=True,
                null=True,
                help_text="PDF elaborado y remitido por la Jefatura UTIC a Dirección.",
            ),
        ),
    ]
