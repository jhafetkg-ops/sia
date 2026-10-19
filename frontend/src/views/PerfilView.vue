<template>
  <div class="layout">
    <SolicitanteMenu />
    <main class="content">
      <header class="topbar">
        <div>
          <h1>Mi perfil</h1>
          <p>Consulte y actualice la información de su cuenta registrada en SIA.</p>
        </div>
      </header>

      <section class="summary">
        <article>
          <span>Usuario</span>
          <strong>{{ iniciales }}</strong>
          <small>{{ form.nombre_completo || 'Usuario' }}</small>
        </article>
        <article>
          <span>Área</span>
          <strong class="summary-text">{{ form.area_nombre || 'Sin área' }}</strong>
          <small>Dependencia registrada</small>
        </article>
        <article>
          <span>Cuenta</span>
          <strong class="summary-text">Activa</strong>
          <small>{{ form.rol_nombre || 'Solicitante' }}</small>
        </article>
      </section>

      <section class="profile-sheet requests-card">
        <div class="identity">
          <div class="avatar">{{ iniciales }}</div>
          <div><strong>{{ form.nombre_completo || 'Usuario' }}</strong><span>{{ form.email }}</span></div>
        </div>

        <form @submit.prevent="guardar">
          <div class="field">
            <label for="nombre">Nombre completo</label>
            <input id="nombre" v-model="form.nombre_completo" maxlength="150" required :disabled="guardando" />
          </div>
          <div class="field">
            <label for="correo">Correo institucional</label>
            <input id="correo" v-model="form.email" disabled />
            <small>El correo identifica su cuenta y no se modifica desde el perfil.</small>
          </div>
          <div class="field">
            <label for="area">Área</label>
            <select id="area" v-model="form.area_id" required :disabled="guardando">
              <option value="">Seleccione un área</option>
              <option v-for="area in areas" :key="area.id" :value="area.id">{{ area.nombre }}</option>
            </select>
          </div>
          <div class="field">
            <label>Rol</label>
            <input :value="form.rol_nombre || 'Solicitante'" disabled />
          </div>

          <SistemaNotificacion
            v-if="mensaje"
            :key="mensaje"
            :tipo="esError ? 'error' : 'exito'"
            :titulo="esError ? 'No se pudo actualizar el perfil' : 'Perfil actualizado'"
            :descripcion="mensaje"
            :duracion="esError ? 0 : 5000"
            @close="mensaje = ''"
          />

          <div class="actions"><button type="submit" :disabled="guardando">{{ guardando ? 'Guardando...' : 'Guardar cambios' }}</button></div>
        </form>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import SolicitanteMenu from '../components/SolicitanteMenu.vue'
import SistemaNotificacion from '../components/SistemaNotificacion.vue'

const areas = ref([]), guardando = ref(false), mensaje = ref(''), esError = ref(false)
const form = reactive({ nombre_completo: '', email: '', area_id: '', rol_nombre: '' })
const token = () => localStorage.getItem('sigta_token')
const headers = () => ({ Authorization: `Token ${token()}`, Accept: 'application/json' })
const iniciales = computed(() => (form.nombre_completo || 'Usuario').split(' ').filter(Boolean).slice(0, 2).map(x => x[0]).join('').toUpperCase())

async function cargar() {
  try {
    const [perfilRespuesta, areasRespuesta] = await Promise.all([
      fetch('/api/usuarios/mi-perfil/', { headers: headers() }),
      fetch('/api/usuarios/areas/', { headers: headers() }),
    ])
    if (!perfilRespuesta.ok || !areasRespuesta.ok) throw new Error('No fue posible cargar el perfil.')
    Object.assign(form, await perfilRespuesta.json())
    const datosAreas = await areasRespuesta.json()
    areas.value = Array.isArray(datosAreas) ? datosAreas : (datosAreas.results || [])
  } catch (error) {
    console.error('Error cargando perfil:', error)
    esError.value = true; mensaje.value = error.message
  }
}

