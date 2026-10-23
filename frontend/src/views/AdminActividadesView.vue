<template>
  <div class="layout">

    <AdminMenu />

    <main class="main">

      <!-- =================================================
           ENCABEZADO
      ================================================== -->
      <header class="page-header">

        <div>
          <h1>
            Actividades
          </h1>

          <p>
            Informes de actividad que las jefaturas remiten a la
            Dirección al cerrar un flujo.
          </p>
        </div>



      
        <UsuarioHeader @actualizar="cargarInformes" />
      </header>

      <p v-if="errorCarga" class="mensaje-error">
        {{ errorCarga }}
      </p>


      <!-- =================================================
           SEPARACIÓN POR JEFATURA
      ================================================== -->

      <nav class="jefatura-tabs">

        <button
          type="button"
          :class="['jefatura-tab', { activa: jefatura === 'MANTENIMIENTO' }]"
          @click="jefatura = 'MANTENIMIENTO'"
        >
          <IconoSigta class="jefatura-tab-icono" nombre="mantenimiento" :tamano="18" />
          Mantenimiento
          <span class="jefatura-tab-contador">
            {{ informesMantenimiento.length }}
          </span>
        </button>

        <button
          type="button"
          :class="['jefatura-tab', { activa: jefatura === 'UTIC' }]"
          @click="jefatura = 'UTIC'"
        >
          <IconoSigta class="jefatura-tab-icono" nombre="soporte" :tamano="18" />
          Soporte Técnico
          <span class="jefatura-tab-contador">
            {{ informesUtic.length }}
          </span>
        </button>

      </nav>


      <!-- =================================================
           LISTADO
      ================================================== -->

      <div
        v-if="cargando"
        class="empty"
      >
        Cargando informes de actividad...
      </div>

      <div
        v-else-if="informesVisibles.length === 0"
        class="empty"
      >
        No hay informes de actividad registrados.
      </div>

      <section
        v-else
        class="requests-card"
      >

        <div class="request-list">

          <article
            v-for="informe in informesVisibles"
            :key="informe.id"
            class="request"
          >

            <div class="request-main">

              <div class="request-code">
                <strong>
                  {{ informe.codigo }}
                </strong>

                <small>
                  {{ informe.periodo }}
                </small>
              </div>


              <div class="request-info">

                <h3>
                  {{ informe.titulo }}
                </h3>

                <div class="meta">
                  <span>{{ informe.jefe }}</span>
                  <span>{{ informe.origen }}</span>
                  <span>{{ informe.fecha }}</span>
                </div>

                <p class="resumen">
                  {{ informe.resumen }}
                </p>

              </div>

            </div>


            <div class="request-side">

              <span
                :class="['status', informe.leido ? 'closed' : 'working']"
              >
                {{ informe.leido ? 'Revisado' : 'Nuevo' }}
              </span>

              <div class="row-actions">

                <button
                  class="view"
                  @click="verDetalle(informe)"
                >
                  Ver detalle
                </button>

              </div>

            </div>

          </article>

        </div>

      </section>

    </main>


    <!-- =================================================
         DETALLE DEL INFORME
    ================================================== -->

    <div
      v-if="informeSeleccionado"
      class="detalle-modal-backdrop"
      @click.self="cerrarDetalle"
    >
      <div class="detalle-modal informe-modal">

        <div class="detalle-modal-header">
          <div class="informe-header-titulo">

            <IconoSigta class="informe-header-icono" nombre="auditoria" :tamano="22" />

            <div>
              <h3>{{ informeSeleccionado.codigo }}</h3>
              <small>{{ informeSeleccionado.titulo }}</small>
            </div>

          </div>

          <button
            class="detalle-modal-close"
            @click="cerrarDetalle"
          >✕</button>
        </div>

        <div class="informe-body">

          <div class="informe-cabecera">

            <div class="informe-dato">
              <b>Jefatura</b>
              <strong>{{ informeSeleccionado.jefaturaNombre }}</strong>
            </div>

            <div class="informe-dato">
              <b>Periodo</b>
              <strong>{{ informeSeleccionado.periodo }}</strong>
            </div>

            <div class="informe-dato">
              <b>{{ informeSeleccionado.leido ? 'Recibido' : 'Remitido' }}</b>
              <strong>{{ informeSeleccionado.fecha }}</strong>
            </div>

          </div>

          <dl class="ficha">

            <div>
              <dt>Remitente</dt>
              <dd>{{ informeSeleccionado.jefe }}</dd>
            </div>

            <div>
              <dt>Origen</dt>
              <dd>{{ informeSeleccionado.origen }}</dd>
            </div>

            <div>
              <dt>Estado del proceso</dt>
              <dd>{{ informeSeleccionado.estadoNombre }}</dd>
            </div>

          </dl>

          <div class="informe-seccion">

            <span class="informe-titulo">
              Contenido del informe
            </span>

            <p>{{ informeSeleccionado.contenido }}</p>

            <p v-if="informeSeleccionado.informeTecnico">
              <strong>Informe del técnico:</strong>
              {{ informeSeleccionado.informeTecnico }}
            </p>

            <section class="documentos-informe" aria-label="Documentos del expediente">
              <h4>Informes y documentos del expediente</h4>
              <p v-if="cargandoDocumentos" role="status">Consultando documentos...</p>
              <p v-if="errorDocumentos" role="alert">{{ errorDocumentos }}</p>
              <button v-if="errorDocumentos" class="btn-cerrar" @click="cargarDocumentos(informeSeleccionado)">Volver a consultar</button>
              <div class="documentos-informe-grid">
                <button v-for="archivo in archivosInforme" :key="archivo.url" type="button" class="documento-informe" @click="visualizarArchivo(archivo)">
                  <IconoSigta nombre="reporte" :tamano="22" />
                  <span><strong>{{ archivo.nombre }}</strong><small>Visualizar documento</small></span>
                </button>
              </div>
              <p v-if="!cargandoDocumentos && !archivosInforme.length">No hay documentos adjuntos disponibles.</p>
              <p v-if="errorVisor" role="alert">{{ errorVisor }}</p>
            </section>

          </div>

        </div>

        <div class="informe-acciones">

          <button
            v-if="!informeSeleccionado.leido"
            class="btn-recibir"
            type="button"
            :disabled="procesando"
            @click="confirmandoRecibir = true"
          >
            Recibir y finalizar proceso
          </button>

          <button
            class="btn-cerrar"
            type="button"
            @click="cerrarDetalle"
          >
            Cerrar
          </button>

        </div>

      </div>
    </div>


    <!-- =================================================
         CONFIRMAR RECEPCIÓN DEL INFORME
    ================================================== -->

    <div
      v-if="confirmandoRecibir"
      class="detalle-modal-backdrop confirmar-overlay"
      @click.self="!procesando && (confirmandoRecibir = false)"
    >
      <div class="confirmar-modal">

        <div class="confirmar-icono">!</div>

        <h3>¿Confirmar recepción del informe?</h3>

        <p>
          El requerimiento <strong>{{ informeSeleccionado?.codigo }}</strong>
          quedará finalizado y el solicitante verá su estado como concluido.
          Esta acción no se puede deshacer.
        </p>

        <div class="confirmar-acciones">

          <button
            type="button"
            class="btn-cerrar"
            :disabled="procesando"
            @click="confirmandoRecibir = false"
          >
            Cancelar
          </button>

          <button
            type="button"
            class="btn-recibir"
            :disabled="procesando"
            @click="recibirInforme"
          >
            {{ procesando ? 'Registrando...' : 'Sí, recibir y finalizar' }}
          </button>

        </div>

      </div>
    </div>


    <TarjetaGuardado
      :visible="mostrarGuardado"
      :texto="textoGuardado"
      :tipo="tipoGuardado"
      @cerrar="ocultarGuardado"
    />

    <div v-if="visorArchivo" class="archivo-informe-overlay" @click.self="cerrarVisor">
      <section role="dialog" aria-modal="true" :aria-label="visorArchivo.nombre">
        <header><strong>{{ visorArchivo.nombre }}</strong><button type="button" @click="cerrarVisor">Cerrar</button></header>
        <p v-if="visorArchivo.cargando" role="status">Cargando documento...</p>
        <div v-else class="archivo-informe-body">
          <img v-if="visorArchivo.imagen" :src="visorArchivo.url" :alt="visorArchivo.nombre">
          <iframe v-else-if="visorArchivo.pdf" :src="visorArchivo.url" :title="visorArchivo.nombre" />
          <p v-else>Este formato puede descargarse para consultarlo.</p>
        </div>
        <footer v-if="visorArchivo.url"><a :href="visorArchivo.url" :download="visorArchivo.nombre">Descargar documento</a></footer>
      </section>
    </div>
  </div>
