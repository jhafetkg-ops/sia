<template>
  <div class="layout sigta-role-layout">
    <aside :class="{ abierto: menuAbierto }">
      <div class="brand-row">
        <div class="brand"><b><img src="/img/emi.jpg" alt="EMI"></b><div><strong>SIGTA</strong><small>Compras y Almacén</small></div></div>
        <button type="button" class="menu-toggle" :aria-expanded="menuAbierto" aria-label="Mostrar opciones del menú" @click="menuAbierto = !menuAbierto"><span></span><span></span><span></span></button>
      </div>
      <div class="profile"><i>{{ iniciales }}</i><div><b>{{ nombre }}</b><small>Encargado de Compras y Almacén</small></div></div>
      <p>CAJA CHICA</p>
      <button v-for="m in menu" :key="m.id" :class="{active:vista===m.id}" @click="irA(m.id)"><span>{{ m.icono }}</span>{{ m.nombre }}<em v-if="m.total!==undefined">{{ m.total }}</em></button>
      <div class="bottom"><button @click="salir"><span>↪</span>Cerrar sesión</button></div>
    </aside>

    <main>
      <header>
        <div><small>SIGTA / COMPRAS / {{ titulo }}</small><h1>{{ titulo }}</h1><p>{{ subtitulo }}</p></div>
        <button class="refresh" :disabled="cargando" @click="cargar">↻ Actualizar</button>
      </header>

      <!-- ============================ RESUMEN ============================ -->
      <section v-if="vista==='resumen'">
        <div class="hero">
          <div><small>COMPRAS Y ALMACÉN</small><h2>{{ saludo }}, {{ primerNombre }}</h2><p>Adquisición, control de almacén y entrega de los bienes.</p></div>
          <span>CA</span>
        </div>

        <div class="stats">
          <article @click="irA('comprar')"><i class="gold">CO</i><div><small>Por comprar</small><b>{{ porComprar.length }}</b><p>fondos desembolsados</p></div></article>
          <article @click="irA('entrada')"><i class="blue">EN</i><div><small>Por registrar entrada</small><b>{{ porIngresar.length }}</b><p>producto adquirido</p></div></article>
          <article @click="irA('salida')"><i class="blue">SA</i><div><small>Por registrar salida</small><b>{{ porDespachar.length }}</b><p>en almacén</p></div></article>
          <article @click="irA('entrega')"><i class="green">EG</i><div><small>Por entregar</small><b>{{ porEntregar.length }}</b><p>con acta de conformidad</p></div></article>
        </div>

        <div class="panels">
          <section class="panel">
            <div class="panel-head"><div><h3>Sus cuatro tareas del proceso</h3></div></div>
            <button class="flow" @click="irA('comprar')"><i class="gold">1</i><div><b>Realizar compra</b><small>Adquirir el bien y respaldarlo con la factura o recibo</small></div><strong>›</strong></button>
            <button class="flow" @click="irA('entrada')"><i class="blue">2</i><div><b>Registrar entrada de almacén</b><small>Cuántas unidades llegaron y quién las recibió</small></div><strong>›</strong></button>
            <button class="flow" @click="irA('salida')"><i class="blue">3</i><div><b>Registrar salida de almacén</b><small>Qué sale, cuándo y para quién</small></div><strong>›</strong></button>
            <button class="flow" @click="irA('entrega')"><i class="green">4</i><div><b>Entregar la solicitud con acta de conformidad</b><small>Entrega formal al área solicitante</small></div><strong>›</strong></button>
          </section>
          <section class="panel">
            <div class="panel-head"><div><small>SU FUNCIÓN</small><h3>Ejecutar y controlar</h3></div></div>
            <p class="copy">Usted no autoriza la compra ni desembolsa el dinero: eso corresponde al Director y a Tesorería. Su trabajo empieza cuando ya hay autorización y fondos, y consiste en que el bien pase correctamente por <b>adquisición → control en almacén → entrega</b>.</p>
            <button class="wide primary" @click="irA('historial')">Ver historial de movimientos →</button>
          </section>
        </div>
      </section>

      <!-- ========================= 1. REALIZAR COMPRA ========================= -->
      <section v-else-if="vista==='comprar'">
        <div class="instruction"><b>Realizar compra</b><span>Adquiera el bien y registre el monto real, el proveedor y la factura que respalda la compra.</span></div>

        <div v-if="cargando" class="empty">Consultando expedientes…</div>

        <div v-else-if="!activo" class="cards">
          <article v-for="e in porComprar" :key="e.id">
            <div class="top"><span>{{ e.codigo }}</span><em>fondos entregados</em></div>
            <h3>{{ e.titulo }}</h3>
            <ul class="datos">
              <li><b>Cantidad</b><span>{{ e.cantidad }}</span></li>
              <li><b>Desembolsado</b><span>Bs {{ e.monto_desembolsado || 's/d' }}</span></li>
              <li><b>Entregó Tesorería a</b><span>{{ e.responsable_adquisicion || 's/d' }}</span></li>
            </ul>

            <p class="situacion" :class="{ aviso: !e.fondos_recibidos_en }">
              {{ e.situacion }}
            </p>

            <div class="actions">
              <button @click="verDetalle(e)">Ver expediente</button>
              <button
                v-if="!e.fondos_recibidos_en"
                class="primary"
                @click="confirmarFondos(e)"
              >
                Recibí el efectivo
              </button>
              <template v-else>
                <button @click="abrirGestion(e)">Informar avance</button>
                <button class="primary" @click="abrir(e)">Registrar compra</button>
              </template>
            </div>
          </article>
          <div v-if="!porComprar.length" class="empty">
            <span>✓</span><h3>Sin compras pendientes</h3>
            <p>Los expedientes llegan aquí cuando Tesorería desembolsa los fondos.</p>
          </div>
        </div>

        <div v-else-if="modoGestion" class="panel hoja">
          <div class="hoja-head">
            <div><small>INFORMAR AVANCE</small><h3>{{ activo.codigo }} — {{ activo.titulo }}</h3></div>
            <button class="refresh" @click="cerrar">Volver</button>
          </div>

          <p class="copy">Deje constancia de en qué punto va la gestión. El resto de las áreas verá este avance en el expediente, sin tener que preguntar.</p>

          <label class="campo">¿En qué está?
            <select v-model="formGestion.gestion_estado">
              <option value="BUSCANDO">Buscando producto o proveedor</option>
              <option value="COMPRANDO">Compra en curso</option>
            </select>
          </label>
          <label class="campo">Detalle
            <input v-model="formGestion.gestion_nota" type="text" placeholder="Ej.: cotizando en tres proveedores">
          </label>

          <p v-if="error" class="error-linea">{{ error }}</p>

          <div class="actions">
            <button @click="cerrar">Cancelar</button>
            <button class="primary" :disabled="procesando" @click="informarAvance">Guardar avance</button>
          </div>
        </div>

        <div v-else class="panel hoja">
          <div class="hoja-head">
            <div><small>REALIZAR COMPRA</small><h3>{{ activo.codigo }} — {{ activo.titulo }}</h3></div>
            <button class="refresh" @click="cerrar">Volver</button>
          </div>
          <p class="copy"><b>Solicitado:</b> {{ activo.cantidad }} unidad(es) · {{ activo.especificaciones || 's/d' }}<br><b>Monto desembolsado:</b> Bs {{ activo.monto_desembolsado || 's/d' }}<br><b>Efectivo recibido por:</b> {{ activo.fondos_recibidos_por }} el {{ fecha(activo.fondos_recibidos_en) }}</p>

          <label class="campo">Monto real cobrado (Bs)
            <input v-model="formCompra.monto_real" type="number" min="0" step="0.01" placeholder="0.00">
          </label>
          <label class="campo">Proveedor
            <input v-model="formCompra.proveedor" type="text" placeholder="Nombre o razón social">
          </label>
          <label class="campo">Factura o recibo de la compra
            <input type="file" accept="application/pdf,image/*" @change="onComprobante">
          </label>
          <label class="campo">Verificación del producto
            <input v-model="formCompra.observacion_verificacion" type="text" placeholder="El producto corresponde a lo solicitado...">
          </label>

          <p v-if="error" class="error-linea">{{ error }}</p>

          <div class="actions">
            <button @click="cerrar">Cancelar</button>
            <button class="primary" :disabled="procesando||!formCompra.monto_real||!formCompra.proveedor.trim()||!comprobante" @click="registrarCompra">Registrar compra</button>
          </div>
        </div>
      </section>

      <!-- ======================= 2. ENTRADA DE ALMACÉN ======================= -->
      <section v-else-if="vista==='entrada'">
        <div class="instruction"><b>Registrar entrada de almacén</b><span>Deje constancia de cuántas unidades ingresaron y quién las recibió.</span></div>

        <div v-if="!activo" class="cards">
          <article v-for="e in porIngresar" :key="e.id">
            <div class="top"><span>{{ e.codigo }}</span><em>comprado</em></div>
            <h3>{{ e.titulo }}</h3>
            <ul class="datos">
              <li><b>Solicitadas</b><span>{{ e.cantidad }}</span></li>
              <li><b>Proveedor</b><span>{{ e.proveedor || 's/d' }}</span></li>
              <li><b>Monto real</b><span>Bs {{ e.monto_real || 's/d' }}</span></li>
            </ul>
            <div class="actions">
              <button @click="verDetalle(e)">Ver expediente</button>
              <button class="primary" @click="abrir(e)">Registrar entrada</button>
            </div>
          </article>
          <div v-if="!porIngresar.length" class="empty"><span>✓</span><h3>Sin ingresos pendientes</h3><p>Aquí aparecen los productos ya comprados.</p></div>
        </div>

        <div v-else class="panel hoja">
          <div class="hoja-head">
            <div><small>ENTRADA DE ALMACÉN</small><h3>{{ activo.codigo }} — {{ activo.titulo }}</h3></div>
            <button class="refresh" @click="cerrar">Volver</button>
          </div>
          <p class="copy"><b>Solicitadas:</b> {{ activo.cantidad }} unidad(es) · <b>Proveedor:</b> {{ activo.proveedor }}</p>

          <label class="campo">Cantidad recibida
            <input v-model="formIngreso.cantidad_recibida" type="number" min="1" :max="activo.cantidad" :placeholder="`Máximo ${activo.cantidad}`">
          </label>
          <label class="campo">Recibido por
            <input v-model="formIngreso.responsable_recepcion" type="text" placeholder="Nombre de quien recibe en almacén">
          </label>
          <label class="campo">Observación del ingreso
            <input v-model="formIngreso.observacion_ingreso" type="text" placeholder="Estado del producto, embalaje...">
          </label>

          <p v-if="error" class="error-linea">{{ error }}</p>

          <div class="actions">
            <button @click="cerrar">Cancelar</button>
            <button class="primary" :disabled="procesando||!formIngreso.cantidad_recibida||!formIngreso.responsable_recepcion.trim()" @click="registrarEntrada">Registrar entrada</button>
          </div>
        </div>
      </section>

      <!-- ======================== 3. SALIDA DE ALMACÉN ======================== -->
      <section v-else-if="vista==='salida'">
        <div class="instruction"><b>Registrar salida de almacén</b><span>Registre qué cantidad sale del almacén y a quién se entrega.</span></div>

        <div v-if="!activo" class="cards">
          <article v-for="e in porDespachar" :key="e.id">
            <div class="top"><span>{{ e.codigo }}</span><em>en almacén</em></div>
            <h3>{{ e.titulo }}</h3>
            <ul class="datos">
              <li><b>En almacén</b><span>{{ e.cantidad_recibida }} unid.</span></li>
              <li><b>Recibió</b><span>{{ e.responsable_recepcion || 's/d' }}</span></li>
              <li><b>Ingresó</b><span>{{ fecha(e.fecha_ingreso_almacen) }}</span></li>
            </ul>
            <div class="actions">
              <button @click="verDetalle(e)">Ver expediente</button>
              <button class="primary" @click="abrir(e)">Registrar salida</button>
            </div>
          </article>
          <div v-if="!porDespachar.length" class="empty"><span>✓</span><h3>Sin salidas pendientes</h3><p>Aquí aparecen los productos que ya ingresaron a almacén.</p></div>
        </div>

        <div v-else class="panel hoja">
          <div class="hoja-head">
            <div><small>SALIDA DE ALMACÉN</small><h3>{{ activo.codigo }} — {{ activo.titulo }}</h3></div>
            <button class="refresh" @click="cerrar">Volver</button>
          </div>
          <p class="copy"><b>Disponible en almacén:</b> {{ activo.cantidad_recibida }} unidad(es), recibidas por {{ activo.responsable_recepcion }}</p>

          <label class="campo">Cantidad que sale
            <input v-model="formSalida.cantidad_entregada" type="number" min="1" :max="activo.cantidad_recibida" :placeholder="`Máximo ${activo.cantidad_recibida}`">
          </label>
          <label class="campo">Entregado a
            <input v-model="formSalida.entregado_a" type="text" placeholder="Nombre de quien retira el producto">
          </label>
          <label class="campo">Observación de la salida
            <input v-model="formSalida.observacion_salida" type="text" placeholder="Detalle adicional...">
          </label>

          <p v-if="error" class="error-linea">{{ error }}</p>

          <div class="actions">
            <button @click="cerrar">Cancelar</button>
            <button class="primary" :disabled="procesando||!formSalida.cantidad_entregada||!formSalida.entregado_a.trim()" @click="registrarSalida">Registrar salida</button>
          </div>
        </div>
      </section>

      <!-- ===================== 4. ENTREGA CON ACTA ===================== -->
      <section v-else-if="vista==='entrega'">
        <div class="instruction"><b>Entregar la solicitud con acta de conformidad</b><span>Entregue el bien al área solicitante adjuntando el acta que respalda la entrega.</span></div>

        <div v-if="!activo" class="cards">
          <article v-for="e in porEntregar" :key="e.id">
            <div class="top"><span>{{ e.codigo }}</span><em>salida registrada</em></div>
            <h3>{{ e.titulo }}</h3>
            <ul class="datos">
              <li><b>Salieron</b><span>{{ e.cantidad_entregada }} unid.</span></li>
              <li><b>Destino</b><span>{{ e.entregado_a || 's/d' }}</span></li>
              <li><b>Solicitante</b><span>{{ e.solicitante_nombre || 's/d' }}</span></li>
            </ul>
            <div class="actions">
              <button @click="verDetalle(e)">Ver expediente</button>
              <button class="primary" @click="abrir(e)">Entregar con acta</button>
            </div>
          </article>
          <div v-if="!porEntregar.length" class="empty"><span>✓</span><h3>Sin entregas pendientes</h3><p>Aquí aparecen los productos cuya salida ya fue registrada.</p></div>
        </div>

        <div v-else class="panel hoja">
          <div class="hoja-head">
            <div><small>ENTREGA CON ACTA</small><h3>{{ activo.codigo }} — {{ activo.titulo }}</h3></div>
            <button class="refresh" @click="cerrar">Volver</button>
          </div>
          <p class="copy"><b>Salieron:</b> {{ activo.cantidad_entregada }} unidad(es) con destino a {{ activo.entregado_a }}<br>Tras la entrega, el solicitante firmará el acta y recibirá formalmente la solicitud.</p>

          <label class="campo">Acta de conformidad
            <input type="file" accept="application/pdf,image/*" @change="onActa">
          </label>

          <p v-if="error" class="error-linea">{{ error }}</p>

          <div class="actions">
            <button @click="cerrar">Cancelar</button>
            <button class="primary" :disabled="procesando||!acta" @click="entregarConActa">Entregar con acta de conformidad</button>
          </div>
        </div>
      </section>

      <!-- =========================== HISTORIAL =========================== -->
      <section v-else-if="vista==='historial'">
        <div class="instruction"><b>Historial de movimientos</b><span>Expedientes que ya pasaron por almacén.</span></div>
        <div v-if="historial.length" class="cards">
          <article v-for="e in historial" :key="e.id">
            <div class="top"><span>{{ e.codigo }}</span><em>{{ etiquetaEstado(e.estado) }}</em></div>
            <h3>{{ e.titulo }}</h3>
            <ul class="datos">
              <li v-if="e.cantidad_recibida"><b>Entrada</b><span>{{ e.cantidad_recibida }} unid. · {{ fecha(e.fecha_ingreso_almacen) }}</span></li>
              <li v-if="e.cantidad_entregada"><b>Salida</b><span>{{ e.cantidad_entregada }} unid. · {{ fecha(e.fecha_despacho_almacen) }}</span></li>
              <li v-if="e.entregado_a"><b>Destino</b><span>{{ e.entregado_a }}</span></li>
            </ul>
            <div class="actions"><button @click="verDetalle(e)">Ver expediente</button></div>
          </article>
        </div>
        <div v-else class="empty"><span>✓</span><h3>Sin movimientos</h3><p>Todavía no registró compras ni movimientos de almacén.</p></div>
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
            <div class="detalle-campo"><b>Estado</b><span>{{ etiquetaEstado(detalle.estado) }}</span></div>
            <div class="detalle-campo"><b>Cantidad solicitada</b><span>{{ detalle.cantidad }}</span></div>
          </div>
          <div class="detalle-campo"><b>Descripción</b><p>{{ detalle.descripcion }}</p></div>
          <div class="detalle-campo"><b>Especificaciones</b><p>{{ detalle.especificaciones || 's/d' }}</p></div>
          <div class="detalle-fila">
            <div class="detalle-campo"><b>Solicitante</b><span>{{ detalle.solicitante_nombre }}</span></div>
            <div class="detalle-campo"><b>Área</b><span>{{ detalle.area_nombre || 's/d' }}</span></div>
          </div>
          <div class="detalle-campo" v-if="detalle.monto_desembolsado"><b>Desembolso</b><span>Bs {{ detalle.monto_desembolsado }} — recibió {{ detalle.responsable_adquisicion }}</span></div>
          <div class="detalle-campo" v-if="detalle.monto_real"><b>Compra</b><span>Bs {{ detalle.monto_real }} a {{ detalle.proveedor }}</span></div>
          <div class="detalle-campo" v-if="detalle.cantidad_recibida"><b>Entrada de almacén</b><span>{{ detalle.cantidad_recibida }} unid. recibidas por {{ detalle.responsable_recepcion }} el {{ fecha(detalle.fecha_ingreso_almacen) }}</span></div>
          <div class="detalle-campo" v-if="detalle.cantidad_entregada"><b>Salida de almacén</b><span>{{ detalle.cantidad_entregada }} unid. a {{ detalle.entregado_a }} el {{ fecha(detalle.fecha_despacho_almacen) }}</span></div>
          <div class="detalle-campo"><b>Documentos</b>
            <p class="documentos">
              <a v-if="detalle.informe" :href="detalle.informe" target="_blank">Informe</a>
              <a v-if="detalle.proforma" :href="detalle.proforma" target="_blank">Proforma</a>
              <a v-if="detalle.poa" :href="detalle.poa" target="_blank">POA</a>
              <a v-if="detalle.certificacion_presupuestaria" :href="detalle.certificacion_presupuestaria" target="_blank">Certificación</a>
              <a v-if="detalle.comprobante_compra" :href="detalle.comprobante_compra" target="_blank">Factura</a>
              <a v-if="detalle.acta_conformidad" :href="detalle.acta_conformidad" target="_blank">Acta</a>
            </p>
          </div>
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
const expedientes = ref([])
const cargando = ref(false)
const procesando = ref(false)
const activo = ref(null)
const detalle = ref(null)
const error = ref('')
const comprobante = ref(null)
const acta = ref(null)

