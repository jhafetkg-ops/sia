from decimal import Decimal
from types import SimpleNamespace

from django.test import SimpleTestCase, override_settings
from rest_framework.exceptions import ValidationError

from .serializers import SolicitudCompraSerializer


class LimiteCajaChicaTests(SimpleTestCase):
    def validar(self, monto):
        serializer = SolicitudCompraSerializer()
        return serializer.validate({
            "monto_estimado": Decimal(monto),
            "informe": SimpleNamespace(name="informe.pdf"),
            "poa": SimpleNamespace(name="poa.pdf"),
            "proforma": SimpleNamespace(name="proforma.pdf"),
        })

    @override_settings(SIA_LIMITE_CAJA_CHICA=Decimal("1000"))
    def test_acepta_montos_inferiores_e_iguales_al_limite(self):
        for monto in ("999", "1000"):
            with self.subTest(monto=monto):
                self.assertEqual(self.validar(monto)["monto_estimado"], Decimal(monto))

    @override_settings(SIA_LIMITE_CAJA_CHICA=Decimal("1000"))
    def test_rechaza_monto_superior(self):
        with self.assertRaises(ValidationError) as error:
            self.validar("1001")
        self.assertIn("monto_estimado", error.exception.detail)

    @override_settings(SIA_LIMITE_CAJA_CHICA=Decimal("800"))
    def test_respeta_limite_configurable(self):
        with self.assertRaises(ValidationError) as error:
            self.validar("900")
        self.assertIn("800.00", str(error.exception.detail))

    @override_settings(SIA_LIMITE_CAJA_CHICA=Decimal("1000"))
    def test_rechaza_actualizacion_del_monto(self):
        serializer = SolicitudCompraSerializer(
            instance=SimpleNamespace(monto_estimado=Decimal("999")), partial=True,
        )
        with self.assertRaises(ValidationError):
            serializer.validate({"monto_estimado": Decimal("1001")})