</template>


<script setup>
import UsuarioHeader from '../components/UsuarioHeader.vue'

import { computed, onMounted, onUnmounted, ref } from 'vue'

import AdminMenu
  from '../components/AdminMenu.vue'

import IconoSigta
  from '../components/IconoSigta.vue'

import TarjetaGuardado
  from '../components/TarjetaGuardado.vue'

import { usarGuardado }
  from '../utils/guardado.js'


const jefatura =
  ref('MANTENIMIENTO')

const informes =
  ref([])

const cargando =
  ref(true)

const procesando =
  ref(false)

const errorCarga =
  ref('')

const {
  mostrar: mostrarGuardado,
  texto: textoGuardado,
  tipo: tipoGuardado,
  animar,
  ocultar: ocultarGuardado,
} = usarGuardado()

const informeSeleccionado =
  ref(null)

const confirmandoRecibir =
  ref(false)


const informesMantenimiento =
  computed(() =>
    informes.value.filter(
      informe => informe.jefatura === 'MANTENIMIENTO'
    )
  )


const informesUtic =
  computed(() =>
    informes.value.filter(
      informe => informe.jefatura === 'UTIC'
    )
  )


const informesVisibles =
  computed(() =>
    jefatura.value === 'MANTENIMIENTO'
      ? informesMantenimiento.value
      : informesUtic.value
  )


