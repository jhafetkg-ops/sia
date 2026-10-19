<template>

  <div class="layout">

    <!-- ================================================
         MENÚ ÚNICO DEL ADMINISTRADOR
    ================================================= -->

    <SuperuserMenu />


    <!-- ================================================
         CONTENIDO
    ================================================= -->

    <main class="content">

      <button
        type="button"
        class="back-link"
        @click="router.push('/superuser/dashboard')"
      >
        ← Volver al panel
      </button>

      <!-- ==============================================
           ENCABEZADO
      =============================================== -->

      <header class="topbar">

        <div>

          <span class="page-kicker">
            Configuración de correo
          </span>

          <h1>
            Correo SMTP
          </h1>

          <p>
            Administre el canal institucional utilizado por SIA
            para recuperación y notificaciones.
          </p>

        </div>


        <span
          :class="[
            'status',
            form.activo
              ? 'enabled'
              : 'disabled'
          ]"
        >
          {{
            form.activo
              ? '● SMTP activo'
              : '● SMTP inactivo'
          }}
        </span>

      
        <UsuarioHeader @actualizar="cargarConfiguracion" />
      </header>


      <!-- ==============================================
           INFORMACIÓN
      =============================================== -->

      <section class="info-grid">

        <article class="info-card" style="border-top-color:#3E7BD6">

          <span class="ic-head" aria-hidden="true">
            <span class="ic-num" style="background:#3E7BD6">01</span>
            <span class="ic-icon" style="background:#3E7BD626;color:#3E7BD6">
              <IconoSigta nombre="llave" :tamano="18" />
            </span>
          </span>

          <div>

            <strong>
              Recuperación de contraseña
            </strong>

            <p>
              Envío del código de recuperación
              solicitado por el usuario.
            </p>

          </div>

        </article>


        <article class="info-card" style="border-top-color:#7B6FD9">

          <span class="ic-head" aria-hidden="true">
            <span class="ic-num" style="background:#7B6FD9">02</span>
            <span class="ic-icon" style="background:#7B6FD926;color:#7B6FD9">
              <IconoSigta nombre="notificaciones" :tamano="18" />
            </span>
          </span>

          <div>

            <strong>
              Notificaciones de requerimientos
            </strong>

            <p>
              Avisos relacionados con cambios de estado,
              asignaciones y cierre de procesos.
            </p>

          </div>

        </article>


        <article class="info-card" style="border-top-color:#1FA396">

          <span class="ic-head" aria-hidden="true">
            <span class="ic-num" style="background:#1FA396">03</span>
            <span class="ic-icon" style="background:#1FA39626;color:#1FA396">
              <IconoSigta nombre="correo" :tamano="18" />
            </span>
          </span>

          <div>

            <strong>
              Canal secundario
            </strong>

            <p>
              SIA mantiene autenticación local;
              el correo se utiliza únicamente
              como medio de notificación.
            </p>

          </div>

        </article>

      </section>


      <!-- ==============================================
           CONFIGURACIÓN
      =============================================== -->

      <section class="configuration">

        <div class="configuration-header">

          <div>

            <span class="section-label">
              CONFIGURACIÓN DE CORREO
            </span>

            <h2>
              Configuración SMTP
            </h2>

            <p>
              Datos del servidor de correo autorizado
              para enviar mensajes desde SIA.
            </p>

          </div>


          <div class="provider">
            OUTLOOK / MICROSOFT
          </div>

        </div>


        <!-- ============================================
             FORMULARIO
        ============================================= -->

        <form
          @submit.prevent="guardar"
        >

          <div class="smtp-layout">

            <section class="smtp-column general-column">
              <div class="column-heading">
                <span class="section-label">CONFIGURACIÓN GENERAL</span>
              </div>

              <div class="field">
                <label>Nombre de configuración</label>
                <input
                  v-model="form.nombre"
                  type="text"
                  placeholder="Correo institucional EMI"
                />
              </div>

              <div class="field">
                <label>Cuenta de envío</label>
                <input
                  v-model="form.usuario"
                  type="email"
                  placeholder="sia@emi.edu.bo"
                />
                <small>Cuenta autorizada para enviar mensajes desde SIA.</small>
              </div>

              <div class="field">
                <label>Remitente visible</label>
                <input
                  v-model="form.remitente"
                  type="email"
                  placeholder="sigta@emi.edu.bo"
                />
                <small>Dirección que visualizará el destinatario.</small>
              </div>
            </section>

            <section class="smtp-column server-column">
              <div class="column-heading">
                <span class="section-label">SERVIDOR Y SEGURIDAD</span>
              </div>

              <div class="server-fields">
                <div class="field">
                  <label>Servidor SMTP</label>
                  <input
                    v-model="form.host"
                    type="text"
                    placeholder="smtp-mail.outlook.com"
                  />
                  <small>Servidor proporcionado por el proveedor de correo.</small>
                </div>

                <div class="field">
                  <label>Puerto</label>
                  <input
                    v-model.number="form.puerto"
                    type="number"
                    min="1"
                    placeholder="587"
                  />
                  <small>Normalmente 587.</small>
                </div>
              </div>

              <section class="security-section">
                <div class="security-header">
                  <span class="section-label">SEGURIDAD DE CONEXIÓN</span>
                </div>

                <label class="switch-row">
                  <input v-model="form.usar_tls" type="checkbox" />
                  <div>
                    <strong>STARTTLS / TLS</strong>
                    <span>Proteger la conexión con el servidor SMTP.</span>
                  </div>
                </label>

                <label class="switch-row">
                  <input v-model="form.activo" type="checkbox" />
                  <div>
                    <strong>Habilitar notificaciones</strong>
                    <span>Permitir que SIA utilice este canal de correo.</span>
                  </div>
                </label>
              </section>
            </section>

          </div>


          <!-- ==========================================
               MENSAJE
          =========================================== -->

          <div
            v-if="mensaje"
            class="success"
          >
            {{ mensaje }}
          </div>


          <div
            v-if="error"
            class="error"
          >
            {{ error }}
          </div>


          <!-- ==========================================
               BOTONES
          =========================================== -->

          <div class="footer-actions">

            <button
              type="button"
              class="secondary"
              @click="
                router.push('/superuser/dashboard')
              "
            >
              Cancelar
            </button>


            <button
              type="submit"
              class="primary"
              :disabled="guardando"
            >
              {{
                guardando
                  ? 'Guardando...'
                  : 'Guardar configuración'
              }}
            </button>

          </div>

        </form>

      </section>

    </main>

    <TarjetaGuardado :visible="mostrarGuardadoOk" :texto="textoGuardado" @cerrar="ocultarGuardado" />

  </div>

