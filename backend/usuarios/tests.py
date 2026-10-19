from datetime import timedelta

from django.conf import settings
from django.core.management import call_command
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from .models import Rol, Usuario, UsuarioRol, DelegacionAprobacion
from .serializers import UsuarioSerializer


class DelegacionAprobacionTests(APITestCase):
    """Caso de uso 'Delegar aprobación temporal': solo actores
    de aprobación (Director, DAF, Tesorería, Jefe de UTIC)
    pueden delegar, solo mientras la delegación esté vigente,
    y solo el propio delegante (o Admin) puede revocarla."""

    def setUp(self):
        call_command("cargar_permisos_sigta")

        self.rol_director = Rol.objects.get(codigo="DIRECTOR")
        self.rol_solicitante = Rol.objects.get(codigo="SOLICITANTE")

        self.director = Usuario.objects.create_user(
            username="director", email="director@emi.edu.bo",
            nombre_completo="Director", password="Prueba#2026",
        )
        UsuarioRol.objects.create(usuario=self.director, rol=self.rol_director, activo=True)

        self.suplente = Usuario.objects.create_user(
            username="suplente", email="suplente@emi.edu.bo",
            nombre_completo="Suplente", password="Prueba#2026",
        )

        self.solicitante = Usuario.objects.create_user(
            username="solicitante", email="solicitante@emi.edu.bo",
            nombre_completo="Solicitante", password="Prueba#2026",
        )
        UsuarioRol.objects.create(usuario=self.solicitante, rol=self.rol_solicitante, activo=True)

    def test_solo_quien_posee_el_rol_puede_delegarlo(self):
        self.client.force_authenticate(self.suplente)
        ahora = timezone.now()
        r = self.client.post("/api/usuarios/delegaciones/", {
            "delegado": self.suplente.id,
            "rol": self.rol_director.id,
            "vigencia_desde": ahora.isoformat(),
            "vigencia_hasta": (ahora + timedelta(days=2)).isoformat(),
        }, format="json")
        self.assertEqual(r.status_code, 403, r.data)

    def test_no_se_puede_delegar_un_rol_no_delegable(self):
        self.client.force_authenticate(self.solicitante)
        ahora = timezone.now()
        r = self.client.post("/api/usuarios/delegaciones/", {
            "delegado": self.suplente.id,
            "rol": self.rol_solicitante.id,
            "vigencia_desde": ahora.isoformat(),
            "vigencia_hasta": (ahora + timedelta(days=2)).isoformat(),
        }, format="json")
        self.assertEqual(r.status_code, 400, r.data)

    def test_no_se_puede_delegar_por_mas_de_90_dias(self):
        self.client.force_authenticate(self.director)
        ahora = timezone.now()
        r = self.client.post("/api/usuarios/delegaciones/", {
            "delegado": self.suplente.id,
            "rol_codigo": "DIRECTOR",
            "vigencia_desde": ahora.isoformat(),
            "vigencia_hasta": (ahora + timedelta(days=400)).isoformat(),
        }, format="json")
        self.assertEqual(r.status_code, 400, r.data)

    def test_delegado_ejerce_el_rol_solo_durante_la_vigencia(self):
        self.client.force_authenticate(self.director)
        ahora = timezone.now()
        r = self.client.post("/api/usuarios/delegaciones/", {
            "delegado": self.suplente.id,
            "rol": self.rol_director.id,
            "vigencia_desde": ahora.isoformat(),
            "vigencia_hasta": (ahora + timedelta(days=2)).isoformat(),
            "motivo": "Viaje institucional",
        }, format="json")
        self.assertEqual(r.status_code, 201, r.data)
        delegacion_id = r.data["id"]

        # Mientras está vigente, el suplente puede actuar como
        # Director (mi-contexto debe reflejar el rol delegado).
        self.client.force_authenticate(self.suplente)
        r = self.client.get("/api/usuarios/mi-contexto/")
        codigos = [rol["codigo"] for rol in r.data["usuario"]["roles"]]
        self.assertIn("DIRECTOR", codigos)
        delegado_flags = [rol["delegado"] for rol in r.data["usuario"]["roles"] if rol["codigo"] == "DIRECTOR"]
        self.assertTrue(any(delegado_flags))

        # Fuera de vigencia (delegación ya vencida): no hereda el rol.
        delegacion = DelegacionAprobacion.objects.get(pk=delegacion_id)
        delegacion.vigencia_desde = ahora - timedelta(days=5)
        delegacion.vigencia_hasta = ahora - timedelta(days=1)
        delegacion.save(update_fields=["vigencia_desde", "vigencia_hasta"])

        r = self.client.get("/api/usuarios/mi-contexto/")
        codigos = [rol["codigo"] for rol in r.data["usuario"]["roles"]]
        self.assertNotIn("DIRECTOR", codigos)

    def test_solo_el_delegante_puede_revocar(self):
        self.client.force_authenticate(self.director)
        ahora = timezone.now()
        r = self.client.post("/api/usuarios/delegaciones/", {
            "delegado": self.suplente.id,
            "rol": self.rol_director.id,
            "vigencia_desde": ahora.isoformat(),
            "vigencia_hasta": (ahora + timedelta(days=2)).isoformat(),
        }, format="json")
        delegacion_id = r.data["id"]

        self.client.force_authenticate(self.suplente)
        r = self.client.post(f"/api/usuarios/delegaciones/{delegacion_id}/revocar/", {}, format="json")
        self.assertEqual(r.status_code, 403, r.data)

        self.client.force_authenticate(self.director)
        r = self.client.post(f"/api/usuarios/delegaciones/{delegacion_id}/revocar/", {}, format="json")
        self.assertEqual(r.status_code, 200, r.data)
        self.assertFalse(r.data["activo"])