function token() {

  return localStorage.getItem('sigta_token')
}


function normalizarLista(datos) {

  return Array.isArray(datos)
    ? datos
    : Array.isArray(datos?.results)
      ? datos.results
      : []
}


function fechaCorta(valor) {

  if (!valor) {
    return 'Sin fecha'
  }

  return new Intl.DateTimeFormat(
    'es-BO',
    {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    }
  ).format(new Date(valor))
}


function periodoDe(valor) {

  if (!valor) {
    return 'Sin fecha'
  }

  return new Intl.DateTimeFormat(
    'es-BO',
    {
      month: 'long',
      year: 'numeric',
    }
  ).format(new Date(valor))
}


function resumenDe(texto) {

  const limpio = String(texto || '')
    .replace(/\s+/g, ' ')
    .trim()

  return limpio.length > 180
    ? `${limpio.slice(0, 177)}...`
    : limpio
}


function normalizarMantenimiento(requerimiento) {

  const fecha = requerimiento.informe_elevado_en
    || requerimiento.actualizado_en

  return {
    id: `mantenimiento-${requerimiento.id}`,
    origenId: requerimiento.id,
    jefatura: 'MANTENIMIENTO',
    jefaturaNombre: 'Jefatura de Mantenimiento',
    codigo: requerimiento.codigo,
    titulo: `Informe final · ${requerimiento.titulo || 'Mantenimiento'}`,
    periodo: periodoDe(fecha),
    fecha: fechaCorta(
      requerimiento.informe_recibido_director_en || fecha
    ),
    jefe: requerimiento.responsable_servicios_generales_nombre
      || 'Jefe de Mantenimiento',
    origen: requerimiento.codigo,
    estadoNombre: requerimiento.estado_nombre || 'Enviado a Dirección',
    resumen: resumenDe(requerimiento.informe_final),
    contenido: requerimiento.informe_final,
    informeTecnico: requerimiento.informe_trabajo,
    pdf: `/api/mantenimiento/requerimientos/${requerimiento.id}/informes-pdf/final/`,
    compraId: requerimiento.compra_vinculada?.id,
    respaldos: [
      { nombre: 'Informe del técnico de mantenimiento', url: requerimiento.informe_trabajo ? `/api/mantenimiento/requerimientos/${requerimiento.id}/informes-pdf/tecnico/` : null },
      { nombre: 'Informe de requerimiento de compra', url: requerimiento.informe_compra || requerimiento.compra_vinculada?.informe },
      { nombre: 'Cotización / proforma del técnico', url: requerimiento.cotizacion_archivo || requerimiento.compra_vinculada?.proforma },
      { nombre: 'Respaldo del trabajo técnico', url: requerimiento.fotografia_trabajo_url },
      { nombre: 'Acta de conformidad firmada', url: requerimiento.compra_vinculada?.acta_conformidad },
      { nombre: 'POA', url: requerimiento.compra_vinculada?.poa },
      { nombre: 'Proveído', url: requerimiento.compra_vinculada?.pedido },
    ].filter(archivo => archivo.url),
    leido: Boolean(requerimiento.informe_recibido_director_en),
    fechaElevado: fecha,
  }
}


