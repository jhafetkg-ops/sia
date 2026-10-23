<template>
  <div class="layout sigta-role-layout">
    <aside :class="{ abierto: menuAbierto }">
      <div class="brand-row">
        <div class="brand"><b><img src="/img/emi.jpg" alt="EMI"></b><div><strong>SIGTA</strong><small>Mantenimiento</small></div></div>
        <button type="button" class="menu-toggle" :aria-expanded="menuAbierto" aria-label="Mostrar opciones del menú" @click="menuAbierto = !menuAbierto"><span></span><span></span><span></span></button>
      </div>
      <div class="profile"><i>{{ iniciales }}</i><div><b>{{ nombre }}</b><small>Técnico de Mantenimiento</small></div></div>
      <p>MI TRABAJO</p>
      <button v-for="m in menu" :key="m.id" :class="{active:vista===m.id}" @click="irA(m.id)"><span>{{ m.icono }}</span>{{ m.nombre }}<em v-if="m.total!==undefined">{{ m.total }}</em></button>
      <div class="bottom"><button @click="salir"><span>↪</span>Cerrar sesión</button></div>
    </aside>

    <main>
      <header>
        <div><small>SIGTA / MANTENIMIENTO / {{ titulo }}</small><h1>{{ titulo }}</h1><p>{{ subtitulo }}</p></div>
        <button class="refresh" :disabled="cargando" @click="cargar">↻ Actualizar</button>
      </header>

      <!-- ============================ RESUMEN ============================ -->
      <section v-if="vista==='resumen'">
        <div class="hero">
          <div><small>TÉCNICO DE MANTENIMIENTO</small><h2>{{ saludo }}, {{ primerNombre }}</h2><p>Órdenes de trabajo asignadas a usted.</p></div>
          <span>MT</span>
        </div>

        <div v-if="conRetorno.length" class="alerta">
          <b>⚠ {{ conRetorno.length }} orden(es) devuelta(s) por la jefatura</b>
          <span>{{ conRetorno.map(r=>r.codigo).join(', ') }} — el problema no quedó resuelto; repita la intervención.</span>
        </div>

        <div class="stats">
          <article @click="irA('ordenes')"><i class="blue">OT</i><div><small>Órdenes por recibir</small><b>{{ porRecibir.length }}</b><p>designadas por la jefatura</p></div></article>
          <article @click="irA('trabajo')"><i class="gold">RP</i><div><small>En reparación</small><b>{{ porReparar.length }}</b><p>trabajo en curso</p></div></article>
          <article @click="irA('trabajo')"><i class="green">PB</i><div><small>Por probar</small><b>{{ porProbar.length }}</b><p>pruebas e informe</p></div></article>
          <article @click="irA('compras')"><i class="navy">CO</i><div><small>En espera de compra</small><b>{{ enEsperaCompra.length }}</b><p>flujo en pausa</p></div></article>
        </div>

        <div class="panels">
          <section class="panel">
            <div class="panel-head"><div><small>FLUJO BPMN</small><h3>Atención del mantenimiento</h3></div></div>
            <button class="flow" @click="irA('ordenes')"><i class="blue">1</i><div><b>Recibir orden de trabajo</b><small>Tomar conocimiento del requerimiento designado</small></div><strong>›</strong></button>
            <button class="flow" @click="irA('ordenes')"><i class="blue">2</i><div><b>Inspección técnica y diagnóstico</b><small>Determinar la falla y si requiere compra</small></div><strong>›</strong></button>
            <button class="flow" @click="irA('compras')"><i class="navy">3</i><div><b>Realizar requerimiento</b><small>Características del componente y cotización</small></div><strong>›</strong></button>
            <button class="flow" @click="irA('trabajo')"><i class="gold">4</i><div><b>Reparación o instalación</b><small>Ejecutar y registrar la intervención</small></div><strong>›</strong></button>
            <button class="flow" @click="irA('trabajo')"><i class="green">5</i><div><b>Pruebas e informe a la jefatura</b><small>Comprobar el funcionamiento y elevar el informe</small></div><strong>›</strong></button>
          </section>
          <section class="panel">
            <div class="panel-head"><div><small>SEGUIMIENTO</small><h3>Historial</h3></div></div>
            <p class="copy">Consulte los requerimientos que ya atendió y su estado actual.</p>
            <button class="wide primary" @click="irA('historial')">Ver historial →</button>
          </section>
        </div>
      </section>

      <!-- ==================== A. ÓRDENES DE TRABAJO ==================== -->
      <section v-else-if="vista==='ordenes' && !ordenAbierta">
        <div class="instruction"><b>Recibir orden de trabajo</b><span>Revise los datos del requerimiento y abra la hoja de trabajo para registrar el diagnóstico.</span></div>
        <div v-if="cargando" class="empty">Consultando órdenes…</div>
        <div v-else-if="porRecibir.length" class="cards">
          <article v-for="r in porRecibir" :key="r.id">
            <div class="top"><span>{{ r.codigo }}</span><em>{{ r.prioridad_jefatura || r.estado_codigo }}</em></div>
            <h3>{{ r.titulo }}</h3>
            <ul class="datos">
              <li><b>Designada</b><span>{{ fecha(r.derivado_en) }}</span></li>
              <li><b>Ubicación</b><span>{{ r.ubicacion || 's/d' }}</span></li>
              <li><b>Solicitante</b><span>{{ r.solicitante_nombre || 's/d' }}</span></li>
            </ul>
            <p>{{ (r.descripcion||'').slice(0,140) }}</p>
            <a v-if="r.evidencia_archivo_url" class="adjunto" :href="r.evidencia_archivo_url" target="_blank">📎 Evidencia del solicitante</a>
            <div class="actions">
              <button @click="verItem(r)">Ver detalle</button>
              <button class="primary" @click="recibirOrden(r)">Recibir orden de trabajo</button>
            </div>
          </article>
        </div>
        <div v-else class="empty"><span>✓</span><h3>Bandeja al día</h3><p>No tiene órdenes pendientes de recibir.</p></div>
      </section>

      <!-- ============ B/C. DIAGNÓSTICO Y REQUERIMIENTO ============ -->
      <section v-else-if="vista==='ordenes' && ordenAbierta" class="panel hoja">
        <div class="hoja-head">
          <div><small>ORDEN DE TRABAJO</small><h3>{{ ordenAbierta.codigo }} — {{ ordenAbierta.titulo }}</h3></div>
          <button class="refresh" @click="cerrarOrden">Cerrar hoja</button>
        </div>

        <template v-if="!modoComponente">
          <label class="campo">Inspección técnica y diagnóstico
            <textarea v-model="formDiagnostico.diagnostico" rows="4" placeholder="Falla detectada y componente afectado"></textarea>
          </label>
          <label class="campo">Plan de solución
            <textarea v-model="formDiagnostico.plan_solucion" rows="3" placeholder="Acciones previstas para resolver el problema"></textarea>
          </label>

          <fieldset class="compuerta">
            <legend>¿Requiere compra de componentes o materiales?</legend>
            <label><input v-model="formDiagnostico.requiere_compra" type="radio" :value="false"> No</label>
            <label><input v-model="formDiagnostico.requiere_compra" type="radio" :value="true"> Sí</label>
          </fieldset>

          <div class="actions">
            <button @click="cerrarOrden">Cancelar</button>
            <button class="primary" :disabled="procesando||!formDiagnostico.diagnostico.trim()||!formDiagnostico.plan_solucion.trim()" @click="guardarDiagnostico">
              {{ formDiagnostico.requiere_compra ? 'Guardar y realizar requerimiento' : 'Guardar diagnóstico' }}
            </button>
          </div>
        </template>

        <template v-else>
          <div class="instruction"><b>Realizar requerimiento</b><span>El trabajo quedará en pausa hasta que la jefatura evalúe la viabilidad y Almacén entregue el componente.</span></div>
          <label class="campo">Componente requerido
            <input v-model="formComponente.producto_requerido" placeholder="Ej.: Compresor 12000 BTU">
          </label>
          <label class="campo">Características del componente
            <textarea v-model="formComponente.especificacion_producto" rows="3" placeholder="Marca, modelo, voltaje y demás especificaciones"></textarea>
          </label>
          <label class="campo">Cantidad
            <input v-model="formComponente.cantidad_requerida" type="number" min="1">
          </label>
          <label class="campo">Costo estimado (Bs.)
            <input v-model="formComponente.costo_estimado" type="number" min="0" step="0.01">
          </label>
          <label class="campo">Cotización
            <input type="file" accept="application/pdf,image/*" @change="onCotizacion">
          </label>
          <div class="actions">
            <button @click="cerrarOrden">Cancelar</button>
            <button class="primary" :disabled="procesando||!formComponente.producto_requerido.trim()" @click="enviarRequerimiento">Enviar requerimiento</button>
          </div>
        </template>
      </section>

      <!-- ==================== EN ESPERA DE COMPRA ==================== -->
      <section v-else-if="vista==='compras'">
        <div class="instruction"><b>Requerimientos en curso</b><span>El trabajo está en pausa: se reanuda cuando Almacén entregue el componente.</span></div>
        <div v-if="enEsperaCompra.length" class="cards">
          <article v-for="r in enEsperaCompra" :key="r.id">
            <div class="top"><span>{{ r.codigo }}</span><em>{{ r.estado_compra_componente }}</em></div>
            <h3>{{ r.titulo }}</h3>
            <ul class="datos">
              <li><b>Componente</b><span>{{ r.producto_requerido || 's/d' }}</span></li>
              <li><b>Costo estimado</b><span>{{ r.costo_estimado ? `Bs. ${r.costo_estimado}` : 's/d' }}</span></li>
              <li><b>Expediente</b><span>{{ r.codigo_compra_vinculada || 'aún no generado' }}</span></li>
            </ul>
            <p>{{ r.estado_compra_componente === 'SOLICITADA' ? 'Pendiente de que la jefatura evalúe la viabilidad.' : 'Compra en curso en la DAF.' }}</p>
            <div class="actions"><button @click="verItem(r)">Ver detalle</button></div>
          </article>
        </div>
        <div v-else class="empty"><span>✓</span><h3>Sin requerimientos en curso</h3><p>Ninguna orden suya espera una compra.</p></div>
      </section>

      <!-- ============= D. REPARACIÓN, PRUEBAS E INFORME ============= -->
      <section v-else-if="vista==='trabajo'">
        <div class="instruction"><b>Reparación, pruebas e informe</b><span>Registre la intervención, ejecute las pruebas técnicas y eleve el informe a la jefatura.</span></div>

        <div v-if="!itemActivo" class="cards">
          <article v-for="r in enTrabajo" :key="r.id" :class="{ retorno: Number(r.rework_count) > 0 }">
            <div class="top"><span>{{ r.codigo }}</span><em>{{ etiqueta(r) }}</em></div>
            <h3>{{ r.titulo }}</h3>
            <div v-if="Number(r.rework_count) > 0" class="mini-alerta">⚠ Devuelta por la jefatura: el problema no quedó resuelto</div>
            <ul class="datos">
              <li><b>Prioridad</b><span>{{ r.prioridad_jefatura || 's/d' }}</span></li>
              <li v-if="r.producto_requerido"><b>Componente</b><span>{{ r.producto_requerido }}</span></li>
            </ul>
            <p>{{ (r.diagnostico||r.descripcion||'').slice(0,140) }}</p>
            <div class="actions">
              <button @click="verItem(r)">Ver detalle</button>
              <button class="primary" @click="abrirTrabajo(r)">{{ siguientePaso(r) }}</button>
            </div>
          </article>
          <div v-if="!enTrabajo.length" class="empty"><span>✓</span><h3>Bandeja al día</h3><p>No hay órdenes en reparación ni pendientes de pruebas.</p></div>
        </div>

        <div v-else class="panel hoja">
          <div class="hoja-head">
            <div><small>HOJA DE TRABAJO</small><h3>{{ itemActivo.codigo }} — {{ itemActivo.titulo }}</h3></div>
            <button class="refresh" @click="itemActivo=null">Volver</button>
          </div>

          <div v-if="Number(itemActivo.rework_count) > 0" class="alerta">
            <b>⚠ La jefatura devolvió este caso</b>
            <span>El problema no quedó resuelto en la intervención anterior.</span>
          </div>

          <template v-if="!itemActivo.trabajo_realizado">
            <label class="campo">Reparación o instalación realizada
              <textarea v-model="formTrabajo.trabajo_realizado" rows="5" placeholder="Trabajo ejecutado sobre el equipo o instalación"></textarea>
            </label>
            <label class="campo">Observaciones
              <textarea v-model="formTrabajo.observaciones_trabajo" rows="2"></textarea>
            </label>
            <div class="actions">
              <button @click="itemActivo=null">Cancelar</button>
              <button class="primary" :disabled="procesando||!formTrabajo.trabajo_realizado.trim()" @click="registrarTrabajo">Guardar reparación</button>
            </div>
          </template>

          <template v-else-if="!itemActivo.resultado_pruebas">
            <p class="copy"><b>Trabajo registrado:</b> {{ itemActivo.trabajo_realizado }}</p>
            <label class="campo">Resultado de las pruebas técnicas
              <textarea v-model="formPruebas.resultado_pruebas" rows="4" placeholder="Pruebas efectuadas y comportamiento del equipo"></textarea>
            </label>
            <div class="actions">
              <button @click="itemActivo=null">Cancelar</button>
              <button class="primary" :disabled="procesando||!formPruebas.resultado_pruebas.trim()" @click="registrarPruebas">Guardar pruebas técnicas</button>
            </div>
          </template>

          <template v-else>
            <p class="copy"><b>Pruebas:</b> {{ itemActivo.resultado_pruebas }}</p>
            <label class="campo">Informe al Jefe de Mantenimiento
              <textarea v-model="formInforme.informe_trabajo" rows="4" placeholder="Trabajo realizado, componentes usados, pruebas y resultado"></textarea>
            </label>
            <label class="campo">Fotografía del trabajo
              <input type="file" accept="image/*" @change="onFotografia">
            </label>
            <div class="actions">
              <button @click="itemActivo=null">Cancelar</button>
              <button class="primary" :disabled="procesando||!formInforme.informe_trabajo.trim()" @click="registrarInforme">Enviar informe a la jefatura</button>
            </div>
          </template>
        </div>
      </section>

      <!-- =========================== HISTORIAL =========================== -->
      <section v-else-if="vista==='historial'">
        <div class="instruction"><b>Historial</b><span>Requerimientos que usted atendió.</span></div>
        <div v-if="misItems.length" class="cards">
          <article v-for="r in misItems" :key="r.id">
            <div class="top"><span>{{ r.codigo }}</span><em>{{ r.estado_codigo }}</em></div>
            <h3>{{ r.titulo }}</h3>
            <p>{{ (r.descripcion||'').slice(0,130) }}</p>
            <div class="actions"><button @click="verItem(r)">Ver detalle</button></div>
          </article>
        </div>
        <div v-else class="empty"><span>✓</span><h3>Sin registros</h3><p>Todavía no tiene requerimientos asignados.</p></div>
      </section>
    </main>

    <!-- ============================ DETALLE ============================ -->
    <div v-if="detalle" class="detalle-modal-backdrop" @click.self="detalle=null">
      <div class="detalle-modal">
        <div class="detalle-modal-header">
          <div><h3>{{ detalle.codigo }}</h3><small>{{ detalle.titulo }}</small></div>
          <button class="detalle-modal-close" @click="detalle=null">✕</button>
        </div>
        <div class="detalle-modal-body">
          <div class="detalle-fila">
            <div class="detalle-campo"><b>Estado</b><span>{{ detalle.estado_nombre || detalle.estado_codigo }}</span></div>
            <div class="detalle-campo"><b>Prioridad</b><span>{{ detalle.prioridad_jefatura || 's/d' }}</span></div>
          </div>
          <div class="detalle-campo"><b>Descripción</b><p>{{ detalle.descripcion }}</p></div>
          <div class="detalle-campo"><b>Ubicación</b><span>{{ detalle.ubicacion || 's/d' }}</span></div>
          <div class="detalle-campo" v-if="detalle.diagnostico"><b>Diagnóstico</b><p>{{ detalle.diagnostico }}</p></div>
          <div class="detalle-campo" v-if="detalle.plan_solucion"><b>Plan de solución</b><p>{{ detalle.plan_solucion }}</p></div>
          <div class="detalle-campo" v-if="detalle.producto_requerido"><b>Componente</b><p>{{ detalle.producto_requerido }} — Bs. {{ detalle.costo_estimado || 's/d' }}</p></div>
          <div class="detalle-campo" v-if="detalle.motivo_no_viable"><b>Compra no viable</b><p>{{ detalle.motivo_no_viable }}</p></div>
          <div class="detalle-campo" v-if="detalle.trabajo_realizado"><b>Trabajo realizado</b><p>{{ detalle.trabajo_realizado }}</p></div>
          <div class="detalle-campo" v-if="detalle.resultado_pruebas"><b>Pruebas técnicas</b><p>{{ detalle.resultado_pruebas }}</p></div>
          <div class="detalle-campo" v-if="detalle.informe_trabajo"><b>Informe a la jefatura</b><p>{{ detalle.informe_trabajo }}</p></div>
          <div class="detalle-campo" v-if="detalle.evidencia_archivo_url"><b>Evidencia</b><a :href="detalle.evidencia_archivo_url" target="_blank">Abrir archivo →</a></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const usuario = ref(JSON.parse(localStorage.getItem('sigta_usuario') || '{}'))
