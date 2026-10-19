<template>
  <main class="login-page">
    <section class="login-card">

      <!-- ==========================
           IDENTIDAD
      =========================== -->
      <div class="brand">
        <div class="logo-placeholder">
          <img src="/img/emi.jpg" alt="EMI" class="logo-img">
        </div>

        <div class="brand-text">
          <h1>SIA</h1>

          <p>
            Escuela Militar de Ingeniería
          </p>

          <span>
            Unidad Académica Santa Cruz
          </span>
        </div>
      </div>


      <div class="divider"></div>


      <!-- ==========================
           ENCABEZADO
      =========================== -->
      <div class="login-header">

        <h2>
          Iniciar sesión
        </h2>

        <p>
          Ingrese sus credenciales institucionales
          para acceder al sistema.
        </p>

      </div>


      <!-- ==========================
           FORMULARIO
      =========================== -->
      <form @submit.prevent="iniciarSesion">

        <!-- CORREO -->
        <div class="form-group">

          <label for="email">
            Correo institucional
          </label>

          <input
            id="email"
            v-model="email"
            type="email"
            placeholder="usuario@emi.edu.bo"
            autocomplete="email"
            required
            :disabled="cargando"
          />

        </div>


        <!-- CONTRASEÑA -->
        <div class="form-group">

          <label for="password">
            Contraseña
          </label>

          <div class="password-wrapper">

            <input
              id="password"
              v-model="password"
              :type="mostrarPassword ? 'text' : 'password'"
              placeholder="Ingrese su contraseña"
              autocomplete="current-password"
              required
              :disabled="cargando"
            />


            <button
              type="button"
              class="show-password"
              @click="mostrarPassword = !mostrarPassword"
              :disabled="cargando"
            >
              {{
                mostrarPassword
                  ? 'Ocultar'
                  : 'Ver'
              }}
            </button>

          </div>

        </div>


        <!-- ==========================
             OPCIONES
        =========================== -->
        <div class="login-options">

          <label class="remember">

            <input
              v-model="recordarme"
              type="checkbox"
              :disabled="cargando"
            />

            <span>
              Recordarme
            </span>

          </label>


          <!-- RECUPERAR CONTRASEÑA -->
          <button
            type="button"
            class="forgot-link"
            @click="irRecuperacion"
            :disabled="cargando"
          >
            ¿Olvidó su contraseña?
          </button>

        </div>


        <!-- ==========================
             MENSAJE
        =========================== -->
        <p
          v-if="mensaje"
          class="message"
        >
          {{ mensaje }}
        </p>


        <!-- ==========================
             BOTÓN LOGIN
        =========================== -->
        <button
          class="login-button"
          type="submit"
          :disabled="cargando"
        >
          {{
            cargando
              ? 'Ingresando...'
              : 'Iniciar sesión'
          }}
        </button>

      </form>


      <!-- ==========================
           FOOTER
      =========================== -->
      <footer>

        <p>
          Sistema Integrado de Atención
        </p>

        <span>
          SIA · EMI Santa Cruz
        </span>

      </footer>

    </section>
  </main>
</template>


<script setup>

import { ref } from 'vue'

import {
  useRouter
} from 'vue-router'


const router = useRouter()


/* ==============================
   DATOS LOGIN
============================== */

const email = ref('')

const password = ref('')

const recordarme = ref(false)

const mostrarPassword = ref(false)


/* ==============================
   ESTADO
============================== */

const mensaje = ref('')

const cargando = ref(false)


/* ==============================
   RECUPERACIÓN DE CONTRASEÑA
============================== */

function irRecuperacion() {

  mensaje.value = ''

  router.push(
    '/recuperar-contrasena'
  )
}


/* ==============================
   LOGIN
============================== */