</template>


<script setup>
import UsuarioHeader from '../components/UsuarioHeader.vue'

import {
  onMounted,
  reactive,
  ref
} from 'vue'

import {
  useRouter
} from 'vue-router'

import SuperuserMenu
  from '../components/SuperuserMenu.vue'

import IconoSigta
  from '../components/IconoSigta.vue'

import TarjetaGuardado
  from '../components/TarjetaGuardado.vue'

import { usarGuardado }
  from '../utils/guardado.js'


const router =
  useRouter()

const {
  mostrar: mostrarGuardadoOk,
  texto: textoGuardado,
  animar: animarGuardado,
  ocultar: ocultarGuardado,
} = usarGuardado()


// ==========================================================
// ESTADO
// ==========================================================

const mensaje =
  ref('')

const error =
  ref('')

const guardando =
  ref(false)


// ==========================================================
// FORMULARIO
// ==========================================================

const form =
  reactive({

    nombre:
      'Correo institucional',

    host:
      '',

    puerto:
      587,

    usuario:
      '',

    remitente:
      '',

    usar_tls:
      true,

    activo:
      false,
  })


// ==========================================================
// TOKEN
// ==========================================================

function token() {

  return localStorage.getItem(
    'sigta_token'
  )
}


// ==========================================================
// HEADERS
// ==========================================================

function headersJson() {

  return {

    'Content-Type':
      'application/json',

    Accept:
      'application/json',

    Authorization:
      `Token ${token()}`,
  }
}


// ==========================================================
// INICIO
// ==========================================================

onMounted(
  async () => {

    if (!token()) {

      router.push(
        '/login'
      )

      return
    }


    await cargarConfiguracion()
  }
)


// ==========================================================
// CARGAR CONFIGURACIÓN
// ==========================================================

async function cargarConfiguracion() {

  error.value =
    ''


  try {

    const respuesta =
      await fetch(
        '/api/auditoria/smtp/',
        {
          headers:
            headersJson()
        }
      )


    if (
      respuesta.status === 401
      ||
      respuesta.status === 403
    ) {

      cerrarSesion()

      return
    }


    if (!respuesta.ok) {

      error.value =
        'No fue posible cargar la configuración SMTP.'

      return
    }


    const datos =
      await respuesta.json()


    Object.assign(
      form,
      datos
    )


  } catch (err) {

    console.error(
      'Error cargando SMTP:',
      err
    )


    error.value =
      'No fue posible conectar con el servicio SMTP.'
  }
}


// ==========================================================
// GUARDAR
// ==========================================================