const nombre = computed(() => usuario.value.nombre || usuario.value.nombre_completo || 'Compras y Almacén')
const primerNombre = computed(() => nombre.value.split(' ')[0])
const iniciales = computed(() => nombre.value.split(' ').slice(0, 2).map(x => x[0]).join('').toUpperCase())
const saludo = computed(() => new Date().getHours() < 12 ? 'Buenos días' : new Date().getHours() < 19 ? 'Buenas tardes' : 'Buenas noches')

/* Las cuatro tareas del BPMN, cada una con su bandeja. */
const porComprar = computed(() => expedientes.value.filter(e => e.estado === 'FONDOS_DESEMBOLSADOS'))
const porIngresar = computed(() => expedientes.value.filter(e => e.estado === 'COMPRA_REGISTRADA' && !e.fecha_ingreso_almacen))
const porDespachar = computed(() => expedientes.value.filter(e => e.estado === 'COMPRA_REGISTRADA' && e.fecha_ingreso_almacen && !e.fecha_despacho_almacen))
const porEntregar = computed(() => expedientes.value.filter(e => e.estado === 'COMPRA_REGISTRADA' && e.fecha_despacho_almacen))
const historial = computed(() => expedientes.value.filter(e => e.fecha_ingreso_almacen || e.monto_real))