const vista = ref('resumen')
const menuAbierto = ref(false)
const items = ref([])
const cargando = ref(false)
const procesando = ref(false)
const itemActivo = ref(null)
const ordenAbierta = ref(null)
const modoComponente = ref(false)
const detalle = ref(null)

const nombre = computed(() => usuario.value.nombre || usuario.value.nombre_completo || 'Técnico de Mantenimiento')
const primerNombre = computed(() => nombre.value.split(' ')[0])
const iniciales = computed(() => nombre.value.split(' ').slice(0, 2).map(x => x[0]).join('').toUpperCase())
const saludo = computed(() => new Date().getHours() < 12 ? 'Buenos días' : new Date().getHours() < 19 ? 'Buenas tardes' : 'Buenas noches')

const misItems = computed(() => items.value.filter(r => Number(r.auxiliar_asignado) === Number(usuario.value.id)))
const enCompra = r => ['SOLICITADA', 'VIABLE'].includes(r.estado_compra_componente)

const porRecibir = computed(() => misItems.value.filter(r => r.estado_codigo === 'DERIVADO'))
const enEsperaCompra = computed(() => misItems.value.filter(r => r.estado_codigo === 'EN_ESPERA_COMPRA' || enCompra(r)))
const porReparar = computed(() => misItems.value.filter(r => r.estado_codigo === 'EN_MANTENIMIENTO' && !r.trabajo_realizado && !enCompra(r)))
const porProbar = computed(() => misItems.value.filter(r => r.estado_codigo === 'EN_MANTENIMIENTO' && !!r.trabajo_realizado && !enCompra(r)))
const enTrabajo = computed(() => [...porReparar.value, ...porProbar.value])
const conRetorno = computed(() => misItems.value.filter(r => Number(r.rework_count) > 0 && r.estado_codigo === 'EN_MANTENIMIENTO'))