function normalizarSoporte(ticket) {

  const fecha = ticket.informe_elevado_en
    || ticket.actualizado_en

  return {
    id: `utic-${ticket.id}`,
    origenId: ticket.id,
    jefatura: 'UTIC',
    jefaturaNombre: 'Jefatura de UTIC',
    codigo: ticket.codigo,
    titulo: `Informe final · ${ticket.titulo || 'Soporte técnico'}`,
    periodo: periodoDe(fecha),
    fecha: fechaCorta(ticket.informe_recibido_director_en || fecha),
    jefe: 'Jefe de UTIC',
    origen: ticket.codigo,
    estadoNombre: ticket.estado_nombre || 'Enviado a Dirección',
    resumen: resumenDe(ticket.informe_final),
    contenido: ticket.informe_final,
    informeTecnico: ticket.informe_tecnico,
    pdf: ticket.informe_final_pdf_url,
    compraId: ticket.compra_vinculada?.id,
    respaldos: [
      { nombre: 'Informe PDF generado del técnico', url: ticket.informe_tecnico_pdf_url },
      { nombre: 'Informe final del jefe de carrera', url: ticket.informe_jefe_carrera_pdf_url },
      { nombre: 'Respaldo y cuadros del técnico', url: ticket.evidencia_pruebas_url },
      { nombre: 'Evidencia del diagnóstico', url: ticket.evidencia_diagnostico_url },
      { nombre: 'Evidencia de la intervención', url: ticket.evidencia_intervencion_url },
      { nombre: 'Cotización técnica', url: ticket.cotizacion_archivo_url },
    ].filter(respaldo => respaldo.url),
    leido: Boolean(ticket.informe_recibido_director_en),
    fechaElevado: fecha,
  }
}


async function obtener(endpoint) {

  const respuesta = await fetch(endpoint, {
    headers: {
      Authorization: `Token ${token()}`,
      Accept: 'application/json',
    },
  })

  if (!respuesta.ok) {
    throw new Error(`No fue posible cargar ${endpoint}.`)
  }

  return normalizarLista(await respuesta.json())
}