const menu = computed(() => [
  { id: 'resumen', icono: '⌂', nombre: 'Dashboard' },
  { id: 'comprar', icono: 'CO', nombre: 'Realizar compra', total: porComprar.value.length },
  { id: 'entrada', icono: 'EN', nombre: 'Entrada de almacén', total: porIngresar.value.length },
  { id: 'salida', icono: 'SA', nombre: 'Salida de almacén', total: porDespachar.value.length },
  { id: 'entrega', icono: 'EG', nombre: 'Entregar con acta', total: porEntregar.value.length },
  { id: 'historial', icono: 'HI', nombre: 'Historial' },
])

const titulo = computed(() => ({
  resumen: 'Dashboard de Compras y Almacén',
  comprar: 'Realizar compra',
  entrada: 'Registrar entrada de almacén',
  salida: 'Registrar salida de almacén',
  entrega: 'Entregar con acta de conformidad',
  historial: 'Historial de movimientos',
}[vista.value]))

const subtitulo = computed(() => ({
  resumen: 'Adquisición, control en almacén y entrega de los bienes de Caja Chica.',
  comprar: 'Expedientes con fondos ya desembolsados por Tesorería.',
  entrada: 'Productos comprados que deben ingresar formalmente a almacén.',
  salida: 'Productos en almacén listos para salir hacia el área solicitante.',
  entrega: 'Productos que salieron de almacén y deben entregarse con acta.',
  historial: 'Todos los movimientos que usted registró.',
}[vista.value]))