const menu = computed(() => [
  { id: 'resumen', icono: '⌂', nombre: 'Resumen' },
  { id: 'ordenes', icono: 'OT', nombre: 'Órdenes de trabajo', total: porRecibir.value.length },
  { id: 'trabajo', icono: 'RP', nombre: 'Reparación y pruebas', total: enTrabajo.value.length },
  { id: 'compras', icono: 'CO', nombre: 'En espera de compra', total: enEsperaCompra.value.length },
  { id: 'historial', icono: 'HI', nombre: 'Historial' },
])

const titulo = computed(() => ({
  resumen: 'Panel del Técnico de Mantenimiento',
  ordenes: ordenAbierta.value ? 'Inspección técnica y diagnóstico' : 'Bandeja de órdenes de trabajo',
  trabajo: 'Reparación, pruebas e informe',
  compras: 'Requerimientos en espera de compra',
  historial: 'Historial de requerimientos',
}[vista.value]))

const subtitulo = computed(() => ({
  resumen: 'Diagnóstico, reparación y pruebas de los requerimientos asignados a usted.',
  ordenes: 'Requerimientos designados por la jefatura de mantenimiento.',
  trabajo: 'Intervención técnica e informe dirigido a la jefatura.',
  compras: 'Requerimientos cuyo trabajo está en pausa hasta recibir el componente.',
  historial: 'Todos los requerimientos que usted atendió.',
}[vista.value]))