class GestionUsuariosAdminTests(APITestCase):

    def setUp(self):
        call_command("cargar_permisos_sigta")
        self.rol_solicitante = Rol.objects.get(codigo="SOLICITANTE")
        self.admin = Usuario.objects.create_user(
            username="admin-prueba",
            email="admin-prueba@emi.edu.bo",
            nombre_completo="Admin Prueba",
            password="Admin#Prueba2026",
        )
        UsuarioRol.objects.create(
            usuario=self.admin,
            rol=Rol.objects.get(codigo="ADMIN"),
            activo=True,
        )

    def datos_usuario(self):
        return {
            "primer_nombre": "Wendy",
            "segundo_nombre": "Roxana",
            "apellido_paterno": "Caillaví",
            "apellido_materno": "Reyes",
            "nombre_completo": "Wendy Roxana Caillaví Reyes",
            "email": "cualquier-valor@emi.edu.bo",
            "password": "Temporal2026*",
            "rol_id": self.rol_solicitante.id,
        }

    def test_genera_correo_y_password_temporal_con_hash(self):
        serializer = UsuarioSerializer(data=self.datos_usuario())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        usuario = serializer.save()
        respuesta = serializer.data

        self.assertEqual(usuario.email, "wcaillavir@emi.edu.bo")
        self.assertIn("password_temporal", respuesta)
        self.assertEqual(respuesta["password_temporal"], "Temporal2026*")
        self.assertTrue(usuario.check_password(respuesta["password_temporal"]))
        self.assertNotEqual(usuario.password, respuesta["password_temporal"])
        self.assertTrue(usuario.must_change_password)

        usuario_recargado = Usuario.objects.get(pk=usuario.pk)
        self.assertNotIn(
            "password_temporal",
            UsuarioSerializer(usuario_recargado).data,
        )

    def test_el_correo_no_utiliza_el_segundo_nombre(self):
        datos = self.datos_usuario()
        datos["segundo_nombre"] = ""
        serializer = UsuarioSerializer(data=datos)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertEqual(serializer.save().email, "wcaillavir@emi.edu.bo")

    def test_inactivar_y_activar_usuario(self):
        serializer = UsuarioSerializer(data=self.datos_usuario())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        usuario = serializer.save()
        self.client.force_authenticate(self.admin)

        respuesta = self.client.delete(f"/api/usuarios/usuarios/{usuario.id}/")
        self.assertEqual(respuesta.status_code, 200, respuesta.data)
        usuario.refresh_from_db()
        self.assertFalse(usuario.is_active)

        respuesta = self.client.post(f"/api/usuarios/usuarios/{usuario.id}/activar/", {})
        self.assertEqual(respuesta.status_code, 200, respuesta.data)
        usuario.refresh_from_db()
        self.assertTrue(usuario.is_active)

    def test_restablecer_password_invalida_anterior_y_exige_cambio(self):
        serializer = UsuarioSerializer(data=self.datos_usuario())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        usuario = serializer.save()
        self.client.force_authenticate(self.admin)

        respuesta = self.client.post(
            f"/api/usuarios/usuarios/{usuario.id}/restablecer-password/",
            {},
        )

        self.assertEqual(respuesta.status_code, 200, respuesta.data)
        self.assertIn("password_temporal", respuesta.data)
        self.assertEqual(respuesta.data["password_temporal"], "Temporal2026*")

        usuario.refresh_from_db()
        self.assertTrue(usuario.check_password(respuesta.data["password_temporal"]))
        self.assertTrue(usuario.must_change_password)

        usuario_consultado = Usuario.objects.get(pk=usuario.pk)
        listado = UsuarioSerializer(usuario_consultado).data
        self.assertNotIn("password_temporal", listado)

    def test_restablecer_password_no_activa_usuario_inactivo(self):
        serializer = UsuarioSerializer(data=self.datos_usuario())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        usuario = serializer.save()
        usuario.is_active = False
        usuario.save(update_fields=["is_active"])
        self.client.force_authenticate(self.admin)

        respuesta = self.client.post(
            f"/api/usuarios/usuarios/{usuario.id}/restablecer-password/",
            {},
        )

        self.assertEqual(respuesta.status_code, 200, respuesta.data)
        usuario.refresh_from_db()
        self.assertFalse(usuario.is_active)

    def test_usuario_sin_rol_admin_no_puede_restablecer_password(self):
        serializer = UsuarioSerializer(data=self.datos_usuario())
        self.assertTrue(serializer.is_valid(), serializer.errors)
        usuario = serializer.save()
        solicitante = Usuario.objects.create_user(
            username="solicitante-sin-permiso",
            email="sin-permiso@emi.edu.bo",
            nombre_completo="Solicitante Sin Permiso",
            password="Prueba#2026",
        )
        UsuarioRol.objects.create(
            usuario=solicitante,
            rol=self.rol_solicitante,
            activo=True,
        )
        self.client.force_authenticate(solicitante)

        respuesta = self.client.post(
            f"/api/usuarios/usuarios/{usuario.id}/restablecer-password/",
            {},
        )

        self.assertEqual(respuesta.status_code, 403, respuesta.data)


