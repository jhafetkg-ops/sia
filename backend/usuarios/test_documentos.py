from django.test import SimpleTestCase
from rest_framework.exceptions import ValidationError
from .documentos import validar_firma


class ValidacionFirmaTests(SimpleTestCase):
    def test_rechaza_datos_ajenos_a_coordenadas(self):
        for valor in (None, [], '<script>', [[[float('nan'), 10], [20, 20]]], [[[10, 10], [601, 20]]], [[[True, 10], [20, 20]]], [[[10, 10], [10, 10]]]):
            with self.subTest(valor=repr(valor)), self.assertRaises(ValidationError):
                validar_firma(valor)

    def test_firma_multipart_normaliza_coordenadas(self):
        self.assertEqual(validar_firma('[[[10.12345,20],[40,60]]]'), [[[10.12, 20], [40, 60]]])