async function iniciarSesion() {

  mensaje.value = ''


  /* ------------------------------
     VALIDACIÓN
  ------------------------------ */

  if (
    !email.value.trim()
    ||
    !password.value
  ) {

    mensaje.value =
      'Ingrese su correo y contraseña.'

    return
  }


  cargando.value = true


  try {

    const respuesta =
      await fetch(
        '/api/usuarios/login/',
        {

          method: 'POST',

          headers: {
            'Content-Type':
              'application/json',
          },

          body:
            JSON.stringify({

              email:
                email.value
                  .trim()
                  .toLowerCase(),

              password:
                password.value,

            }),

        }
      )


    const datos =
      await respuesta.json()


    /* ------------------------------
       ERROR LOGIN
    ------------------------------ */

    if (!respuesta.ok) {

      mensaje.value =
        datos.mensaje
        ||
        'No se pudo iniciar sesión.'

      return
    }


    /* ------------------------------
       GUARDAR TOKEN
    ------------------------------ */

    localStorage.setItem(
      'sigta_token',
      datos.token
    )


    localStorage.setItem(
      'sigta_usuario',
      JSON.stringify(
        datos.usuario
      )
    )


    /* ------------------------------
       RECORDAR CORREO
    ------------------------------ */

    if (recordarme.value) {

      localStorage.setItem(
        'sigta_recordar_email',
        email.value
          .trim()
          .toLowerCase()
      )

    } else {

      localStorage.removeItem(
        'sigta_recordar_email'
      )
    }


    /* ------------------------------
       CAMBIO OBLIGATORIO
    ------------------------------ */

    if (
      datos.usuario
        .must_change_password
    ) {

      router.push(
        '/cambiar-contrasena'
      )

      return
    }


    /* ------------------------------
       OBTENER ROLES
    ------------------------------ */

    const codigosRoles =
      Array.isArray(
        datos.usuario.roles
      )
        ? datos.usuario.roles.map(
            rol => rol.codigo
          )
        : []


    /* ------------------------------
       ADMIN
    ------------------------------ */

    if (
      codigosRoles.includes(
        'ADMIN'
      )
    ) {

      router.push(
        '/admin/dashboard'
      )

      return
    }

    if (codigosRoles.includes('JEFE_UTIC')) {
      router.push('/jefe-utic/dashboard')
      return
    }

    if (codigosRoles.includes('ESPECIALISTA')) {
      router.push('/especialista/dashboard')
      return
    }

    if (codigosRoles.includes('SERVICIOS_GENERALES')) {
      router.push('/servicios-generales/dashboard')
      return
    }

    if (codigosRoles.includes('AUXILIAR_SERVICIOS_GENERALES')) {
      router.push('/auxiliar-servicios-generales/dashboard')
      return
    }

    if (codigosRoles.includes('TESORERIA')) {
      router.push('/tesoreria/dashboard')
      return
    }

    if (codigosRoles.includes('ENCARGADO_COMPRAS_ALMACEN')) {
      router.push('/almacen/dashboard')
      return
    }

    if (codigosRoles.includes('DAF')) {
      router.push('/daf/dashboard')
      return
    }


    /* ------------------------------
       AGENTE / TÉCNICO
    ------------------------------ */

    if (
      codigosRoles.includes(
        'AGENTE'
      )
    ) {

      router.push(
        '/tecnico/dashboard'
      )

      return
    }


    /* ------------------------------
       SUPERVISOR / APROBADOR
    ------------------------------ */

    if (
      codigosRoles.includes(
        'SUPERVISOR_AREA'
      )
      ||
      codigosRoles.includes(
        'APROBADOR'
      )
    ) {

      router.push(
        '/supervisor/dashboard'
      )

      return
    }


    /* ------------------------------
       SOLICITANTE
    ------------------------------ */

    router.push(
      '/usuario/dashboard'
    )

  } catch (error) {

    console.error(
      'Error login:',
      error
    )


    mensaje.value =
      'No fue posible comunicarse con el servidor.'

  } finally {

    cargando.value = false
  }
}


/* ==============================
   CARGAR CORREO RECORDADO
============================== */

const emailRecordado =
  localStorage.getItem(
    'sigta_recordar_email'
  )


if (emailRecordado) {

  email.value =
    emailRecordado

  recordarme.value =
    true
}

</script>


<style scoped>

/* ==========================
   GENERAL
========================== */

