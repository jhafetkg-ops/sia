<template>
  <div class="header-usuario">
    <button
      v-if="puedeActualizar"
      type="button"
      class="usuario-refresh"
      @click="actualizar"
    >↻ Actualizar</button>

    <button type="button" class="user-box" @click="abrirPerfil">
      <div class="user-avatar">{{ inicialesUsuario }}</div>
      <div class="user-datos">
        <strong>{{ nombreUsuario }}</strong>
        <span>{{ usuario.email || '' }}</span>
      </div>
    </button>
  </div>

  <div v-if="panelAbierto" class="perfil-backdrop" @click.self="panelAbierto = false">
    <section class="perfil-panel">
      <header class="perfil-head">
        <div>
          <h3>Mi perfil</h3>
          <small>{{ perfil.rol_nombre || '' }}</small>
        </div>
        <button type="button" class="perfil-cerrar" aria-label="Cerrar" @click="panelAbierto = false">✕</button>
      </header>

      <div class="perfil-body">
        <div class="perfil-identidad">
          <div class="user-avatar">{{ inicialesUsuario }}</div>
          <div>
            <strong>{{ perfil.nombre_completo || nombreUsuario }}</strong>
            <span>{{ perfil.email || usuario.email || '' }}</span>
          </div>
        </div>

        <p v-if="cargandoPerfil" class="perfil-aviso">Cargando...</p>
        <p v-else-if="errorPerfil" class="perfil-aviso">{{ errorPerfil }}</p>

        <dl v-else class="perfil-datos">
          <div>
            <dt>Nombre completo</dt>
            <dd>{{ perfil.nombre_completo || '—' }}</dd>
          </div>
          <div>
            <dt>Correo institucional</dt>
            <dd>{{ perfil.email || '—' }}</dd>
          </div>
          <div>
            <dt>Rol</dt>
            <dd>{{ perfil.rol_nombre || '—' }}</dd>
          </div>
        </dl>
      </div>
    </section>
  </div>
</template>

<script setup>
/*
  Bloque de usuario del encabezado (arriba a la derecha).

  Al pulsarlo abre un panel de solo lectura con los datos de la cuenta.
  Consulta el endpoint que ya existe, /api/usuarios/mi-perfil/ (GET), el
  mismo que usa la pantalla de perfil; no navega a ninguna ruta, no toca
  el guard, los permisos ni el flujo de ninguna pantalla, y no escribe
  nada (el PATCH de ese endpoint no se usa aqui).
*/
import { computed, ref, useAttrs } from 'vue'

defineOptions({ inheritAttrs: false })

/* El boton de actualizar se muestra solo si la pantalla enlazo
   @actualizar con SU PROPIA funcion de recarga; aqui no se define
   ninguna logica de carga, solo se invoca la que ya existe. */
const attrs = useAttrs()
const puedeActualizar = computed(() => typeof attrs.onActualizar === 'function')
function actualizar() {
  if (puedeActualizar.value) attrs.onActualizar()
}

const usuario = ref(JSON.parse(localStorage.getItem('sigta_usuario') || '{}'))

const panelAbierto = ref(false)
const cargandoPerfil = ref(false)
const errorPerfil = ref('')
const perfil = ref({})

const nombreUsuario = computed(() =>
  usuario.value?.nombre || usuario.value?.nombre_completo || usuario.value?.email || ''
)

const inicialesUsuario = computed(() =>
  (perfil.value?.nombre_completo || nombreUsuario.value || '')
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map(palabra => palabra.charAt(0).toUpperCase())
    .join('')
)

async function abrirPerfil() {
  panelAbierto.value = true
  cargandoPerfil.value = true
  errorPerfil.value = ''
  try {
    const respuesta = await fetch('/api/usuarios/mi-perfil/', {
      headers: { Authorization: `Token ${localStorage.getItem('sigta_token')}` },
    })
    if (respuesta.ok) {
      perfil.value = await respuesta.json()
    } else {
      errorPerfil.value = 'No se pudo cargar la información del perfil.'
    }
  } catch {
    errorPerfil.value = 'No se pudo cargar la información del perfil.'
  } finally {
    cargandoPerfil.value = false
  }
}
</script>