const ETIQUETAS = {
  CREADO_PENDIENTE_DAF: 'Esperando revisión de la DAF',
  EVALUADO_PENDIENTE_CERTIFICACION: 'Esperando certificación de la DAF',
  VERIFICADO_PENDIENTE_AUTORIZACION: 'Esperando autorización del Director',
  APROBADO_PARA_DESEMBOLSO: 'Esperando desembolso de Tesorería',
  FONDOS_DESEMBOLSADOS: 'Fondos entregados — por comprar',
  COMPRA_REGISTRADA: 'Compra realizada',
  COMPRADO_Y_ENTREGADO: 'Entregado al solicitante',
  DESCARGO_PENDIENTE_LIQUIDACION: 'Acta firmada',
  CERRADO_ARCHIVADO: 'Cerrado y archivado',
  RECHAZADO: 'Rechazado',
  ANULADO: 'Anulado',
}

function etiquetaEstado(estado) { return ETIQUETAS[estado] || estado }

function fecha(valor) {
  return valor ? new Date(valor).toLocaleDateString('es-BO', { day: '2-digit', month: 'short', year: 'numeric' }) : 's/d'
}

const token = () => localStorage.getItem('sigta_token')

async function cargar() {
  cargando.value = true
  try {
    const r = await fetch('/api/compras/solicitudes/', { headers: { Authorization: `Token ${token()}` } })
    const d = await r.json()
    expedientes.value = Array.isArray(d) ? d : (d.results || [])
    if (activo.value) activo.value = expedientes.value.find(e => e.id === activo.value.id) || null
  } finally {
    cargando.value = false
  }
}