* {
  box-sizing: border-box;
}


.login-page {

  min-height: 100vh;

  width: 100%;

  display: flex;

  align-items: center;

  justify-content: center;

  padding: 20px;

  background: var(--sigta-azul);

  font-family: var(--sigta-fuente);
}


/* ==========================
   TARJETA
========================== */

.login-card {

  width: 100%;

  max-width: 420px;

  background: var(--sigta-blanco);

  border-radius: 16px;

  padding:
    24px
    30px
    20px;

  border-top:
    4px solid var(--sigta-mostaza);

  box-shadow:
    0 20px 50px
    rgba(0, 0, 0, 0.24);
}


/* ==========================
   IDENTIDAD
========================== */

.brand {

  display: flex;

  align-items: center;

  gap: 15px;
}


.logo-placeholder {

  width: 60px;

  height: 60px;

  flex-shrink: 0;

  display: flex;

  align-items: center;

  justify-content: center;

  border-radius: 13px;

  background: var(--sigta-azul);

  border:
    3px solid var(--sigta-mostaza);

  color: var(--sigta-blanco);

  font-size: 19px;

  font-weight: 800;

  letter-spacing: 0.5px;

  overflow: hidden;
}


.logo-img {

  width: 100%;

  height: 100%;

  object-fit: contain;
}


.brand-text {

  min-width: 0;
}


.brand h1 {

  margin: 0;

  color: var(--sigta-azul);

  font-size: 28px;

  line-height: 1;

  font-weight: 800;

  letter-spacing: 1px;
}


.brand p {

  margin:
    5px
    0
    2px;

  color: var(--sigta-azul);

  font-size: 14px;

  font-weight: 700;
}


.brand span {

  display: block;

  color: var(--sigta-texto-suave);

  font-size: 12px;
}


/* ==========================
   DIVISOR
========================== */

.divider {

  height: 3px;

  margin:
    17px
    0;

  border-radius: 10px;

  background: var(--sigta-mostaza);
}


/* ==========================
   ENCABEZADO
========================== */

.login-header h2 {

  margin: 0;

  color: var(--sigta-azul-oscuro);

  font-size: 23px;

  font-weight: 700;
}


.login-header p {

  margin:
    6px
    0
    17px;

  color: var(--sigta-texto-suave);

  font-size: 13px;

  line-height: 1.45;
}


/* ==========================
   CAMPOS
========================== */

.form-group {

  margin-bottom: 14px;
}


.form-group label {

  display: block;

  margin-bottom: 6px;

  color: var(--sigta-azul);

  font-size: 13px;

  font-weight: 700;
}


.form-group input {

  width: 100%;

  height: 44px;

  padding:
    0
    14px;

  border:
    1px solid var(--sigta-borde);

  border-radius: 8px;

  background: var(--sigta-blanco);

  color: var(--sigta-azul);

  font-size: 15px;

  outline: none;

  transition:
    border-color .2s,
    box-shadow .2s;
}


.form-group input::placeholder {

  color: var(--sigta-texto-suave);
}


.form-group input:focus {

  border-color: var(--sigta-texto-suave);

  box-shadow:
    0 0 0 3px
    rgba(11, 87, 149, .12);
}


.form-group input:disabled {

  background: var(--sigta-azul-tenue);

  cursor: not-allowed;
}


/* ==========================
   PASSWORD
========================== */

.password-wrapper {

  position: relative;
}


.password-wrapper input {

  padding-right: 70px;
}


.show-password {

  position: absolute;

  top: 50%;

  right: 12px;

  transform:
    translateY(-50%);

  border: none;

  background: transparent;

  color: var(--sigta-azul);

  font-size: 13px;

  font-weight: 700;

  cursor: pointer;
}


.show-password:hover {

  color: var(--sigta-azul);
}


.show-password:disabled {

  opacity: .55;

  cursor: not-allowed;
}


/* ==========================
   OPCIONES
========================== */

.login-options {

  display: flex;

  align-items: center;

  justify-content: space-between;

  gap: 12px;

  margin:
    2px
    0
    17px;

  font-size: 13px;
}