async function cargarInformes() {

  cargando.value = true
  errorCarga.value = ''

  try {
    const resultados = await Promise.allSettled([
      obtener('/api/mantenimiento/requerimientos/'),
      obtener('/api/soporte/tickets/'),
    ])

    const mantenimiento = resultados[0].status === 'fulfilled'
      ? resultados[0].value
      : []

    const soporte = resultados[1].status === 'fulfilled'
      ? resultados[1].value
      : []

    informes.value = [
      ...mantenimiento
        .filter(item => item.informe_elevado_en && item.informe_final)
        .map(normalizarMantenimiento),
      ...soporte
        .filter(item => item.informe_elevado_en && item.informe_final && item.informe_final_pdf_url)
        .map(normalizarSoporte),
    ].sort(
      (a, b) => new Date(b.fechaElevado) - new Date(a.fechaElevado)
    )

    if (resultados.some(resultado => resultado.status === 'rejected')) {
      errorCarga.value =
        'No fue posible cargar todos los informes. Los disponibles se muestran a continuación.'
    }
  } catch (error) {
    console.error('No fue posible cargar las actividades.', error)
    informes.value = []
    errorCarga.value =
      'No fue posible cargar los informes de actividad. Actualice la página e intente nuevamente.'
  } finally {
    cargando.value = false
  }
}


function verDetalle(informe) {

  informeSeleccionado.value = informe
  cargarDocumentos(informe)
}


function cerrarDetalle() {
  cerrarVisor()
  documentosDetalle.value = []

  informeSeleccionado.value = null
  confirmandoRecibir.value = false
}


const documentosDetalle = ref([])
const cargandoDocumentos = ref(false)
const errorDocumentos = ref('')
const visorArchivo = ref(null)
const errorVisor = ref('')
let secuenciaVisor = 0
const archivosInforme = computed(() => {
  const informe = informeSeleccionado.value
  if (!informe) return []
  const archivos = [
    ...(informe.pdf ? [{ nombre: 'Informe final PDF', url: informe.pdf }] : []),
    ...documentosDetalle.value,
    ...(informe.respaldos || []),
  ]
  return archivos.filter((archivo, indice) => archivos.findIndex(a => a.url === archivo.url) === indice)
})
async function cargarDocumentos(informe) {
  documentosDetalle.value = []; errorDocumentos.value = ''; errorVisor.value = ''; cargandoDocumentos.value = true
  const base = informe.jefatura === 'MANTENIMIENTO' ? '/api/mantenimiento/requerimientos' : '/api/soporte/tickets'
  const consultas = [{ base: `${base}/${informe.origenId}`, actas: false }]
  if (informe.compraId) consultas.push({ base: `/api/compras/solicitudes/${informe.compraId}`, actas: false }, { base: `/api/compras/solicitudes/${informe.compraId}`, actas: true })
  const resultados = await Promise.allSettled(consultas.map(async consulta => {
    const datos = await obtener(`${consulta.base}/${consulta.actas ? 'actas-almacen' : 'documentos'}/`)
    return datos.flatMap(d => consulta.actas
      ? [{ nombre: 'Acta de entrega original', url: d.original_url }, { nombre: 'Acta de entrega firmada', url: d.firmado_url }].filter(a => a.url)
      : [{ nombre: d.tipo, url: `${consulta.base}/documentos/${d.id}/pdf/` }])
  }))
  if (informeSeleccionado.value !== informe) return
  documentosDetalle.value = resultados.flatMap(r => r.status === 'fulfilled' ? r.value : [])
  if (resultados.some(r => r.status === 'rejected')) errorDocumentos.value = 'No se pudieron consultar todos los documentos. Puede reintentar.'
  cargandoDocumentos.value = false
}
function cerrarVisor() {
  secuenciaVisor += 1
  if (visorArchivo.value?.url) URL.revokeObjectURL(visorArchivo.value.url)
  visorArchivo.value = null
}
onUnmounted(cerrarVisor)
async function visualizarArchivo(archivo) {
  cerrarVisor(); errorVisor.value = ''
  const solicitud = secuenciaVisor
  const vista = { nombre: archivo.nombre, cargando: true, url: '' }
  visorArchivo.value = vista
  try {
    const r = await fetch(archivo.url, { headers: { Authorization: `Token ${token()}` }, cache: 'no-store' })
    if (!r.ok) throw new Error('No fue posible visualizar este documento.')
    const blob = await r.blob()
    if (solicitud !== secuenciaVisor) return
    visorArchivo.value = { ...vista, cargando: false, url: URL.createObjectURL(blob), imagen: blob.type.startsWith('image/'), pdf: blob.type.includes('pdf') }
  } catch (e) {
    if (solicitud !== secuenciaVisor) return
    cerrarVisor(); errorVisor.value = e.message
  }
}