async function guardar() {

  mensaje.value =
    ''

  error.value =
    ''

  guardando.value =
    true


  try {

    const respuesta =
      await fetch(
        '/api/auditoria/smtp/',
        {
          method:
            'PUT',

          headers:
            headersJson(),

          body:
            JSON.stringify(
              form
            ),
        }
      )


    if (
      respuesta.status === 401
      ||
      respuesta.status === 403
    ) {

      cerrarSesion()

      return
    }


    let datos = {}


    try {

      datos =
        await respuesta.json()

    } catch {

      datos = {}
    }


    if (!respuesta.ok) {

      error.value =
        datos?.detalle
        ||
        datos?.detail
        ||
        'No fue posible guardar la configuración.'

      return
    }


    Object.assign(
      form,
      datos
    )


    guardando.value = false

    await animarGuardado('Configuración SMTP guardada')


  } catch (err) {

    console.error(
      'Error guardando SMTP:',
      err
    )


    error.value =
      'No fue posible guardar la configuración SMTP.'


  } finally {

    guardando.value =
      false

    mostrarGuardadoOk.value =
      false
  }
}


// ==========================================================
// CERRAR SESIÓN
// ==========================================================

function cerrarSesion() {

  localStorage.removeItem(
    'sigta_token'
  )

  localStorage.removeItem(
    'sigta_usuario'
  )

  router.push(
    '/login'
  )
}

</script>


<style scoped>

* {
  box-sizing: border-box;
}


/* =========================================================
   LAYOUT
========================================================= */

.layout {
  min-height: 100vh;
  display: flex;
  background: var(--sigta-azul-tenue);
  font-family: var(--sigta-fuente);
}


.content {
  flex: 1;
  min-width: 0;
  padding: 27px;
  overflow-x: hidden;
}

.back-link {
  margin: 0 0 9px;
  padding: 0;
  border: 0;
  background: transparent;
  color: var(--sigta-azul);
  font-family: inherit;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
}

.back-link:hover {
  text-decoration: underline;
}


/* =========================================================
   ENCABEZADO
========================================================= */

.topbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 20px;
  margin-bottom: 15px;
}

.page-kicker {
  display: block;
  margin-bottom: 4px;
  color: var(--sigta-texto-suave);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: .7px;
  text-transform: uppercase;
}


.breadcrumb {
  display: block;
  margin-bottom: 6px;
  color: var(--sigta-texto-suave);
  font-size: 15px;
}


.topbar h1 {
  margin: 0;
  color: var(--sigta-texto);
  font-size: 27px;
}


.topbar p {
  margin: 5px 0 0;
  color: var(--sigta-texto-suave);
  font-size: 17px;
  line-height: 1.45;
}


/* =========================================================
   ESTADO
========================================================= */

.status {
  padding: 7px 11px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 900;
  letter-spacing: .3px;
}


.status.enabled {
  background: var(--sigta-exito-fondo);
  color: var(--sigta-exito);
}


.status.disabled {
  background: var(--sigta-azul-tenue);
  color: var(--sigta-texto-suave);
}


/* =========================================================
   TARJETAS DE INFORMACIÓN
========================================================= */

.info-grid {
  display: grid;
  grid-template-columns: repeat(3,1fr);
  gap: 13px;
  margin-bottom: 17px;
}


.info-card {
  min-height: 82px;
  display: flex;
  align-items: flex-start;
  gap: 13px;
  padding: 14px 15px;
  border-top: 4px solid var(--sigta-mostaza);
  border-radius: 11px;
  background: white;
  box-shadow: 0 3px 12px rgba(0,0,0,.04);
  transition: box-shadow .2s ease, transform .2s ease;
}


.info-card:hover {
  box-shadow: 0 8px 22px rgba(0,0,0,.09);
  transform: translateY(-1px);
}


.ic-head {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 6px;
}


.ic-num {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  color: #fff;
  font-size: 13px;
  font-weight: 900;
}


.ic-icon {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
}


.info-card strong {
  color: var(--sigta-azul);
  font-size: 16px;
}


.info-card p {
  margin: 3px 0 0;
  color: var(--sigta-texto-suave);
  font-size: 14px;
  line-height: 1.35;
}


/* =========================================================
   CONFIGURACIÓN
========================================================= */

.configuration {
  padding: 18px 20px;
  border-top: 4px solid var(--sigta-mostaza);
  border-radius: 9px;
  background: white;
  box-shadow: 0 4px 14px rgba(0,0,0,.04);
}


.configuration-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  padding-bottom: 15px;
  border-bottom: 1px solid var(--sigta-azul-tenue);
}