async function guardar() {
  guardando.value = true; mensaje.value = ''; esError.value = false
  try {
    const respuesta = await fetch('/api/usuarios/mi-perfil/', {
      method: 'PATCH',
      headers: { ...headers(), 'Content-Type': 'application/json' },
      body: JSON.stringify({ nombre_completo: form.nombre_completo.trim(), area_id: form.area_id }),
    })
    const datos = await respuesta.json()
    if (!respuesta.ok) throw new Error(datos.nombre_completo || datos.area_id || datos.detalle || 'No se pudo actualizar el perfil.')
    Object.assign(form, datos)
    const usuario = JSON.parse(localStorage.getItem('sigta_usuario') || '{}')
    usuario.nombre = datos.nombre_completo; usuario.nombre_completo = datos.nombre_completo
    if (usuario.roles?.[0]) { usuario.roles[0].area_id = datos.area_id; usuario.roles[0].area_nombre = datos.area_nombre; usuario.roles[0].area = datos.area_nombre }
    localStorage.setItem('sigta_usuario', JSON.stringify(usuario))
    mensaje.value = 'Su nombre y área se guardaron correctamente.'
  } catch (error) {
    console.error('Error actualizando perfil:', error)
    esError.value = true; mensaje.value = error.message
  } finally { guardando.value = false }
}

onMounted(cargar)
</script>

<style scoped>
* { box-sizing: border-box; }
.layout { min-height: 100vh; display: flex; background: var(--sigta-azul-tenue); font-family: var(--sigta-fuente); }
.content { flex: 1; min-width: 0; padding: 27px 30px 45px; overflow-x: hidden; }
.topbar { display: flex; align-items: center; justify-content: space-between; gap: 20px; margin-bottom: 20px; }
.topbar h1 { margin: 0; color: var(--sigta-texto); font-size: 33px; }
.topbar p { margin: 5px 0 0; color: var(--sigta-texto-suave); font-size: 17px; }
.summary { display: grid; grid-template-columns: repeat(3, 1fr); gap: 13px; margin-bottom: 17px; }
.summary article { min-height: 104px; padding: 16px; border-top: 4px solid var(--sigta-mostaza); border-radius: 9px; background: white; box-shadow: 0 3px 12px rgba(0,0,0,.05); }
.summary span, .summary small { display: block; }
.summary span { color: var(--sigta-texto-suave); font-size: 14px; font-weight: 800; text-transform: uppercase; }
.summary strong { display: block; margin: 7px 0 4px; color: var(--sigta-azul); font-size: 31px; }
.summary strong.summary-text { overflow: hidden; font-size: 21px; line-height: 37px; text-overflow: ellipsis; white-space: nowrap; }
.summary small { color: var(--sigta-texto-suave); font-size: 14px; }
.requests-card { overflow: hidden; border-radius: 10px; background: white; box-shadow: 0 4px 14px rgba(0,0,0,.05); }
.identity { display: flex; align-items: center; gap: 14px; padding: 20px; border-bottom: 1px solid var(--sigta-azul-tenue); }
.avatar { width: 56px; height: 56px; display: grid; place-items: center; flex-shrink: 0; border-radius: 50%; background: var(--sigta-azul); color: white; font-size: 20px; font-weight: 800; }
.identity strong, .identity span { display: block; }
.identity strong { color: var(--sigta-azul); font-size: 18px; }
.identity span { margin-top: 4px; color: var(--sigta-texto-suave); font-size: 14px; }
form { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; padding: 20px; }
.field { display: flex; flex-direction: column; gap: 5px; }
.field label { color: var(--sigta-texto-suave); font-size: 14px; font-weight: 800; }
.field input, .field select { width: 100%; height: 40px; padding: 0 11px; border: 1px solid var(--sigta-borde); border-radius: 6px; background: white; color: var(--sigta-azul); font-family: inherit; font-size: 15px; outline: none; }
.field input:disabled { background: var(--sigta-azul-tenue); color: var(--sigta-texto-suave); }
.field small { color: var(--sigta-texto-suave); font-size: 12px; }
form :deep(.notificacion) { grid-column: 1 / -1; margin: 0; }
.actions { grid-column: 1 / -1; display: flex; justify-content: flex-end; padding-top: 4px; }
.actions button { min-height: 41px; padding: 0 18px; border: 0; border-radius: 7px; background: var(--sigta-azul); color: white; font-size: 15px; font-weight: 800; cursor: pointer; }
@media (max-width: 760px) { .layout { display: block; } .content { padding: 18px 15px 35px; } .summary, form { grid-template-columns: 1fr; } .actions { grid-column: auto; } .actions button { width: 100%; } }
</style>