async function recibirInforme() {

  const informe = informeSeleccionado.value

  if (!informe || informe.leido) {
    return
  }

  procesando.value = true

  try {
    const endpoint = informe.jefatura === 'MANTENIMIENTO'
      ? `/api/mantenimiento/requerimientos/${informe.origenId}/recibir-informe/`
      : `/api/soporte/tickets/${informe.origenId}/recibir-informe/`

    const respuesta = await fetch(endpoint, {
      method: 'POST',
      headers: {
        Authorization: `Token ${token()}`,
        'Content-Type': 'application/json',
        Accept: 'application/json',
      },
      body: '{}',
    })

    const datos = await respuesta.json().catch(() => ({}))

    if (!respuesta.ok) {
      throw new Error(
        datos.detalle || 'No fue posible registrar la recepción del informe.'
      )
    }

    cerrarDetalle()
    await cargarInformes()
    animar(
      informe.jefatura === 'MANTENIMIENTO'
        ? 'Informe recibido. El requerimiento quedó finalizado y el solicitante ya verá su estado como concluido.'
        : 'Informe recibido. El proceso de soporte quedó finalizado.'
    )
  } catch (error) {
    console.error('No fue posible recibir el informe.', error)
    errorCarga.value = error.message
    confirmandoRecibir.value = false
  } finally {
    procesando.value = false
  }
}


onMounted(cargarInformes)

</script>


<style scoped>
.documentos-informe{margin-top:20px;padding-top:16px;border-top:1px solid #dce5ef}.documentos-informe h4{margin:0 0 14px;color:var(--sigta-azul)}.documentos-informe-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(240px,100%),1fr));gap:10px}.documento-informe{display:flex;align-items:center;gap:12px;padding:14px;border:1px solid #dce5ef;border-radius:9px;background:#f7faff;color:var(--sigta-azul);text-align:left;cursor:pointer}.documento-informe:hover{background:#edf4fc;border-color:var(--sigta-azul)}.documento-informe strong,.documento-informe small{display:block}.documento-informe small{margin-top:5px;color:#64748b}.archivo-informe-overlay{position:fixed;inset:0;z-index:1800;background:#082b4fcc;display:grid;place-items:center;padding:18px}.archivo-informe-overlay>section{width:min(1100px,96vw);max-height:95vh;background:white;border-radius:12px;overflow:auto}.archivo-informe-overlay header{display:flex;justify-content:space-between;align-items:center;gap:14px;padding:16px;background:var(--sigta-azul);color:white}.archivo-informe-overlay header button{border:1px solid #ffffff66;border-radius:7px;padding:8px 12px;background:transparent;color:white;cursor:pointer}.archivo-informe-body{height:72vh;display:grid;place-items:center;padding:12px}.archivo-informe-body iframe{width:100%;height:100%;border:0}.archivo-informe-body img{max-width:100%;max-height:100%;object-fit:contain}.archivo-informe-overlay footer{padding:12px 18px}.archivo-informe-overlay footer a{color:var(--sigta-azul)}


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
  overflow-x: hidden;
}


/* =========================================================
   HEADER
========================================================= */

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 18px;
  margin-bottom: 20px;
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


.refresh-button {
  flex-shrink: 0;
  min-height: 42px;
  padding: 0 16px;
  border: 1px solid var(--sigta-borde);
  border-radius: 8px;
  background: var(--sigta-blanco);
  color: var(--sigta-azul);
  font-family: inherit;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
}


.refresh-button:disabled {
  opacity: .65;
  cursor: not-allowed;
}


.mensaje-exito,
.mensaje-error {
  margin: 0 0 16px;
  padding: 12px 14px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 700;
}


.mensaje-exito {
  border-left: 4px solid var(--sigta-exito);
  background: var(--sigta-exito-fondo);
  color: var(--sigta-exito);
}