.remember {

  display: flex;

  align-items: center;

  gap: 7px;

  color: var(--sigta-texto-suave);

  white-space: nowrap;
}


.remember input {

  width: 16px;

  height: 16px;

  accent-color: var(--sigta-azul);
}


/* ==========================
   OLVIDÓ CONTRASEÑA
========================== */

.forgot-link {

  padding: 0;

  border: none;

  background: transparent;

  color: var(--sigta-azul);

  font-family: var(--sigta-fuente);

  font-size: 13px;

  font-weight: 700;

  cursor: pointer;

  text-decoration: none;
}


.forgot-link:hover:not(:disabled) {

  text-decoration: underline;

  color: var(--sigta-azul);
}


.forgot-link:disabled {

  opacity: .55;

  cursor: not-allowed;
}


/* ==========================
   MENSAJE
========================== */

.message {

  margin:
    0
    0
    13px;

  padding:
    9px
    11px;

  border-radius: 7px;

  background: var(--sigta-azul-tenue);

  color: var(--sigta-azul);

  font-size: 12px;

  line-height: 1.4;
}


/* ==========================
   BOTÓN LOGIN
========================== */

.login-button {

  width: 100%;

  height: 45px;

  border: none;

  border-radius: 8px;

  background: var(--sigta-azul);

  color: var(--sigta-blanco);

  font-size: 15px;

  font-weight: 700;

  cursor: pointer;

  transition:
    background .2s,
    transform .1s,
    box-shadow .2s;
}


.login-button:hover:not(:disabled) {

  background: var(--sigta-azul);

  box-shadow:
    0 8px 18px
    rgba(7, 53, 99, .2);
}


.login-button:active:not(:disabled) {

  transform: scale(.99);
}


.login-button:disabled {

  opacity: .7;

  cursor: not-allowed;
}


/* ==========================
   FOOTER
========================== */

footer {

  margin-top: 15px;

  text-align: center;

  color: var(--sigta-texto-suave);
}


footer p {

  margin:
    0
    0
    3px;

  font-size: 10.5px;
}


footer span {

  font-size: 10px;

  font-weight: 600;
}


/* ==========================
   TABLET
========================== */

@media (
  max-width: 768px
) {

  .login-page {

    padding: 18px;
  }


  .login-card {

    max-width: 410px;

    padding:
      23px
      27px
      19px;
  }

}


/* ==========================
   CELULAR
========================== */

@media (
  max-width: 520px
) {

  .login-page {

    align-items: flex-start;

    padding:
      15px
      12px;
  }


  .login-card {

    max-width: 100%;

    padding:
      21px
      19px
      18px;

    border-radius: 13px;
  }


  .brand {

    gap: 11px;
  }


  .logo-placeholder {

    width: 52px;

    height: 52px;

    border-radius: 11px;

    font-size: 16px;
  }


  .brand h1 {

    font-size: 24px;
  }


  .brand p {

    font-size: 12.5px;
  }


  .brand span {

    font-size: 10.5px;
  }


  .divider {

    margin:
      14px
      0;
  }


  .login-header h2 {

    font-size: 21px;
  }


  .login-header p {

    margin-bottom: 14px;

    font-size: 12.5px;
  }


  .form-group {

    margin-bottom: 12px;
  }


  .form-group input {

    height: 44px;

    font-size: 16px;
  }


  .login-options {

    flex-direction: column;

    align-items: flex-start;

    gap: 9px;

    margin-bottom: 15px;
  }


  .forgot-link {

    font-size: 13px;
  }


  .login-button {

    height: 45px;
  }


  footer {

    margin-top: 13px;
  }

}


/* ==========================
   CELULAR MUY PEQUEÑO
========================== */

@media (
  max-width: 350px
) {

  .login-page {

    padding: 8px;
  }


  .login-card {

    padding:
      18px
      15px;
  }


  .brand p {

    font-size: 11.5px;
  }


  .brand span {

    display: none;
  }


  .login-header h2 {

    font-size: 20px;
  }

}


</style>