function irA(id) {
  vista.value = id
  menuAbierto.value = false
  cerrar()
}

function abrir(e) {
  activo.value = e
  modoGestion.value = false
  error.value = ''
  comprobante.value = null
  acta.value = null
  formCompra.monto_real = e.monto_desembolsado || ''
  formCompra.proveedor = ''
  formCompra.observacion_verificacion = ''
  formIngreso.cantidad_recibida = e.cantidad || 1
  formIngreso.responsable_recepcion = ''
  formIngreso.observacion_ingreso = ''
  formSalida.cantidad_entregada = e.cantidad_recibida || 1
  formSalida.entregado_a = ''
  formSalida.observacion_salida = ''
}

function cerrar() {
  activo.value = null
  modoGestion.value = false
  error.value = ''
}

function verDetalle(e) { detalle.value = e }

function salir() {
  localStorage.removeItem('sigta_token')
  localStorage.removeItem('sigta_usuario')
  router.push('/login')
}

async function accion(endpoint, cuerpo, esFormData = false) {
  error.value = ''
  procesando.value = true
  try {
    const headers = { Authorization: `Token ${token()}` }
    if (!esFormData) headers['Content-Type'] = 'application/json'
    const r = await fetch(`/api/compras/solicitudes/${activo.value.id}/${endpoint}/`, {
      method: 'POST',
      headers,
      body: esFormData ? cuerpo : JSON.stringify(cuerpo),
    })
    const d = await r.json().catch(() => ({}))
    if (!r.ok) throw new Error(d.detalle || Object.values(d)[0] || 'No fue posible completar la acción.')
    await cargar()
    cerrar()
    return d
  } catch (e) {
    error.value = e.message
  } finally {
    procesando.value = false
  }
}

