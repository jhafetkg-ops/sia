from io import StringIO
from decimal import Decimal
from django.core.management import call_command
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APITestCase
from usuarios.models import Area, Rol, Usuario, UsuarioRol, DocumentoProceso
from .models import SolicitudCompra, ReciboTesoreria


class ReciboTesoreriaTests(APITestCase):
    def setUp(self):
        call_command('cargar_permisos_sigta', stdout=StringIO())
        self.usuarios = {}
        for rol in ['SOLICITANTE', 'TESORERIA', 'DAF', 'ENCARGADO_COMPRAS_ALMACEN']:
            usuario = Usuario.objects.create_user(username=rol.lower(), email=f'{rol.lower()}@example.invalid', nombre_completo=f'Nombre Completo {rol}')
            UsuarioRol.objects.create(usuario=usuario, rol=Rol.objects.get(codigo=rol))
            self.usuarios[rol] = usuario
        self.s = SolicitudCompra.objects.create(codigo='CMP-TES-QA', titulo='Compra de repuestos', solicitante=self.usuarios['SOLICITANTE'], area=Area.objects.create(codigo='TESQA', nombre='Área de prueba'), tipo='BIEN', cantidad=1, monto_estimado=Decimal('100.00'), estado='APROBADO_PARA_DESEMBOLSO')
        self.url = f'/api/compras/solicitudes/{self.s.pk}'
        self.datos = {'monto_desembolsado': '100.00', 'responsable_adquisicion': 'María Elena Pérez', 'tipo_desembolso': 'Efectivo'}
        self.client.force_authenticate(self.usuarios['TESORERIA'])

    def generar(self, **cambios):
        return self.client.post(self.url + '/recibos-tesoreria/', {**self.datos, **cambios}, format='json')

    def archivo(self, contenido=None, nombre='firmado.pdf'):
        if contenido is None:
            recibo = ReciboTesoreria.objects.latest('pk')
            with recibo.original.open('rb') as f:
                contenido = f.read()
        return SimpleUploadedFile(nombre, contenido, content_type='application/pdf')

    def confirmar(self, recibo_id, **cambios):
        return self.client.post(self.url + '/desembolsar/', {**self.datos, 'recibo_id': recibo_id, 'recibo_firmado': self.archivo(), **cambios}, format='multipart')

    def test_generar_no_desembolsa_y_conserva_instantanea(self):
        respuesta = self.generar()
        self.assertEqual(respuesta.status_code, 201, respuesta.data)
        self.s.refresh_from_db()
        self.assertEqual(self.s.estado, 'APROBADO_PARA_DESEMBOLSO')
        self.assertIsNone(self.s.monto_desembolsado)
        self.s.titulo = 'Título posterior'
        self.s.save()
        pdf = self.client.get(respuesta.data['original_url'])
        contenido = b''.join(pdf.streaming_content)
        self.assertEqual(pdf.status_code, 200)
        self.assertEqual(pdf['Content-Type'], 'application/pdf')
        self.assertIn(b'Compra de repuestos', contenido)
        self.assertNotIn(b'T\xedtulo posterior', contenido)
        self.assertIn(b'Firma de quien recibe', contenido)
        self.assertIn(b'Firma de quien entrega', contenido)
        self.assertTrue(b'Mar\\355a Elena P\\351rez' in contenido, 'El PDF conserva el nombre completo de quien recibe.')

    def test_nombre_completo_monto_y_metodo_obligatorios(self):
        for cambios in [{'responsable_adquisicion': 'Juan'}, {'responsable_adquisicion': '123 456'}, {'monto_desembolsado': 'NaN'}, {'monto_desembolsado': '0'}, {'monto_desembolsado': '-1'}, {'monto_desembolsado': '100.001'}, {'tipo_desembolso': 'Otro'}]:
            with self.subTest(cambios=cambios):
                self.assertEqual(self.generar(**cambios).status_code, 400)
        self.assertFalse(ReciboTesoreria.objects.exists())

    def test_sin_recibo_o_sin_pdf_firmado_no_transiciona(self):
        self.assertEqual(self.client.post(self.url + '/desembolsar/', self.datos).status_code, 400)
        r = self.generar()
        self.assertEqual(self.client.post(self.url + '/desembolsar/', {**self.datos, 'recibo_id': r.data['id']}).status_code, 400)
        self.s.refresh_from_db()
        self.assertEqual(self.s.estado, 'APROBADO_PARA_DESEMBOLSO')
        self.assertFalse(DocumentoProceso.objects.exists())

    def test_efectivo_archiva_original_y_firmado_y_no_se_repite(self):
        r = self.generar()
        firmado = self.archivo().read()
        self.assertEqual(self.confirmar(r.data['id']).status_code, 200)
        self.s.refresh_from_db()
        self.assertEqual(self.s.estado, 'FONDOS_DESEMBOLSADOS')
        self.assertEqual(self.s.responsable_adquisicion, 'María Elena Pérez')
        with self.s.comprobante_desembolso.open('rb') as f:
            self.assertEqual(f.read(), firmado)
        recibos = self.client.get(self.url + '/recibos-tesoreria/').data
        self.assertIsNotNone(recibos[0]['confirmado_en'])
        for campo in ['original_url', 'firmado_url']:
            pdf = self.client.get(recibos[0][campo])
            self.assertEqual(pdf.status_code, 200)
            self.assertTrue(b''.join(pdf.streaming_content).startswith(b'%PDF-'))
        self.assertEqual(self.confirmar(r.data['id']).status_code, 409)
        self.assertEqual(DocumentoProceso.objects.filter(tipo='Constancia de desembolso').count(), 1)

    def test_qr_exige_pdf_firmado_y_comprobante_separados(self):
        self.datos['tipo_desembolso'] = 'QR'
        r = self.generar()
        self.assertEqual(self.confirmar(r.data['id']).status_code, 400)
        self.assertEqual(self.confirmar(r.data['id'], comprobante_desembolso=self.archivo()).status_code, 200)
        recibo = ReciboTesoreria.objects.get(pk=r.data['id'])
        self.assertTrue(recibo.original and recibo.firmado and recibo.comprobante)
        respaldo = self.client.get(self.url + '/recibos-tesoreria/').data[0]
        self.assertTrue(respaldo['original_url'] and respaldo['firmado_url'] and respaldo['comprobante_url'])
        archivo = self.client.get(respaldo['comprobante_url'])
        self.assertEqual(archivo.status_code, 200)
        self.assertTrue(b''.join(archivo.streaming_content).startswith(b'%PDF-'))

    def test_cambio_de_datos_o_recibo_anterior_no_se_puede_confirmar(self):
        r = self.generar()
        self.assertEqual(self.confirmar(r.data['id'], responsable_adquisicion='Otra Persona').status_code, 409)
        self.assertEqual(self.confirmar(r.data['id'], monto_desembolsado='110.00').status_code, 409)
        self.generar()
        self.assertEqual(self.confirmar(r.data['id']).status_code, 409)
        self.s.refresh_from_db()
        self.assertEqual(self.s.estado, 'APROBADO_PARA_DESEMBOLSO')

    def test_recibo_no_se_confirma_en_otro_expediente(self):
        r = self.generar()
        otro = SolicitudCompra.objects.create(codigo='CMP-TES-OTRO', titulo='Otra compra', solicitante=self.usuarios['SOLICITANTE'], area=self.s.area, tipo='BIEN', cantidad=1, estado='APROBADO_PARA_DESEMBOLSO')
        self.url = f'/api/compras/solicitudes/{otro.pk}'
        self.assertEqual(self.confirmar(r.data['id']).status_code, 404)

    def test_pdf_invalido_no_se_archiva(self):
        r = self.generar()
        self.assertEqual(self.confirmar(r.data['id'], recibo_firmado=self.archivo(b'No es PDF')).status_code, 400)
        self.assertEqual(self.confirmar(r.data['id'], recibo_firmado=self.archivo(b'%PDF-' + b'x' * (10 * 1024 * 1024))).status_code, 400)
        self.assertFalse(ReciboTesoreria.objects.get(pk=r.data['id']).confirmado_en)

    def test_privacidad_y_solo_tesoreria_emite_recibos(self):
        r = self.generar()
        for rol in ['DAF', 'ENCARGADO_COMPRAS_ALMACEN']:
            self.client.force_authenticate(self.usuarios[rol])
            self.assertEqual(self.generar().status_code, 403)
            self.assertEqual(self.client.get(r.data['original_url']).status_code, 403)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.get(r.data['original_url']).status_code, 401)

    def test_historial_usa_fecha_de_desembolso_y_no_cambia_otras_bandejas(self):
        r = self.generar()
        self.confirmar(r.data['id'])
        listado = self.client.get('/api/compras/solicitudes/?tesoreria=1')
        datos = listado.data if isinstance(listado.data, list) else listado.data['results']
        self.assertTrue(datos[0]['tesoreria_fecha'])
        normal = self.client.get(self.url + '/').data
        self.assertNotIn('tesoreria_fecha', normal)

    def test_recibo_no_autorizado_no_se_genera(self):
        self.s.estado = 'VERIFICADO_PENDIENTE_AUTORIZACION'
        self.s.save()
        self.assertEqual(self.generar().status_code, 409)
        self.assertFalse(ReciboTesoreria.objects.exists())