function etiqueta(r) {
  if (enCompra(r)) return 'En espera de compra'
  if (!r.trabajo_realizado) return 'En reparación'
  if (!r.resultado_pruebas) return 'Por probar'
  return 'Por informar'
}

function siguientePaso(r) {
  if (!r.trabajo_realizado) return 'Registrar reparación'
  if (!r.resultado_pruebas) return 'Registrar pruebas'
  return 'Elaborar informe'
}

function fecha(valor) {
  return valor ? new Date(valor).toLocaleDateString('es-BO', { day: '2-digit', month: 'short', year: 'numeric' }) : 's/d'
}

const base = '/api/mantenimiento/requerimientos'
const token = () => localStorage.getItem('sigta_token')

async function cargar() {
  cargando.value = true
  try {
    const r = await fetch(`${base}/`, { headers: { Authorization: `Token ${token()}` } })
    const d = await r.json()
    items.value = Array.isArray(d) ? d : (d.results || [])
    if (ordenAbierta.value) ordenAbierta.value = items.value.find(x => x.id === ordenAbierta.value.id) || null
    if (itemActivo.value) itemActivo.value = items.value.find(x => x.id === itemActivo.value.id) || null
  } finally {
    cargando.value = false
  }
}

async function postAccion(item, endpoint, body, esFormData = false) {
  procesando.value = true
  try {
    const headers = { Authorization: `Token ${token()}` }
    if (!esFormData) headers['Content-Type'] = 'application/json'
    const r = await fetch(`${base}/${item.id}/${endpoint}/`, {
      method: 'POST',
      headers,
      body: esFormData ? body : JSON.stringify(body || {}),
    })
    const d = await r.json().catch(() => ({}))
    if (!r.ok) throw new Error(d.detalle || Object.values(d)[0] || 'No fue posible completar la acción.')
    await cargar()
    return d
  } finally {
    procesando.value = false
  }
}