/* --------- 0. Coordinación con Tesorería --------- */
const modoGestion = ref(false)
const formGestion = reactive({ gestion_estado: 'BUSCANDO', gestion_nota: '' })

async function confirmarFondos(e) {
  activo.value = e
  await accion('confirmar-recepcion-fondos', {})
}

function abrirGestion(e) {
  activo.value = e
  modoGestion.value = true
  error.value = ''
  formGestion.gestion_estado = e.gestion_estado || 'BUSCANDO'
  formGestion.gestion_nota = e.gestion_nota || ''
}

async function informarAvance() {
  await accion('actualizar-gestion', {
    gestion_estado: formGestion.gestion_estado,
    gestion_nota: formGestion.gestion_nota.trim(),
  })
}


/* --------- 1. Realizar compra --------- */
const formCompra = reactive({ monto_real: '', proveedor: '', observacion_verificacion: '' })

function onComprobante(evento) { comprobante.value = evento.target.files?.[0] || null }

async function registrarCompra() {
  const datos = new FormData()
  datos.append('monto_real', formCompra.monto_real)
  datos.append('proveedor', formCompra.proveedor.trim())
  datos.append('componente_verificado', 'true')
  datos.append('observacion_verificacion', formCompra.observacion_verificacion.trim())
  datos.append('comprobante_compra', comprobante.value)
  await accion('registrar-compra', datos, true)
}

/* --------- 2. Entrada de almacén --------- */
const formIngreso = reactive({ cantidad_recibida: '', responsable_recepcion: '', observacion_ingreso: '' })

async function registrarEntrada() {
  await accion('registrar-ingreso-almacen', {
    cantidad_recibida: Number(formIngreso.cantidad_recibida),
    responsable_recepcion: formIngreso.responsable_recepcion.trim(),
    observacion_ingreso: formIngreso.observacion_ingreso.trim(),
  })
}

/* --------- 3. Salida de almacén --------- */
const formSalida = reactive({ cantidad_entregada: '', entregado_a: '', observacion_salida: '' })

async function registrarSalida() {
  await accion('registrar-despacho-almacen', {
    cantidad_entregada: Number(formSalida.cantidad_entregada),
    entregado_a: formSalida.entregado_a.trim(),
    observacion_salida: formSalida.observacion_salida.trim(),
  })
}

/* --------- 4. Entrega con acta --------- */
function onActa(evento) { acta.value = evento.target.files?.[0] || null }

