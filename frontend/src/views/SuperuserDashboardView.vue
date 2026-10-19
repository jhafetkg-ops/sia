<template>

  <div class="layout">

    <SuperuserMenu />

    <main class="main">

      <header class="page-header">

        <div>
          <h1>
            Panel de Superusuario
          </h1>

          <p>
            Administración técnica del sistema: usuarios, roles y
            permisos, auditoría y configuración de SIA.
          </p>
        </div>

      
        <UsuarioHeader />
      </header>


      <section class="quick-grid">

        <button
          class="quick-card"
          type="button"
          @click="router.push('/superuser/usuarios')"
        >
          <IconoSigta class="quick-icon" nombre="usuarios" :tamano="22" />

          <div>
            <strong>
              Usuarios
            </strong>

            <span>
              Crear, modificar, activar e inactivar
              cuentas institucionales.
            </span>
          </div>
        </button>


        <button
          class="quick-card"
          type="button"
          @click="router.push('/superuser/roles-permisos')"
        >
          <IconoSigta class="quick-icon" nombre="roles" :tamano="22" />

          <div>
            <strong>
              Roles y permisos
            </strong>

            <span>
              Definir qué puede visualizar y ejecutar
              cada rol dentro de SIA.
            </span>
          </div>
        </button>


        <button
          class="quick-card"
          type="button"
          @click="router.push('/superuser/auditoria')"
        >
          <IconoSigta class="quick-icon" nombre="auditoria" :tamano="22" />

          <div>
            <strong>
              Auditoría
            </strong>

            <span>
              Consultar accesos, acciones y trazabilidad
              de los procesos del sistema.
            </span>
          </div>
        </button>


        <button
          class="quick-card"
          type="button"
          @click="router.push('/superuser/smtp')"
        >
          <IconoSigta class="quick-icon" nombre="correo" :tamano="22" />

          <div>
            <strong>
              Correo SMTP
            </strong>

            <span>
              Configurar el canal de correo para
              recuperación y notificaciones.
            </span>
          </div>
        </button>


        <button
          class="quick-card"
          type="button"
          @click="router.push('/superuser/preferencias')"
        >
          <IconoSigta class="quick-icon" nombre="configuracion" :tamano="22" />

          <div>
            <strong>
              Preferencias
            </strong>

            <span>
              Configurar parámetros generales del
              funcionamiento de SIA.
            </span>
          </div>
        </button>

      </section>

    </main>

  </div>

</template>


<script setup>
import UsuarioHeader from '../components/UsuarioHeader.vue'
import IconoSigta from '../components/IconoSigta.vue'

import {
  useRouter
} from 'vue-router'

import SuperuserMenu
  from '../components/SuperuserMenu.vue'


const router =
  useRouter()

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


.main {
  flex: 1;
  min-width: 0;
  padding: 27px;
}


/* =========================================================
   HEADER
========================================================= */

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 22px;
}


.page-header h1 {
  margin: 0;
  color: var(--sigta-texto);
  font-size: 33px;
}


.page-header p {
  margin: 5px 0 0;
  color: var(--sigta-texto-suave);
  font-size: 17px;
}


/* =========================================================
   ACCESOS RÁPIDOS
========================================================= */

.quick-grid {
  display: grid;
  grid-template-columns: repeat(2,1fr);
  gap: 18px;
  padding: 6px;
}


.quick-card {
  position: relative;
  z-index: 1;
  min-height: 105px;
  display: flex;
  align-items: center;
  gap: 15px;
  padding: 19px;
  border: 1px solid var(--sigta-borde);
  border-radius: 9px;
  background: var(--sigta-azul-tenue);
  text-align: left;
  cursor: pointer;
  transform-origin: center;
  transition:
    border-color .25s ease,
    background .25s ease,
    box-shadow .25s ease,
    transform .32s cubic-bezier(.34, 1.55, .5, 1);
}


.quick-card:hover {
  z-index: 5;
  border-color: #FF9F00;
  background: #FFB300;
  box-shadow: 0 22px 48px rgba(255, 159, 0, .6);
  transform: scale(1.12);
}


.quick-card:hover strong,
.quick-card:hover span {
  color: var(--sigta-azul);
}


.quick-card:active {
  transform: scale(1.05);
}


.quick-icon {
  width: 46px;
  height: 46px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: var(--sigta-azul);
  color: var(--sigta-mostaza);
  font-size: 22px;
  box-shadow: 0 4px 10px rgba(7,35,60,.16);
  transition:
    background .2s,
    color .2s,
    transform .2s,
    box-shadow .2s;
}


.quick-card:hover .quick-icon {
  background: var(--sigta-blanco, #fff);
  color: var(--sigta-azul);
  transform: scale(1.1);
  box-shadow: 0 8px 18px rgba(7,35,60,.22);
}


.quick-card strong {
  display: block;
  color: var(--sigta-texto);
  font-size: 18px;
}


.quick-card span {
  display: block;
  margin-top: 4px;
  color: var(--sigta-texto-suave);
  font-size: 15px;
  line-height: 1.5;
}


/* =========================================================
   RESPONSIVE
========================================================= */

@media (max-width: 900px) {

  .quick-grid {
    grid-template-columns: 1fr;
  }
}


@media (max-width: 760px) {

  .layout {
    display: block;
  }

  .main {
    padding: 16px;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }
}

</style>
