<template>
  <div class="deleg">
    <div class="instruction">
      <b>Delegar aprobación temporal</b>
      <span>Ceda temporalmente su rol de {{ rolNombre }} a otro usuario habilitado mientras esté ausente. El sistema respeta automáticamente la vigencia: fuera de esas fechas, la delegación deja de tener efecto.</span>
    </div>

    <div class="panel form">
      <h3>Nueva delegación</h3>
      <label class="campo">Correo del usuario a quien delega
        <div class="buscar">
          <input v-model="emailBuscar" placeholder="correo@emi.edu.bo" @keyup.enter="buscarUsuario">
          <button type="button" @click="buscarUsuario">Buscar</button>
        </div>
      </label>
      <p v-if="usuarioEncontrado" class="encontrado">Delegado: <b>{{ usuarioEncontrado.nombre_completo || usuarioEncontrado.email }}</b> ({{ usuarioEncontrado.email }})</p>
      <p v-if="errorBusqueda" class="error">{{ errorBusqueda }}</p>

      <div class="fechas">
        <label class="campo">Desde<input v-model="form.vigencia_desde" type="datetime-local"></label>
        <label class="campo">Hasta<input v-model="form.vigencia_hasta" type="datetime-local"></label>
      </div>
      <label class="campo">Motivo (opcional)<input v-model="form.motivo" placeholder="Ej.: Viaje institucional"></label>

      <div class="actions">
        <button class="primary" :disabled="procesando||!usuarioEncontrado||!form.vigencia_desde||!form.vigencia_hasta" @click="crearDelegacion">Delegar rol {{ rolNombre }}</button>
      </div>
    </div>

    <div class="panel">
      <h3>Delegaciones que otorgué</h3>
      <div class="table" v-if="otorgadas.length">
        <div class="thead"><span>Delegado a</span><span>Vigencia</span><span>Motivo</span><span>Estado</span><span>Acción</span></div>
        <div class="row" v-for="d in otorgadas" :key="d.id">
          <span>{{ d.delegado_nombre }}</span>
          <span>{{ formatoFecha(d.vigencia_desde) }} — {{ formatoFecha(d.vigencia_hasta) }}</span>
          <span>{{ d.motivo || '—' }}</span>
          <em>{{ d.activo ? (d.vigente ? 'Vigente' : 'Fuera de vigencia') : 'Revocada' }}</em>
          <button v-if="d.activo" @click="revocar(d)">Revocar</button>
        </div>
      </div>
      <div v-else class="empty">Aún no ha delegado su rol a nadie.</div>
    </div>

    <div class="panel" v-if="recibidas.length">
      <h3>Delegaciones que recibí</h3>
      <div class="table">
        <div class="thead"><span>Otorgada por</span><span>Vigencia</span><span>Motivo</span><span>Estado</span></div>
        <div class="row" v-for="d in recibidas" :key="d.id">
          <span>{{ d.delegante_nombre }}</span>
          <span>{{ formatoFecha(d.vigencia_desde) }} — {{ formatoFecha(d.vigencia_hasta) }}</span>
          <span>{{ d.motivo || '—' }}</span>
          <em>{{ d.activo ? (d.vigente ? 'Vigente' : 'Fuera de vigencia') : 'Revocada' }}</em>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

const props = defineProps({
  rolCodigo: { type: String, required: true },
  rolNombre: { type: String, required: true },
})

const usuario = ref(JSON.parse(localStorage.getItem('sigta_usuario') || '{}'))
const delegaciones = ref([])
const emailBuscar = ref('')
const usuarioEncontrado = ref(null)
const errorBusqueda = ref('')
const procesando = ref(false)
const form = reactive({ vigencia_desde: '', vigencia_hasta: '', motivo: '' })

const otorgadas = computed(() => delegaciones.value.filter(d => d.delegante === usuario.value.id))
const recibidas = computed(() => delegaciones.value.filter(d => d.delegado === usuario.value.id))

function headersJson() {
  return { Authorization: `Token ${localStorage.getItem('sigta_token')}`, 'Content-Type': 'application/json' }
}

function formatoFecha(v) {
  if (!v) return '—'
  return new Date(v).toLocaleString('es-BO', { dateStyle: 'medium', timeStyle: 'short' })
}

async function cargar() {
  const r = await fetch('/api/usuarios/delegaciones/', { headers: { Authorization: `Token ${localStorage.getItem('sigta_token')}` } })
  const d = await r.json().catch(() => [])
  delegaciones.value = Array.isArray(d) ? d : (d.results || [])
}