.section-label {
  display: block;
  margin-bottom: 4px;
  color: var(--sigta-azul);
  font-size: 13px;
  font-weight: 900;
  letter-spacing: .8px;
}


.configuration-header h2 {
  margin: 0;
  color: var(--sigta-texto);
  font-size: 17px;
}


.configuration-header p {
  margin: 5px 0 0;
  color: var(--sigta-texto-suave);
  font-size: 15px;
}


.provider {
  flex-shrink: 0;
  padding: 6px 9px;
  border-radius: 5px;
  background: var(--sigta-azul-tenue);
  color: var(--sigta-azul);
  font-size: 14px;
  font-weight: 800;
}


/* =========================================================
   FORMULARIO
========================================================= */

.smtp-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
  gap: 24px;
  width: 100%;
  margin-top: 18px;
}

.smtp-column {
  min-width: 0;
  padding: 17px;
  border: 1px solid var(--sigta-borde);
  border-radius: 8px;
  background: white;
}

.server-column {
  background: var(--sigta-azul-tenue);
}

.column-heading {
  margin-bottom: 13px;
  padding-bottom: 9px;
  border-bottom: 1px solid var(--sigta-borde);
}

.column-heading .section-label {
  margin: 0;
}

.general-column .field + .field {
  margin-top: 13px;
}

.server-fields {
  display: grid;
  grid-template-columns: minmax(0, 7fr) minmax(100px, 3fr);
  gap: 13px;
}


.field {
  display: flex;
  flex-direction: column;
  gap: 5px;
}


.field label {
  color: var(--sigta-azul);
  font-size: 15px;
  font-weight: 800;
}


.field input {
  width: 100%;
  height: 40px;
  padding: 0 11px;
  border: 1px solid var(--sigta-borde);
  border-radius: 6px;
  background: white;
  color: var(--sigta-azul);
  font-family: inherit;
  font-size: 15px;
  outline: none;
}


.field input:focus {
  border-color: var(--sigta-texto-suave);
  box-shadow: 0 0 0 3px rgba(11,87,149,.08);
}


.field small {
  color: var(--sigta-texto-suave);
  font-size: 13px;
}


/* =========================================================
   SEGURIDAD
========================================================= */

.security-section {
  width: 100%;
  margin-top: 17px;
  padding: 13px;
  border: 1px solid var(--sigta-borde);
  border-radius: 8px;
  background: white;
}

.security-header {
  margin-bottom: 4px;
}


.switch-row {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 10px 0;
  border-top: 1px solid var(--sigta-borde);
  cursor: pointer;
}


.switch-row input {
  width: 17px;
  height: 17px;
  flex-shrink: 0;
}


.switch-row strong,
.switch-row span {
  display: block;
}


.switch-row strong {
  color: var(--sigta-azul);
  font-size: 15px;
}


.switch-row span {
  margin-top: 3px;
  color: var(--sigta-texto-suave);
  font-size: 13px;
}


/* =========================================================
   MENSAJES
========================================================= */

.success,
.error {
  width: 100%;
  margin-top: 14px;
  padding: 10px 12px;
  border-radius: 6px;
  font-size: 14px;
}


.success {
  background: var(--sigta-exito-fondo);
  color: var(--sigta-exito);
}


.error {
  background: var(--sigta-error-fondo);
  color: var(--sigta-error);
}


/* =========================================================
   ACCIONES
========================================================= */

.footer-actions {
  width: 100%;
  display: flex;
  justify-content: flex-end;
  gap: 9px;
  margin-top: 18px;
}


.footer-actions button {
  min-height: 38px;
  padding: 0 15px;
  border-radius: 6px;
  font-family: inherit;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
}


.secondary {
  border: 1px solid var(--sigta-borde);
  background: white;
  color: var(--sigta-texto-suave);
}


.primary {
  border: none;
  background: var(--sigta-azul);
  color: white;
}


.primary:disabled {
  opacity: .6;
  cursor: not-allowed;
}


/* =========================================================
   RESPONSIVE
========================================================= */

@media (max-width: 900px) {

  .info-grid {
    grid-template-columns: 1fr;
  }


  .smtp-layout {
    grid-template-columns: 1fr;
  }


  .server-fields {
    grid-template-columns: minmax(0, 7fr) minmax(90px, 3fr);
  }
}


@media (max-width: 760px) {

  .layout {
    display: block;
  }


  .content {
    padding: 16px;
  }


  .topbar {
    align-items: flex-start;
    flex-direction: column;
  }


  .configuration-header {
    flex-direction: column;
  }


  .server-fields {
    grid-template-columns: 1fr;
  }
}

</style>