function irA(id) {
  vista.value = id
  menuAbierto.value = false
  ordenAbierta.value = null
  itemActivo.value = null
  modoComponente.value = false
}

function verItem(item) { detalle.value = item }

function salir() {
  localStorage.removeItem('sigta_token')
  localStorage.removeItem('sigta_usuario')
  router.push('/login')
}

/* ---------- Diagnóstico y requerimiento ---------- */
const formDiagnostico = reactive({ diagnostico: '', plan_solucion: '', requiere_compra: false })
const formComponente = reactive({
  producto_requerido: '', especificacion_producto: '',
  cantidad_requerida: 1, costo_estimado: '', archivo: null,
})
const formTrabajo = reactive({ trabajo_realizado: '', observaciones_trabajo: '' })
const formPruebas = reactive({ resultado_pruebas: '' })
const formInforme = reactive({ informe_trabajo: '', fotografia: null })

function recibirOrden(item) {
  ordenAbierta.value = item
  modoComponente.value = false
  formDiagnostico.diagnostico = ''
  formDiagnostico.plan_solucion = ''
  formDiagnostico.requiere_compra = false
  formComponente.producto_requerido = ''
  formComponente.especificacion_producto = ''
  formComponente.cantidad_requerida = 1
  formComponente.costo_estimado = ''
  formComponente.archivo = null
}