async function entregarConActa() {
  const datos = new FormData()
  datos.append('acta_conformidad', acta.value)
  await accion('entregar-con-acta', datos, true)
}

onMounted(cargar)
</script>

<style scoped>
*{box-sizing:border-box}.layout{min-height:100vh;background:var(--sigta-fondo);color:var(--sigta-texto);font-family:var(--sigta-fuente)}aside{position:fixed;inset:0 auto 0 0;width:var(--sigta-sidebar);background:var(--sigta-azul);color:var(--sigta-blanco);padding:22px 16px;display:flex;flex-direction:column}.brand,.profile{display:flex;align-items:center;gap:12px}.brand{padding:0 10px 20px;border-bottom:1px solid rgba(255,255,255,.2)}.brand>b{background:var(--sigta-mostaza);color:var(--sigta-azul);padding:14px 10px;border-radius:9px}.brand strong,.brand small,.profile b,.profile small{display:block}.brand strong{font-size:23px}.brand small,.profile small{color:var(--sigta-azul-texto-claro);margin-top:3px}.profile{padding:22px 10px}.profile>i{width:42px;height:42px;border-radius:50%;background:var(--sigta-mostaza);color:var(--sigta-azul);display:grid;place-items:center;font-style:normal;font-weight:900}aside>p{font-size:10px;color:var(--sigta-azul-texto-claro);font-weight:800;letter-spacing:1.4px;margin:14px 10px 8px}aside button{border:0;background:transparent;color:var(--sigta-blanco);border-radius:8px;padding:12px;display:flex;gap:11px;align-items:center;text-align:left;cursor:pointer;margin:2px 0;width:100%}aside button>span{font-size:10px;font-weight:900;width:28px}aside button em{margin-left:auto;background:rgba(255,255,255,.16);padding:2px 8px;border-radius:10px;font-style:normal}aside button.active,aside button:hover{background:rgba(255,255,255,.13)}.bottom{margin-top:auto;border-top:1px solid rgba(255,255,255,.2);padding-top:10px}.bottom button{width:100%}main{margin-left:var(--sigta-sidebar);padding:30px 38px 55px;max-width:1650px}header{display:flex;justify-content:space-between;align-items:center;margin-bottom:27px}header small{color:var(--sigta-texto-suave)}h1{font-size:var(--sigta-titulo);margin:6px 0}header p{margin:0;color:var(--sigta-texto-suave)}.refresh{border:1px solid var(--sigta-borde);background:var(--sigta-blanco);color:var(--sigta-azul);padding:10px 14px;border-radius:8px;cursor:pointer}.hero{background:linear-gradient(120deg,var(--sigta-azul),var(--sigta-azul-medio));color:var(--sigta-blanco);border-radius:13px;padding:28px 30px;display:flex;justify-content:space-between;align-items:center}.hero small,.panel-head small,.hoja-head small{font-size:10px;font-weight:800;letter-spacing:1.4px;color:var(--sigta-mostaza-clara)}.hero h2{font-size:24px;margin:7px 0}.hero p{margin:0;color:var(--sigta-azul-texto-claro)}.hero>span{width:68px;height:68px;border:1px solid var(--sigta-mostaza);border-radius:50%;display:grid;place-items:center;font-weight:900}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin:18px 0}.stats article{background:var(--sigta-blanco);border:1px solid var(--sigta-borde);border-radius:10px;padding:19px;display:flex;gap:13px;cursor:pointer}.stats i,.flow i{font-style:normal;width:37px;height:37px;border-radius:8px;display:grid;place-items:center;color:var(--sigta-blanco);font-size:10px;font-weight:900;flex-shrink:0}.blue{background:var(--sigta-azul)}.gold{background:var(--sigta-mostaza);color:var(--sigta-texto)!important}.green{background:var(--sigta-azul-medio)}.stats small,.stats b,.stats p{display:block}.stats b{font-size:25px;margin:3px 0}.stats p{font-size:11px;color:var(--sigta-texto-suave);margin:0}.panels{display:grid;grid-template-columns:2fr 1fr;gap:18px}.panel{background:var(--sigta-blanco);border:1px solid var(--sigta-borde);border-radius:11px;padding:22px}.panel-head h3{margin:5px 0 14px}.flow{width:100%;border:0;border-top:1px solid var(--sigta-borde-suave);background:var(--sigta-blanco);padding:15px 2px;display:flex;gap:13px;align-items:center;text-align:left;cursor:pointer}.flow div{flex:1}.flow b,.flow small{display:block}.flow small{color:var(--sigta-texto-suave);margin-top:4px}.flow>strong{font-size:20px}.copy{color:var(--sigta-texto-suave);font-size:12px;line-height:1.8}.copy a{color:var(--sigta-azul)}.wide{width:100%;padding:10px;border-radius:7px;border:1px solid var(--sigta-borde);cursor:pointer}.primary{background:var(--sigta-azul)!important;color:var(--sigta-blanco)!important;border-color:var(--sigta-azul)!important}.instruction{background:var(--sigta-mostaza-suave);border-left:4px solid var(--sigta-mostaza);padding:14px 17px;margin-bottom:17px;border-radius:7px}.instruction b,.instruction span{display:block}.instruction span{font-size:12px;color:var(--sigta-alerta);margin-top:4px}.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.cards article{background:var(--sigta-blanco);border:1px solid var(--sigta-borde);border-radius:10px;padding:19px}.top{display:flex;justify-content:space-between;gap:8px}.top span{font-size:12px;font-weight:800;color:var(--sigta-azul)}.top em{font-size:10px;background:var(--sigta-azul-tenue);padding:4px 8px;border-radius:10px;font-style:normal;white-space:nowrap}.cards h3{font-size:17px;margin:15px 0 7px}.datos{list-style:none;margin:0 0 10px;padding:0;display:grid;gap:4px}.datos li{display:flex;justify-content:space-between;gap:10px;font-size:11px;border-bottom:1px dashed var(--sigta-borde-suave);padding-bottom:3px}.datos b{color:var(--sigta-texto-suave)}.datos span{color:var(--sigta-texto-suave);text-align:right}.actions{display:flex;gap:7px;border-top:1px solid var(--sigta-borde-suave);padding-top:13px;margin-top:10px}.actions button{flex:1;padding:9px 6px;border-radius:7px;border:1px solid var(--sigta-borde);background:var(--sigta-blanco);color:var(--sigta-texto);font-weight:700;cursor:pointer}.actions button:disabled{opacity:.55;cursor:not-allowed}.empty{text-align:center;background:var(--sigta-blanco);border:1px dashed var(--sigta-borde);padding:65px;border-radius:10px;color:var(--sigta-texto-suave)}.empty>span{font-size:31px;color:var(--sigta-exito)}.empty h3{margin:10px 0 6px}.campo{display:block;margin:14px 0;font-size:12px;font-weight:700;color:var(--sigta-texto)}.campo input{display:block;width:100%;margin-top:6px;padding:9px 11px;border:1px solid var(--sigta-borde);border-radius:7px;font-family:inherit;font-size:13px;font-weight:400;color:var(--sigta-texto)}.situacion{font-size:11px;color:var(--sigta-texto-suave);background:var(--sigta-azul-tenue);border-radius:6px;padding:8px 10px;margin:0 0 10px}.situacion.aviso{background:var(--sigta-mostaza-suave);color:var(--sigta-alerta);font-weight:700}.error-linea{background:var(--sigta-error-fondo);color:var(--sigta-error);padding:10px 13px;border-radius:7px;font-size:12px;font-weight:700}.hoja{max-width:760px}.hoja-head{display:flex;justify-content:space-between;align-items:flex-start;gap:16px;margin-bottom:16px}.hoja-head h3{margin:5px 0 0}.documentos{display:flex;gap:12px;flex-wrap:wrap}.documentos a{color:var(--sigta-azul);font-size:12px}.detalle-modal-backdrop{position:fixed;inset:0;background:rgba(18,58,107,.55);display:grid;place-items:center;padding:20px;z-index:20}.detalle-modal{background:var(--sigta-blanco);border-radius:14px;width:min(700px,100%);max-height:88vh;display:flex;flex-direction:column}.detalle-modal-header{display:flex;justify-content:space-between;align-items:center;padding:20px 24px;border-bottom:1px solid var(--sigta-borde-suave)}.detalle-modal-header h3{margin:0}.detalle-modal-header small{color:var(--sigta-texto-suave)}.detalle-modal-close{border:0;background:transparent;font-size:20px;cursor:pointer;color:var(--sigta-texto-suave)}.detalle-modal-body{padding:20px 24px;overflow-y:auto;display:grid;gap:14px}.detalle-fila{display:grid;grid-template-columns:1fr 1fr;gap:14px}.detalle-campo b{display:block;font-size:11px;color:var(--sigta-texto-suave);margin-bottom:4px}.detalle-campo span,.detalle-campo p{font-size:13px;color:var(--sigta-texto);margin:0}@media(max-width:1050px){.stats{grid-template-columns:1fr 1fr}.panels{grid-template-columns:1fr}.cards{grid-template-columns:1fr 1fr}}@media(max-width:760px){aside{position:static;width:100%}main{margin:0;padding:20px}.stats,.cards{grid-template-columns:1fr}header{align-items:flex-start;flex-direction:column;gap:12px}.detalle-fila{grid-template-columns:1fr}}
</style>