<style scoped>
/* Mismos valores que el bloque original del dashboard del Director,
   mas los reinicios propios de un <button> para que sea pulsable. */
.user-box {
  min-width: 205px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 9px;
  padding: 10px 14px;
  border: 0;
  background: var(--sigta-blanco);
  border-radius: 9px;
  box-shadow: 0 3px 10px rgba(0,0,0,.07);
  font-family: inherit;
  text-align: left;
  cursor: pointer;
  transition: box-shadow .2s ease, transform .2s ease;
}

.user-box:hover {
  box-shadow: 0 6px 16px rgba(0,0,0,.12);
  transform: translateY(-1px);
}

.user-avatar {
  width: 35px;
  height: 35px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--sigta-mostaza);
  color: var(--sigta-azul);
  font-size: 15px;
  font-weight: 900;
}

.user-datos {
  min-width: 0;
}

.user-box strong,
.user-box span {
  display: block;
  max-width: 190px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-box strong {
  color: var(--sigta-azul);
  font-size: 17px;
}

.user-box span {
  margin-top: 2px;
  color: var(--sigta-texto-suave);
  font-size: 15px;
}

.header-usuario {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 12px;
}

/* Mismo aspecto que el boton .refresh que ya usaban los dashboards. */
.usuario-refresh {
  flex-shrink: 0;
  padding: 10px 15px;
  border: 1px solid var(--sigta-borde);
  border-radius: 8px;
  background: var(--sigta-blanco);
  color: var(--sigta-azul);
  font-family: inherit;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 3px 10px rgba(0,0,0,.07);
  transition: background .2s ease, color .2s ease;
}

.usuario-refresh:hover {
  background: var(--sigta-azul);
  color: var(--sigta-blanco);
}

/* ---------- Panel de perfil (solo lectura) ---------- */
.perfil-backdrop {
  position: fixed;
  inset: 0;
  z-index: 10050;
  display: grid;
  place-items: center;
  padding: 20px;
  background: rgba(18, 58, 107, .55);
}

.perfil-panel {
  width: min(460px, 100%);
  background: var(--sigta-blanco);
  border-radius: 14px;
  box-shadow: 0 24px 60px rgba(11, 40, 79, .3);
  overflow: hidden;
}

.perfil-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 16px 20px;
  border-bottom: 1px solid var(--sigta-borde-suave);
}

.perfil-head h3 {
  margin: 0;
  color: var(--sigta-azul);
  font-size: 17px;
}

.perfil-head small {
  display: block;
  margin-top: 2px;
  color: var(--sigta-texto-suave);
  font-size: 12px;
}

.perfil-cerrar {
  flex-shrink: 0;
  border: 0;
  background: transparent;
  color: var(--sigta-texto-suave);
  font-size: 17px;
  cursor: pointer;
}

.perfil-body {
  padding: 18px 20px 22px;
}

.perfil-identidad {
  display: flex;
  align-items: center;
  gap: 12px;
  padding-bottom: 16px;
  margin-bottom: 16px;
  border-bottom: 1px solid var(--sigta-borde-suave);
}

.perfil-identidad strong {
  display: block;
  color: var(--sigta-texto);
  font-size: 15px;
}

.perfil-identidad span {
  display: block;
  margin-top: 2px;
  color: var(--sigta-texto-suave);
  font-size: 13px;
}

.perfil-aviso {
  margin: 0;
  padding: 14px 0;
  color: var(--sigta-texto-suave);
  font-size: 13px;
}

.perfil-datos {
  margin: 0;
  display: grid;
  gap: 13px;
}

.perfil-datos dt {
  color: var(--sigta-texto-suave);
  font-size: 11px;
  font-weight: 800;
  letter-spacing: .5px;
  text-transform: uppercase;
}

.perfil-datos dd {
  margin: 3px 0 0;
  color: var(--sigta-texto);
  font-size: 14px;
  word-break: break-word;
}
</style>