function cerrarOrden() {
  ordenAbierta.value = null
  modoComponente.value = false
}

async function guardarDiagnostico() {
  try {
    await postAccion(ordenAbierta.value, 'registrar-diagnostico', {
      diagnostico: formDiagnostico.diagnostico.trim(),
      plan_solucion: formDiagnostico.plan_solucion.trim(),
    })
    if (formDiagnostico.requiere_compra) {
      modoComponente.value = true
    } else {
      cerrarOrden()
      vista.value = 'trabajo'
    }
  } catch (e) { alert(e.message) }
}

function onCotizacion(evento) {
  formComponente.archivo = evento.target.files?.[0] || null
}

async function enviarRequerimiento() {
  try {
    const datos = new FormData()
    datos.append('producto_requerido', formComponente.producto_requerido.trim())
    datos.append('especificacion_producto', formComponente.especificacion_producto.trim())
    datos.append('cantidad_requerida', String(formComponente.cantidad_requerida || 1))
    if (formComponente.costo_estimado) datos.append('costo_estimado', formComponente.costo_estimado)
    if (formComponente.archivo) datos.append('cotizacion_archivo', formComponente.archivo)
    await postAccion(ordenAbierta.value, 'solicitar-requerimiento', datos, true)
    cerrarOrden()
    vista.value = 'compras'
    alert('Requerimiento enviado a la jefatura para evaluar su viabilidad.')
  } catch (e) { alert(e.message) }
}

/* ---------- Reparación, pruebas e informe ---------- */
function abrirTrabajo(item) {
  itemActivo.value = item
  formTrabajo.trabajo_realizado = ''
  formTrabajo.observaciones_trabajo = ''
  formPruebas.resultado_pruebas = ''
  formInforme.informe_trabajo = ''
  formInforme.fotografia = null
}

async function registrarTrabajo() {
  try {
    await postAccion(itemActivo.value, 'realizar-mantenimiento', {
      trabajo_realizado: formTrabajo.trabajo_realizado.trim(),
      observaciones_trabajo: formTrabajo.observaciones_trabajo.trim(),
    })
  } catch (e) { alert(e.message) }
}

async function registrarPruebas() {
  try {
    await postAccion(itemActivo.value, 'pruebas-tecnicas', {
      resultado_pruebas: formPruebas.resultado_pruebas.trim(),
    })
  } catch (e) { alert(e.message) }
}

function onFotografia(evento) {
  formInforme.fotografia = evento.target.files?.[0] || null
}

async function registrarInforme() {
  try {
    const datos = new FormData()
    datos.append('informe_trabajo', formInforme.informe_trabajo.trim())
    if (formInforme.fotografia) datos.append('fotografia_trabajo', formInforme.fotografia)
    await postAccion(itemActivo.value, 'registrar-informe', datos, true)
    itemActivo.value = null
    alert('Informe enviado. La jefatura verificará el funcionamiento.')
  } catch (e) { alert(e.message) }
}

onMounted(cargar)
</script>

