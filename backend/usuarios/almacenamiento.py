from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.utils.deconstruct import deconstructible


@deconstructible
class AlmacenamientoPrivado(FileSystemStorage):
    def __init__(self):
        super().__init__(location=getattr(settings, 'SIA_PRIVATE_ROOT', settings.BASE_DIR / 'private'), base_url=None)