class SeguridadAutenticacionTests(APITestCase):
    """Pentest automatizado del flujo de autenticación: fuerza
    bruta, cuentas inactivas, expiración de sesión y bloqueo
    obligatorio de navegación hasta cambiar la contraseña
    inicial (HU-01 / HU-02)."""

    def setUp(self):
        call_command("cargar_permisos_sigta")
        self.rol_solicitante = Rol.objects.get(codigo="SOLICITANTE")

    def crear_usuario(self, email="prueba@emi.edu.bo", password="Prueba#2026", activo=True, must_change=True):
        usuario = Usuario.objects.create_user(
            username=email.split("@")[0], email=email,
            nombre_completo="Usuario de Prueba", password=password,
            is_active=activo,
        )
        usuario.must_change_password = must_change
        usuario.save(update_fields=["must_change_password"])
        UsuarioRol.objects.create(usuario=usuario, rol=self.rol_solicitante, activo=True)
        return usuario

    # ------------------------------------------------------
    # FUERZA BRUTA
    # ------------------------------------------------------

    def test_bloqueo_por_intentos_fallidos(self):
        usuario = self.crear_usuario(must_change=False)
        cliente = APIClient()

        for _ in range(settings.LOGIN_MAX_INTENTOS_FALLIDOS - 1):
            r = cliente.post("/api/usuarios/login/", {"email": usuario.email, "password": "incorrecta"}, format="json")
            self.assertEqual(r.status_code, 401, r.data)

        # El intento número N dispara el bloqueo temporal.
        r = cliente.post("/api/usuarios/login/", {"email": usuario.email, "password": "incorrecta"}, format="json")
        self.assertEqual(r.status_code, 401, r.data)

        usuario.refresh_from_db()
        self.assertIsNotNone(usuario.locked_until)
        self.assertGreater(usuario.locked_until, timezone.now())

        # Ni siquiera la contraseña correcta funciona mientras
        # dura el bloqueo.
        r = cliente.post("/api/usuarios/login/", {"email": usuario.email, "password": "Prueba#2026"}, format="json")
        self.assertEqual(r.status_code, 403, r.data)

    def test_cuenta_inactiva_no_puede_iniciar_sesion(self):
        usuario = self.crear_usuario(activo=False, must_change=False)
        cliente = APIClient()
        r = cliente.post("/api/usuarios/login/", {"email": usuario.email, "password": "Prueba#2026"}, format="json")
        self.assertEqual(r.status_code, 403, r.data)

    # ------------------------------------------------------
    # SESIÓN / TOKEN
    # ------------------------------------------------------

    def test_token_expirado_es_rechazado_y_eliminado(self):
        usuario = self.crear_usuario(must_change=False)
        token = Token.objects.create(user=usuario)
        Token.objects.filter(pk=token.pk).update(
            created=timezone.now() - timedelta(hours=settings.SESION_TOKEN_HORAS_VALIDEZ + 1)
        )

        cliente = APIClient()
        cliente.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")
        r = cliente.get("/api/usuarios/mi-contexto/")
        self.assertEqual(r.status_code, 401, r.data)
        self.assertFalse(Token.objects.filter(pk=token.pk).exists())

    def test_login_renueva_token_expirado_y_carga_datos_en_primer_ingreso(self):
        usuario = self.crear_usuario(must_change=False)
        anterior = Token.objects.create(user=usuario)
        Token.objects.filter(pk=anterior.pk).update(
            created=timezone.now() - timedelta(hours=settings.SESION_TOKEN_HORAS_VALIDEZ + 1)
        )
        cliente = APIClient()
        respuesta = cliente.post('/api/usuarios/login/', {
            'email': usuario.email, 'password': 'Prueba#2026',
        }, format='json')
        self.assertEqual(respuesta.status_code, 200, respuesta.data)
        self.assertNotEqual(respuesta.data['token'], anterior.key)
        cliente.credentials(HTTP_AUTHORIZATION=f"Token {respuesta.data['token']}")
        self.assertEqual(cliente.get('/api/usuarios/mi-contexto/').status_code, 200)
        self.assertEqual(cliente.get('/api/soporte/tickets/').status_code, 200)

    # ------------------------------------------------------
    # HU-02: CAMBIO OBLIGATORIO DE CONTRASEÑA
    # ------------------------------------------------------

    def test_must_change_password_bloquea_el_resto_de_la_api(self):
        usuario = self.crear_usuario(must_change=True)
        token = Token.objects.create(user=usuario)

        cliente = APIClient()
        cliente.credentials(HTTP_AUTHORIZATION=f"Token {token.key}")

        # Cualquier endpoint que no sea el de cambio de
        # contraseña queda bloqueado por el middleware, sin
        # importar que el token sea válido.
        r = cliente.get("/api/compras/solicitudes/")
        self.assertEqual(r.status_code, 403, r.content)
        self.assertTrue(r.json().get("must_change_password"))

        # mi-contexto y el propio endpoint de cambio siguen
        # accesibles (son los únicos necesarios para salir del
        # estado de "debe cambiar contraseña").
        r = cliente.get("/api/usuarios/mi-contexto/")
        self.assertEqual(r.status_code, 200, r.data)

        r = cliente.post("/api/usuarios/cambiar-password-obligatorio/", {
            "password_actual": "Prueba#2026",
            "nueva_password": "OtraClave#2027",
            "confirmar_password": "OtraClave#2027",
        }, format="json")
        self.assertEqual(r.status_code, 200, r.data)

        usuario.refresh_from_db()
        self.assertFalse(usuario.must_change_password)

        # Ahora sí puede navegar el resto de la API.
        r = cliente.get("/api/compras/solicitudes/")
        self.assertEqual(r.status_code, 200, r.data)

    # ------------------------------------------------------
    # HASH DE CONTRASEÑAS
    # ------------------------------------------------------

    def test_password_se_almacena_con_argon2id(self):
        usuario = self.crear_usuario(must_change=False)
        self.assertTrue(usuario.password.startswith("argon2$argon2id$"))