<style scoped>
*{box-sizing:border-box}.layout{min-height:100vh;background:var(--sigta-fondo);color:var(--sigta-texto);font-family:var(--sigta-fuente)}aside{position:fixed;inset:0 auto 0 0;width:var(--sigta-sidebar);background:var(--sigta-azul);color:var(--sigta-blanco);padding:22px 16px;display:flex;flex-direction:column}.brand,.profile{display:flex;align-items:center;gap:12px}.brand{padding:0 10px 20px;border-bottom:1px solid rgba(255,255,255,.2)}.brand>b{background:var(--sigta-mostaza);color:var(--sigta-azul);padding:14px 10px;border-radius:9px}.brand strong,.brand small,.profile b,.profile small{display:block}.brand strong{font-size:23px}.brand small,.profile small{color:var(--sigta-azul-texto-claro);margin-top:3px}.profile{padding:22px 10px}.profile>i{width:42px;height:42px;border-radius:50%;background:var(--sigta-mostaza);color:var(--sigta-azul);display:grid;place-items:center;font-style:normal;font-weight:900}aside>p{font-size:10px;color:var(--sigta-azul-texto-claro);font-weight:800;letter-spacing:1.4px;margin:14px 10px 8px}aside button{border:0;background:transparent;color:var(--sigta-blanco);border-radius:8px;padding:12px;display:flex;gap:11px;align-items:center;text-align:left;cursor:pointer;margin:2px 0;width:100%}aside button>span{font-size:10px;font-weight:900;width:28px}aside button em{margin-left:auto;background:rgba(255,255,255,.16);padding:2px 8px;border-radius:10px;font-style:normal}aside button.active,aside button:hover{background:rgba(255,255,255,.13)}.bottom{margin-top:auto;border-top:1px solid rgba(255,255,255,.2);padding-top:10px}.bottom button{width:100%}main{margin-left:var(--sigta-sidebar);padding:30px 38px 55px;max-width:1650px}header{display:flex;justify-content:space-between;align-items:center;margin-bottom:27px}header small{color:var(--sigta-texto-suave)}h1{font-size:var(--sigta-titulo);margin:6px 0}header p{margin:0;color:var(--sigta-texto-suave)}.refresh{border:1px solid var(--sigta-borde);background:var(--sigta-blanco);color:var(--sigta-azul);padding:10px 14px;border-radius:8px;cursor:pointer}.hero{background:linear-gradient(120deg,var(--sigta-azul),var(--sigta-azul-medio));color:var(--sigta-blanco);border-radius:13px;padding:28px 30px;display:flex;justify-content:space-between;align-items:center}.hero small,.panel-head small,.hoja-head small{font-size:10px;font-weight:800;letter-spacing:1.4px;color:var(--sigta-mostaza-clara)}.hero h2{font-size:24px;margin:7px 0}.hero p{margin:0;color:var(--sigta-azul-texto-claro)}.hero>span{width:68px;height:68px;border:1px solid var(--sigta-mostaza);border-radius:50%;display:grid;place-items:center;font-weight:900}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin:18px 0}.stats article{background:var(--sigta-blanco);border:1px solid var(--sigta-borde);border-radius:10px;padding:19px;display:flex;gap:13px;cursor:pointer}.stats i,.flow i{font-style:normal;width:37px;height:37px;border-radius:8px;display:grid;place-items:center;color:var(--sigta-blanco);font-size:10px;font-weight:900}.blue{background:var(--sigta-azul)}.gold{background:var(--sigta-mostaza);color:var(--sigta-texto)!important}.green{background:var(--sigta-azul-medio)}.navy{background:var(--sigta-azul-medio)}.stats small,.stats b,.stats p{display:block}.stats b{font-size:25px;margin:3px 0}.stats p{font-size:11px;color:var(--sigta-texto-suave);margin:0}.panels{display:grid;grid-template-columns:2fr 1fr;gap:18px}.panel{background:var(--sigta-blanco);border:1px solid var(--sigta-borde);border-radius:11px;padding:22px}.panel-head h3{margin:5px 0 14px}.flow{width:100%;border:0;border-top:1px solid var(--sigta-borde-suave);background:var(--sigta-blanco);padding:15px 2px;display:flex;gap:13px;align-items:center;text-align:left;cursor:pointer}.flow div{flex:1}.flow b,.flow small{display:block}.flow small{color:var(--sigta-texto-suave);margin-top:4px}.flow>strong{font-size:20px}.copy{color:var(--sigta-texto-suave);font-size:12px;line-height:1.7}.wide{width:100%;padding:10px;border-radius:7px;border:1px solid var(--sigta-borde);cursor:pointer}.primary{background:var(--sigta-azul)!important;color:var(--sigta-blanco)!important;border-color:var(--sigta-azul)!important}.instruction{background:var(--sigta-mostaza-suave);border-left:4px solid var(--sigta-mostaza);padding:14px 17px;margin-bottom:17px;border-radius:7px}.instruction b,.instruction span{display:block}.instruction span{font-size:12px;color:var(--sigta-alerta);margin-top:4px}.alerta{background:var(--sigta-error-fondo);border-left:4px solid var(--sigta-error);padding:14px 17px;margin:0 0 17px;border-radius:7px}.alerta b,.alerta span{display:block}.alerta b{color:var(--sigta-error)}.alerta span{font-size:12px;color:var(--sigta-error);margin-top:4px}.mini-alerta{background:var(--sigta-error-fondo);color:var(--sigta-error);font-size:11px;font-weight:700;padding:7px 9px;border-radius:6px;margin-bottom:10px}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.cards article{background:var(--sigta-blanco);border:1px solid var(--sigta-borde);border-radius:10px;padding:19px}.cards article.retorno{border-color:var(--sigta-error);box-shadow:inset 3px 0 var(--sigta-error)}.top{display:flex;justify-content:space-between;gap:8px}.top span{font-size:12px;font-weight:800;color:var(--sigta-azul)}.top em{font-size:10px;background:var(--sigta-azul-tenue);padding:4px 8px;border-radius:10px;font-style:normal;white-space:nowrap}.cards h3{font-size:17px;margin:15px 0 7px}.cards article>p{font-size:12px;color:var(--sigta-texto-suave);min-height:42px}.datos{list-style:none;margin:0 0 10px;padding:0;display:grid;gap:4px}.datos li{display:flex;justify-content:space-between;gap:10px;font-size:11px;border-bottom:1px dashed var(--sigta-borde-suave);padding-bottom:3px}.datos b{color:var(--sigta-texto-suave)}.datos span{color:var(--sigta-texto-suave);text-align:right}.adjunto{display:inline-block;font-size:11px;color:var(--sigta-azul);margin-bottom:10px;text-decoration:none}.actions{display:flex;gap:7px;border-top:1px solid var(--sigta-borde-suave);padding-top:13px;margin-top:10px}.actions button{flex:1;padding:9px 6px;border-radius:7px;border:1px solid var(--sigta-borde);background:var(--sigta-blanco);color:var(--sigta-texto);font-weight:700;cursor:pointer}.actions button:disabled{opacity:.55;cursor:not-allowed}.empty{text-align:center;background:var(--sigta-blanco);border:1px dashed var(--sigta-borde);padding:65px;border-radius:10px;color:var(--sigta-texto-suave)}.empty>span{font-size:31px;color:var(--sigta-exito)}.campo{display:block;margin:14px 0;font-size:12px;font-weight:700;color:var(--sigta-texto)}.campo input,.campo select,.campo textarea{display:block;width:100%;margin-top:6px;padding:9px 11px;border:1px solid var(--sigta-borde);border-radius:7px;font-family:inherit;font-size:13px;font-weight:400;color:var(--sigta-texto)}.hoja{max-width:820px}.hoja-head{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;margin-bottom:16px}.hoja-head h3{margin:5px 0 0}.compuerta{border:1px solid var(--sigta-borde);border-radius:8px;padding:12px 15px;margin:16px 0;display:flex;gap:22px;align-items:center}.compuerta legend{font-size:12px;font-weight:700;color:var(--sigta-texto);padding:0 6px}.compuerta label{font-size:13px;display:flex;align-items:center;gap:6px;font-weight:600}.compuerta input{margin:0}.detalle-modal-backdrop{position:fixed;inset:0;background:rgba(18,58,107,.55);display:grid;place-items:center;padding:20px;z-index:20}.detalle-modal{background:var(--sigta-blanco);border-radius:14px;width:min(700px,100%);max-height:88vh;display:flex;flex-direction:column}.detalle-modal-header{display:flex;justify-content:space-between;align-items:center;padding:20px 24px;border-bottom:1px solid var(--sigta-borde-suave)}.detalle-modal-header h3{margin:0}.detalle-modal-header small{color:var(--sigta-texto-suave)}.detalle-modal-close{border:0;background:transparent;font-size:20px;cursor:pointer;color:var(--sigta-texto-suave)}.detalle-modal-body{padding:20px 24px;overflow-y:auto;display:grid;gap:14px}.detalle-fila{display:grid;grid-template-columns:1fr 1fr;gap:14px}.detalle-campo b{display:block;font-size:11px;color:var(--sigta-texto-suave);margin-bottom:4px}.detalle-campo span,.detalle-campo p{font-size:13px;color:var(--sigta-texto);margin:0}@media(max-width:1050px){.stats{grid-template-columns:1fr 1fr}.panels{grid-template-columns:1fr}.cards{grid-template-columns:1fr 1fr}}@media(max-width:760px){aside{position:static;width:100%}main{margin:0;padding:20px}.stats,.cards{grid-template-columns:1fr}header{align-items:flex-start;flex-direction:column;gap:12px}.detalle-fila{grid-template-columns:1fr}}
</style>
