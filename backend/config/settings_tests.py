"""Pruebas con almacenamiento aislado de los expedientes del usuario."""
from .settings import *
import atexit
import tempfile

_archivos_prueba = tempfile.TemporaryDirectory(prefix='sia-tests-')
atexit.register(_archivos_prueba.cleanup)
MEDIA_ROOT = Path(_archivos_prueba.name) / 'media'
SIA_PRIVATE_ROOT = Path(_archivos_prueba.name) / 'private'