.mensaje-error {
  border-left: 4px solid var(--sigta-error);
  background: var(--sigta-error-fondo);
  color: var(--sigta-error);
}


/* =========================================================
   PESTAÑAS POR JEFATURA
========================================================= */

.jefatura-tabs {
  display: flex;
  gap: 4px;
  margin-bottom: 18px;
  border-bottom: 2px solid var(--sigta-azul-tenue);
}


.jefatura-tab {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 18px;
  border: none;
  border-bottom: 3px solid transparent;
  margin-bottom: -2px;
  background: transparent;
  color: var(--sigta-texto-suave);
  font-family: inherit;
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
}


.jefatura-tab:hover {
  color: var(--sigta-azul-oscuro);
}


.jefatura-tab.activa {
  color: var(--sigta-azul-oscuro);
  border-bottom-color: var(--sigta-mostaza);
}


.jefatura-tab-icono {
  flex-shrink: 0;
}


.jefatura-tab-contador {
  padding: 1px 8px;
  border-radius: 10px;
  background: var(--sigta-azul-tenue);
  color: var(--sigta-texto-suave);
  font-size: 12px;
}


.jefatura-tab.activa .jefatura-tab-contador {
  background: var(--sigta-mostaza);
  color: var(--sigta-azul-oscuro);
}


/* =========================================================
   LISTADO
========================================================= */

.requests-card {
  overflow: hidden;
  border-radius: 10px;
  background: white;
  box-shadow: 0 4px 14px rgba(0,0,0,.05);
}


.request-list {
  display: flex;
  flex-direction: column;
}


.request {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  padding: 17px 20px;
  border-bottom: 1px solid var(--sigta-azul-tenue);
}


.request:last-child {
  border-bottom: none;
}


.request-main {
  flex: 1;
  min-width: 0;
  display: grid;
  grid-template-columns: 175px 1fr;
  gap: 15px;
}


.request-code strong {
  display: block;
  color: var(--sigta-azul);
  font-size: 15px;
}


.request-code small {
  display: block;
  margin-top: 4px;
  color: var(--sigta-texto-suave);
  font-size: 13px;
}


.request-info h3 {
  margin: 0 0 5px;
  color: var(--sigta-azul);
  font-size: 18px;
}


.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}


.meta span {
  padding: 4px 6px;
  border-radius: 4px;
  background: var(--sigta-azul-tenue);
  color: var(--sigta-texto-suave);
  font-size: 13px;
}


.resumen {
  margin: 7px 0 0;
  color: var(--sigta-texto-suave);
  font-size: 14px;
  line-height: 1.45;
}


.request-side {
  flex-shrink: 0;
  display: flex;
  align-items: flex-end;
  flex-direction: column;
  gap: 9px;
}


/* =========================================================
   ESTADO
========================================================= */

.status {
  display: inline-block;
  padding: 5px 8px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 800;
}


.status.working {
  background: var(--sigta-mostaza-suave);
  color: var(--sigta-mostaza-oscuro);
}


.status.closed {
  background: var(--sigta-exito-fondo);
  color: var(--sigta-exito);
}


.row-actions {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 6px;
}


.view {
  padding: 6px 8px;
  border: none;
  border-radius: 5px;
  background: var(--sigta-azul-tenue);
  color: var(--sigta-texto-suave);
  font-family: inherit;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
}


.empty {
  padding: 34px;
  border-radius: 10px;
  background: white;
  box-shadow: 0 4px 14px rgba(0,0,0,.05);
  color: var(--sigta-texto-suave);
  font-size: 16px;
  text-align: center;
}


/* =========================================================
   DETALLE DEL INFORME
========================================================= */

.informe-modal {
  max-width: 720px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}


.informe-header-titulo {
  display: flex;
  align-items: center;
  gap: 12px;
}


.informe-header-icono {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 38px;
  height: 38px;
  border-radius: 10px;
  background: var(--sigta-mostaza-suave);
}


.informe-body {
  flex: 1;
  min-height: 0;
  padding: 16px 22px 18px;
  overflow-y: auto;
}