async function buscarUsuario() {
  errorBusqueda.value = ''
  usuarioEncontrado.value = null
  if (!emailBuscar.value.trim()) return
  try {
    const r = await fetch(`/api/usuarios/buscar-usuario/?email=${encodeURIComponent(emailBuscar.value.trim())}`, {
      headers: { Authorization: `Token ${localStorage.getItem('sigta_token')}` },
    })
    const d = await r.json()
    if (!r.ok) throw new Error(d.detalle || 'No se encontró el usuario.')
    usuarioEncontrado.value = d
  } catch (e) {
    errorBusqueda.value = e.message
  }
}

async function crearDelegacion() {
  procesando.value = true
  try {
    const r = await fetch('/api/usuarios/delegaciones/', {
      method: 'POST',
      headers: headersJson(),
      body: JSON.stringify({
        delegado: usuarioEncontrado.value.id,
        rol_codigo: props.rolCodigo,
        vigencia_desde: new Date(form.vigencia_desde).toISOString(),
        vigencia_hasta: new Date(form.vigencia_hasta).toISOString(),
        motivo: form.motivo.trim(),
      }),
    })
    const d = await r.json().catch(() => ({}))
    if (!r.ok) throw new Error(d.detalle || Object.values(d)[0] || 'No fue posible crear la delegación.')
    usuarioEncontrado.value = null
    emailBuscar.value = ''
    form.vigencia_desde = ''
    form.vigencia_hasta = ''
    form.motivo = ''
    await cargar()
    alert('Delegación registrada correctamente.')
  } catch (e) {
    alert(e.message)
  } finally {
    procesando.value = false
  }
}

async function revocar(d) {
  if (!await window.sigtaConfirm(`¿Revocar la delegación otorgada a ${d.delegado_nombre}?`)) return
  try {
    const r = await fetch(`/api/usuarios/delegaciones/${d.id}/revocar/`, { method: 'POST', headers: headersJson(), body: '{}' })
    const respuesta = await r.json().catch(() => ({}))
    if (!r.ok) throw new Error(respuesta.detalle || 'No fue posible revocar la delegación.')
    await cargar()
  } catch (e) {
    alert(e.message)
  }
}

onMounted(cargar)
</script>

<style scoped>
.deleg{display:flex;flex-direction:column;gap:16px}
.instruction{background:var(--sigta-mostaza-suave);border-left:4px solid var(--sigta-mostaza);padding:14px 17px;border-radius:7px}
.instruction b,.instruction span{display:block}
.instruction span{font-size:12px;color:var(--sigta-texto-suave);margin-top:4px}
.panel{background:white;border:1px solid var(--sigta-borde);border-radius:11px;padding:22px}
.panel h3{margin:0 0 14px}
.campo{display:block;margin:12px 0;font-size:12px;font-weight:700;color:var(--sigta-texto-suave)}
.campo input,.campo select,.campo textarea{display:block;width:100%;margin-top:6px;padding:9px 11px;border:1px solid var(--sigta-azul-texto-claro);border-radius:7px;font-family:inherit;font-size:13px;font-weight:400;color:var(--sigta-texto)}
.buscar{display:flex;gap:8px;margin-top:6px}
.buscar input{flex:1;padding:9px 11px;border:1px solid var(--sigta-azul-texto-claro);border-radius:7px}
.buscar button{padding:9px 14px;border-radius:7px;border:1px solid var(--sigta-borde);background:white;cursor:pointer;font-weight:700}
.fechas{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.encontrado{font-size:12px;color:var(--sigta-exito);margin:8px 0 0}
.error{font-size:12px;color:var(--sigta-error);margin:8px 0 0}
.actions{margin-top:16px}
.primary{background:var(--sigta-azul)!important;color:white!important;border-color:var(--sigta-azul)!important;padding:10px 16px;border-radius:7px;border:1px solid var(--sigta-azul);cursor:pointer;font-weight:700}
.primary:disabled{opacity:.5;cursor:not-allowed}
.table{background:white;border:1px solid var(--sigta-borde);border-radius:10px;overflow:hidden}
.thead,.row{display:grid;grid-template-columns:1.2fr 1.6fr 1fr .8fr .6fr;gap:10px;align-items:center;padding:12px 16px}
.thead{background:var(--sigta-azul-tenue);color:var(--sigta-texto-suave);font-size:10px;font-weight:800}
.row{border-top:1px solid var(--sigta-borde);font-size:12px}
.row em{font-style:normal;color:var(--sigta-exito)}
.row button{padding:6px 10px;border-radius:6px;border:1px solid var(--sigta-error-fondo);background:white;color:var(--sigta-error);cursor:pointer;font-size:11px}
.empty{text-align:center;background:white;border:1px dashed var(--sigta-borde);padding:30px;border-radius:10px;color:var(--sigta-texto-suave)}
@media(max-width:720px){.fechas{grid-template-columns:1fr}.thead,.row{grid-template-columns:1fr;gap:4px}}
</style>
