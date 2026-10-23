<template>
  <aside class="sidebar">

    <!-- =====================================================
         MARCA + BOTÓN DESPLEGABLE (móvil)
    ====================================================== -->

    <div class="brand-row">

      <div class="brand">

        <div class="logo">
          <img src="/img/emi.jpg" alt="EMI" class="logo-img">
        </div>

        <div class="brand-text">
          <h2>SIA</h2>

          <span>
            Sistema Integrado de Atención
          </span>
        </div>

      </div>

      <button
        type="button"
        class="menu-toggle"
        :aria-expanded="menuAbierto"
        aria-label="Mostrar opciones del menú"
        @click="menuAbierto = !menuAbierto"
      >
        <span></span>
        <span></span>
        <span></span>
      </button>

    </div>


    <!-- =====================================================
         CONTENIDO DESPLEGABLE
    ====================================================== -->

    <div
      class="sidebar-body"
      :class="{ abierto: menuAbierto }"
    >

    <!-- =====================================================
         TESORERÍA
    ====================================================== -->

    <div class="section-title">
      TESORERÍA
    </div>

    <nav @click="menuAbierto = false">

      <router-link
        to="/tesoreria/dashboard"
        class="menu-item"
      >
        <span class="icon-badge" style="background:#2E9E6B26;color:#2E9E6B"><IconoSigta nombre="compras" :tamano="16" /></span>

        <span>
          Solicitudes
        </span>
      </router-link>

    </nav>


    <!-- =====================================================
         CERRAR SESIÓN
    ====================================================== -->

    <button
      class="logout"
      type="button"
      @click="mostrarLogout = true"
    >
      <IconoSigta nombre="salir" :tamano="18" />
      <span>Cerrar sesión</span>
    </button>

    </div>

    <LogoutModal
      :visible="mostrarLogout"
      @cancelar="mostrarLogout = false"
      @confirmar="confirmarCierreSesion"
    />

  </aside>
</template>


<script setup>

import IconoSigta from './IconoSigta.vue'
import LogoutModal from './LogoutModal.vue'

import {
  ref
} from 'vue'

import {
  useRouter
} from 'vue-router'


const router =
  useRouter()


/* =========================================================
   MENÚ MÓVIL (desplegable)
========================================================= */

const menuAbierto =
  ref(false)


/* =========================================================
   CERRAR SESIÓN
========================================================= */

const mostrarLogout = ref(false)

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

function confirmarCierreSesion() {
  mostrarLogout.value = false
  cerrarSesion()
}

</script>


<style scoped>
/* Distintivo del icono: mismo formato y tamano que el panel de
   Mantenimiento (30x30, radio 8, fondo del color al 15%). */
.icon-badge { flex-shrink: 0; width: 30px; height: 30px; border-radius: 8px; display: flex; align-items: center; justify-content: center; }


* {
  box-sizing: border-box;
}


/* =========================================================
   SIDEBAR
========================================================= */

.sidebar {

  position: sticky;

  top: 0;

  width: var(--sigta-sidebar);
  min-width: var(--sigta-sidebar);

  height: 100vh;

  display: flex;
  flex-direction: column;

  padding:
    20px
    14px;

  overflow-y: auto;
  overflow-x: hidden;

  background: var(--sigta-azul);

  color: var(--sigta-blanco);

  font-family: var(--sigta-fuente);
}


/* Scroll discreto */

.sidebar::-webkit-scrollbar {
  width: 5px;
}

.sidebar::-webkit-scrollbar-thumb {

  border-radius: 10px;

  background:
    rgba(
      255,
      255,
      255,
      .18
    );
}


/* =========================================================
   MARCA
========================================================= */

.brand-row {

  display: flex;
  align-items: center;
  justify-content: space-between;

  padding:
    0
    8px
    20px;

  border-bottom:
    1px solid
    rgba(
      255,
      255,
      255,
      .17
    );
}


.brand {

  display: flex;
  align-items: center;

  gap: 12px;
}


.logo {

  width: 48px;
  height: 48px;

  flex-shrink: 0;

  display: flex;

  align-items: center;
  justify-content: center;

  border-radius: 10px;

  overflow: hidden;

  background: var(--sigta-mostaza);
}


.logo-img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}


.brand-text {
  min-width: 0;
}


.brand h2 {

  margin: 0;

  font-size: 22px;
}


.brand span {

  display: block;

  margin-top: 3px;

  color: var(--sigta-azul-texto-claro);

  font-size: 11px;

  line-height: 1.3;
}


/* =========================================================
   SECCIONES
========================================================= */

.section-title {

  margin:
    17px
    10px
    6px;

  color: var(--sigta-texto-suave);

  font-size: 10px;

  font-weight: 800;

  letter-spacing: 1px;
}