.informe-cabecera {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 12px;
  margin-bottom: 14px;
  padding: 12px 14px;
  border-radius: 10px;
  background: var(--sigta-azul-tenue);
  border-left: 5px solid var(--sigta-mostaza);
}


.informe-dato b {
  display: block;
  margin-bottom: 4px;
  color: var(--sigta-texto-suave);
  font-size: 11px;
  font-weight: 700;
  letter-spacing: .6px;
  text-transform: uppercase;
}


.informe-dato strong {
  display: block;
  color: var(--sigta-azul-oscuro);
  font-size: 16px;
}


.ficha {
  margin: 0 0 14px;
}


.ficha > div {
  display: grid;
  grid-template-columns: 116px 1fr;
  gap: 14px;
  align-items: baseline;
  padding: 7px 0;
  border-top: 1px solid var(--sigta-azul-tenue);
}


.ficha > div:first-child {
  border-top: none;
}


.ficha dt {
  color: var(--sigta-texto-suave);
  font-size: 13px;
  font-weight: 700;
}


.ficha dd {
  margin: 0;
  color: var(--sigta-texto);
  font-size: 15px;
  line-height: 1.45;
}


.informe-seccion {
  padding-top: 14px;
  border-top: 1px solid var(--sigta-azul-tenue);
}


.informe-titulo {
  display: block;
  margin-bottom: 8px;
  color: var(--sigta-texto-suave);
  font-size: 13px;
  font-weight: 800;
  letter-spacing: .6px;
  text-transform: uppercase;
}


.informe-seccion p {
  margin: 0;
  color: var(--sigta-texto);
  font-size: 15px;
  line-height: 1.6;
  white-space: pre-wrap;
}


.informe-acciones {
  flex-shrink: 0;
  display: flex;
  justify-content: flex-end;
  padding: 12px 22px;
  border-top: 1px solid var(--sigta-azul-tenue);
  background: var(--sigta-blanco);
  border-radius: 0 0 14px 14px;
}


.btn-cerrar {
  min-height: 40px;
  padding: 0 20px;
  border: none;
  border-radius: 7px;
  background: var(--sigta-azul-tenue);
  color: var(--sigta-texto-suave);
  font-family: inherit;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
}


.btn-recibir {
  min-height: 40px;
  margin-right: 8px;
  padding: 0 18px;
  border: none;
  border-radius: 7px;
  background: var(--sigta-exito);
  color: var(--sigta-blanco);
  font-family: inherit;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
}


.btn-recibir:disabled {
  opacity: .65;
  cursor: not-allowed;
}


/* =========================================================
   CONFIRMAR RECEPCIÓN
========================================================= */

.confirmar-overlay {
  z-index: 210;
}


.confirmar-modal {
  width: min(420px, 100%);
  padding: 28px 26px;
  border-radius: 14px;
  background: var(--sigta-blanco);
  text-align: center;
}


.confirmar-icono {
  width: 46px;
  height: 46px;
  margin: 0 auto 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--sigta-mostaza-suave);
  color: var(--sigta-mostaza-oscuro);
  font-size: 22px;
  font-weight: 900;
}


.confirmar-modal h3 {
  margin: 0 0 10px;
  color: var(--sigta-texto);
  font-size: 18px;
}


.confirmar-modal p {
  margin: 0 0 22px;
  color: var(--sigta-texto-suave);
  font-size: 14px;
  line-height: 1.5;
}


.confirmar-acciones {
  display: flex;
  justify-content: center;
  gap: 10px;
}


.confirmar-acciones .btn-recibir {
  margin-right: 0;
}


/* =========================================================
   RESPONSIVE
========================================================= */

@media (max-width: 760px) {

  .layout {
    display: block;
  }


  .main {
    padding: 16px;
  }


  .request {
    flex-direction: column;
    align-items: flex-start;
  }


  .request-main {
    grid-template-columns: 1fr;
  }


  .request-side {
    align-items: flex-start;
  }


  .informe-cabecera {
    grid-template-columns: 1fr;
  }

}

</style>
