from django.core.files.base import ContentFile


def asegurar_informe_tecnico(origen):
    """Reutiliza el PDF del técnico; completa expedientes antiguos sin PDF."""
    if origen.informe_compra and origen.informe_compra.storage.exists(origen.informe_compra.name):
        return origen.informe_compra
    from soporte.informes_pdf import informe_requerimiento, informe_requerimiento_mantenimiento
    generar = informe_requerimiento if origen._meta.app_label == "soporte" else informe_requerimiento_mantenimiento
    origen.informe_compra.save(
        f"informe-requerimiento-{origen.codigo}.pdf", ContentFile(generar(origen)), save=True,
    )
    return origen.informe_compra


def visualizar_informe_tecnico(origen):
    from django.http import FileResponse
    archivo = asegurar_informe_tecnico(origen)
    return FileResponse(archivo.open("rb"), content_type="application/pdf", filename=f"informe-{origen.codigo}.pdf")