/* =========================================================
   NAVEGACIÓN
========================================================= */

nav {

  display: flex;

  flex-direction: column;

  gap: 3px;
}


.menu-item {

  position: relative;

  min-height: 46px;

  display: flex;

  align-items: center;

  gap: 11px;

  padding:
    0
    11px;

  border-radius: 7px;

  color: var(--sigta-azul-tenue);

  text-decoration: none;

  font-size: 13px;

  transition:
    background .2s,
    color .2s,
    padding .2s;
}


.icon {

  width: 27px;

  flex-shrink: 0;

  display: flex;
  align-items: center;
  justify-content: center;

  font-size: 18px;
  line-height: 1;
}


.menu-item:hover {

  background:
    rgba(
      255,
      255,
      255,
      .08
    );

  color: var(--sigta-blanco);
}


.menu-item.router-link-active {

  padding-left: 8px;

  border-left:
    3px solid var(--sigta-mostaza);

  background:
    rgba(
      255,
      255,
      255,
      .13
    );

  color: var(--sigta-mostaza);

  font-weight: 700;
}


.menu-item.router-link-active
.icon {

  color: var(--sigta-mostaza);
}


/* =========================================================
   CERRAR SESIÓN
========================================================= */

.logout {

  width: 100%;

  min-height: 54px;

  flex-shrink: 0;

  position: sticky;

  bottom: 0;

  margin-top: auto;

  display: flex;

  align-items: center;

  justify-content: center;

  gap: 10px;

  border: none;

  border-radius: 7px;

  background: var(--sigta-mostaza);

  color: var(--sigta-texto);

  font-size: 16px;

  font-weight: 800;

  cursor: pointer;

  transition:
    transform .15s ease,
    box-shadow .15s ease;
}


.logout:hover {

  transform: scale(1.05);

  box-shadow:
    0
    4px
    12px
    rgba(0,0,0,.18);
}


/* Estilo unificado del botón "Cerrar sesión" en todos los
   perfiles (idéntico al de Superuser). */
.sidebar .logout {
  gap: 14px !important;
  border: 1px solid var(--sigta-mostaza) !important;
  border-radius: 8px !important;
  background: transparent !important;
  color: #fff !important;
  box-shadow: inset 0 0 0 1px rgba(255, 199, 44, .35) !important;
  transition:
    transform .3s cubic-bezier(.34, 1.55, .5, 1),
    background .2s ease,
    color .2s ease,
    box-shadow .2s ease !important;
}

.sidebar .logout .icono-sigta {
  color: var(--sigta-mostaza);
  transition: color .2s ease;
}

.sidebar .logout:hover {
  background: #FFB300 !important;
  color: var(--sigta-azul) !important;
  transform: scale(1.09) !important;
  box-shadow: 0 14px 32px rgba(255, 159, 0, .55) !important;
}

.sidebar .logout:hover .icono-sigta {
  color: var(--sigta-azul);
}


/* =========================================================
   BOTÓN DESPLEGABLE (solo móvil)
========================================================= */

.menu-toggle {

  display: none;

  flex-shrink: 0;

  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;

  width: 34px;
  height: 34px;

  border: none;
  border-radius: 7px;

  background:
    rgba(255, 255, 255, .1);

  cursor: pointer;
}


.menu-toggle span {

  width: 16px;
  height: 2px;

  border-radius: 2px;

  background: var(--sigta-blanco);

  transition:
    transform .2s ease,
    opacity .2s ease;
}


.menu-toggle[aria-expanded="true"] span:nth-child(1) {
  transform: translateY(6px) rotate(45deg);
}

.menu-toggle[aria-expanded="true"] span:nth-child(2) {
  opacity: 0;
}

.menu-toggle[aria-expanded="true"] span:nth-child(3) {
  transform: translateY(-6px) rotate(-45deg);
}


/* =========================================================
   CUERPO DESPLEGABLE
========================================================= */

.sidebar-body {

  display: flex;
  flex: 1;
  flex-direction: column;
  min-height: 0;
}


/* =========================================================
   RESPONSIVE
========================================================= */

@media (
  max-width: 760px
) {

  .sidebar {

    position: relative;

    width: 100%;
    min-width: 100%;

    height: auto;

    min-height: auto;

    overflow-y: visible;
  }


  .menu-toggle {

    display: flex;
  }


  .sidebar-body {

    max-height: 0;

    overflow: hidden;

    transition:
      max-height .25s ease;
  }


  .sidebar-body.abierto {

    max-height: min(65vh, 460px);

    overflow-y: auto;

    -webkit-overflow-scrolling: touch;
  }


  .logout {

    margin-top: 20px;
  }

}

</style>
