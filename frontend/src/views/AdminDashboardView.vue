<template>

  <div class="dashboard-layout">

    <!-- =====================================================
         MENÚ ÚNICO DEL ADMINISTRADOR
    ====================================================== -->

    <AdminMenu />


    <!-- =====================================================
         CONTENIDO PRINCIPAL
    ====================================================== -->

    <main class="main-content">


      <!-- =================================================
           BARRA SUPERIOR: BUSCADOR · NOTIFICACIONES · PERFIL
      ================================================== -->

      <div class="dash-strip">

        <div class="dash-search">
          <IconoSigta nombre="buscar" :tamano="17" />
          <input
            v-model="busqueda"
            type="text"
            placeholder="Buscar solicitudes por código, descripción o área…"
          />
        </div>

        <div class="dash-strip-right">

          <div class="dash-notif">
            <button
              type="button"
              class="dash-bell"
              :aria-expanded="notifAbierta"
              aria-label="Notificaciones"
              @click="notifAbierta = !notifAbierta"
            >
              <IconoSigta nombre="notificaciones" :tamano="20" />
              <em v-if="pendientesAprobacion.length">{{ pendientesAprobacion.length }}</em>
            </button>

            <div v-if="notifAbierta" class="dash-notif-panel">
              <header>
                <strong>Notificaciones</strong>
                <button type="button" @click="notifAbierta = false">✕</button>
              </header>
              <p v-if="!pendientesAprobacion.length" class="dash-notif-vacio">
                No tiene solicitudes esperando su decisión.
              </p>
              <ul v-else>
                <li v-for="p in pendientesAprobacion.slice(0, 6)" :key="p.id">
                  <IconoSigta nombre="reloj" :tamano="15" />
                  <div>
                    <strong>{{ p.codigo }}</strong>
                    <span>{{ p.descripcion }}</span>
                  </div>
                  <button type="button" @click="notifAbierta = false; router.push('/admin/compras')">Revisar</button>
                </li>
              </ul>
            </div>
          </div>

          <UsuarioHeader @actualizar="cargarResumen" />

        </div>
      </div>


      <!-- =================================================
           ENCABEZADO
      ================================================== -->

      <header class="dash-head">
        <h1>Panel de Administración</h1>
        <p>
          Supervisión general de los procesos y
          configuración del Sistema Integral de Gestión.
        </p>
      </header>


      <!-- =================================================
           FILTROS
      ================================================== -->

      <div class="dash-filtros">
        <label>
          <IconoSigta nombre="filtro" :tamano="15" />
          <span>Proceso</span>
          <select v-model="filtroProceso" @change="actualizarResumen">
            <option value="">Ambos procesos</option>
            <option value="MANTENIMIENTO">Mantenimiento</option>
            <option value="SOPORTE">Soporte técnico</option>
          </select>
        </label>
        <label class="dash-rango">
          <IconoSigta nombre="reloj" :tamano="15" />
          <span>Periodo</span>
          <input type="date" v-model="rango.desde" :max="rango.hasta" aria-label="Fecha desde">
          <b>–</b>
          <input type="date" v-model="rango.hasta" :min="rango.desde" :max="isoHoy" aria-label="Fecha hasta">
        </label>
      </div>


      <!-- =================================================
           RESUMEN GENERAL
      ================================================== -->

      <section class="stats-grid">

        <article class="stat-card t-azul" @click="$router.push('/admin/actividades')">
          <i class="stat-ico"><IconoSigta nombre="actividades" :tamano="20" /></i>
          <div class="stat-body">
            <span>Actividades</span>
            <strong>{{ resumen.actividades }}</strong>
            <small>Informes remitidos por las jefaturas</small>
          </div>
          <b v-if="tendencias.actividades !== null" class="stat-delta" :class="tendencias.actividades >= 0 ? 'sube' : 'baja'">
            {{ tendencias.actividades >= 0 ? '▲' : '▼' }} {{ Math.abs(tendencias.actividades) }}%
          </b>
        </article>

        <article class="stat-card t-oro" @click="$router.push({path:'/admin/compras',query:{proceso:filtroProceso}})">
          <i class="stat-ico"><IconoSigta nombre="reloj" :tamano="20" /></i>
          <div class="stat-body">
            <span>Pendientes</span>
            <strong>{{ resumen.pendientes }}</strong>
            <small>Solicitudes que esperan su decisión</small>
          </div>
          <b class="stat-delta neutro">—</b>
        </article>

        <article class="stat-card t-azul" @click="abrirStatModal('compras')">
          <i class="stat-ico"><IconoSigta nombre="compras" :tamano="20" /></i>
          <div class="stat-body">
            <span>Solicitudes de compra</span>
            <strong>{{ resumen.compras }}</strong>
            <small>Registradas en el proceso de Compras</small>
          </div>
          <b v-if="tendencias.compras !== null" class="stat-delta" :class="tendencias.compras >= 0 ? 'sube' : 'baja'">
            {{ tendencias.compras >= 0 ? '▲' : '▼' }} {{ Math.abs(tendencias.compras) }}%
          </b>
        </article>

        <article class="stat-card t-verde" @click="$router.push({path:'/admin/historial',query:{proceso:filtroProceso}})">
          <i class="stat-ico"><IconoSigta nombre="validar" :tamano="20" /></i>
          <div class="stat-body">
            <span>Aceptadas</span>
            <strong>{{ resumen.aceptadas }}</strong>
            <small>Solicitudes aprobadas</small>
          </div>
          <b v-if="tendencias.aceptadas !== null" class="stat-delta" :class="tendencias.aceptadas >= 0 ? 'sube' : 'baja'">
            {{ tendencias.aceptadas >= 0 ? '▲' : '▼' }} {{ Math.abs(tendencias.aceptadas) }}%
          </b>
        </article>

        <article class="stat-card t-rojo" @click="$router.push({path:'/admin/historial',query:{proceso:filtroProceso}})">
          <i class="stat-ico"><IconoSigta nombre="error" :tamano="20" /></i>
          <div class="stat-body">
            <span>Rechazadas</span>
            <strong>{{ resumen.rechazadas }}</strong>
            <small>Solicitudes rechazadas</small>
          </div>
          <b v-if="tendencias.rechazadas !== null" class="stat-delta" :class="tendencias.rechazadas > 0 ? 'baja' : 'sube'">
            {{ tendencias.rechazadas >= 0 ? '▲' : '▼' }} {{ Math.abs(tendencias.rechazadas) }}%
          </b>
        </article>

      </section>


      <!-- =================================================
           MENSAJE
      ================================================== -->

      <div
        v-if="mensaje"
        class="dashboard-message"
      >
        {{ mensaje }}
      </div>


      <!-- =================================================
           DETALLE DEL PANEL (aparece al hacer clic
           en una de las tarjetas de arriba)
      ================================================== -->

      <section
        v-if="statCategoria"
        class="content-card"
      >

        <div class="section-header">

          <div>

            <span class="section-kicker">
              DETALLE
            </span>

            <h2>
              {{ statTitulo }}
            </h2>

            <p>
              {{ statItems.length }} de {{ statItemsBase.length }} registro(s)
            </p>

          </div>

          <button
            class="close-panel"
            type="button"
            @click="cerrarStatModal"
          >✕</button>

        </div>


        <input
          v-model="statBusqueda"
          type="text"
          class="stat-search"
          :placeholder="statPlaceholder"
        />


        <p
          v-if="statItems.length === 0"
          class="detalle-vacio"
        >
          No se encontraron registros.
        </p>

        <div
          v-else
          class="stat-list"
        >
          <div
            v-for="item in statItems"
            :key="item.id"
            class="stat-item"
          >
            <div class="stat-item-main">
              <strong>{{ item.titulo }}</strong>
              <span v-if="item.subtitulo">{{ item.subtitulo }}</span>
            </div>

            <div class="stat-item-side">

              <small v-if="item.meta">{{ item.meta }}</small>

              <button
                v-if="item.ruta"
                type="button"
                class="stat-item-revisar"
                @click="router.push(item.ruta)"
              >
                {{ item.accion }}
              </button>

            </div>
          </div>
        </div>

      </section>


      <!-- =================================================
           GRÁFICO · ACTIVIDADES · ACCIONES
      ================================================== -->

      <section class="dash-fila">

        <!-- TENDENCIA -->
        <article class="dash-card dash-grafico">
          <header>
            <div>
              <span class="dash-card-kicker">SEGUIMIENTO</span>
              <h2>Tendencia de solicitudes</h2>
            </div>
            <span class="grafico-rango">{{ rangoTexto }}</span>
          </header>

          <div class="grafico-caja">
            <svg
              :viewBox="`0 0 ${graficoLineas.w} ${graficoLineas.h}`"
              class="grafico-svg"
              preserveAspectRatio="none"
              role="img"
              aria-label="Solicitudes registradas y aprobadas por día"
            >
              <!-- rejilla -->
              <g class="g-rejilla">
                <line
                  v-for="(r, i) in graficoLineas.rejilla"
                  :key="'r' + i"
                  :x1="graficoLineas.mx" :x2="graficoLineas.w - graficoLineas.mx"
                  :y1="r.y" :y2="r.y"
                />
                <text
                  v-for="(r, i) in graficoLineas.rejilla"
                  :key="'rt' + i"
                  :x="graficoLineas.mx - 8" :y="r.y + 3"
                  text-anchor="end"
                >{{ r.v }}</text>
              </g>

              <!-- líneas -->
              <path :d="graficoLineas.dReg" class="g-linea g-reg" />
              <path :d="graficoLineas.dApr" class="g-linea g-apr" />

              <!-- puntos (todos si son pocos; si hay muchos, solo el señalado) -->
              <template v-if="graficoLineas.dias.length <= 20">
                <circle
                  v-for="(p, i) in graficoLineas.reg" :key="'pr' + i"
                  :cx="p.x" :cy="p.y" r="4" class="g-punto g-reg"
                  :class="{ activo: graficoHover === i }"
                />
                <circle
                  v-for="(p, i) in graficoLineas.apr" :key="'pa' + i"
                  :cx="p.x" :cy="p.y" r="4" class="g-punto g-apr"
                  :class="{ activo: graficoHover === i }"
                />
              </template>
              <template v-else-if="graficoHover !== null">
                <circle :cx="graficoLineas.reg[graficoHover].x" :cy="graficoLineas.reg[graficoHover].y" r="4.5" class="g-punto g-reg activo" />
                <circle :cx="graficoLineas.apr[graficoHover].x" :cy="graficoLineas.apr[graficoHover].y" r="4.5" class="g-punto g-apr activo" />
              </template>

              <!-- crosshair -->
              <line
                v-if="graficoHover !== null"
                class="g-cross"
                :x1="graficoLineas.reg[graficoHover].x" :x2="graficoLineas.reg[graficoHover].x"
                :y1="graficoLineas.my" :y2="graficoLineas.h - graficoLineas.my"
              />

              <!-- etiquetas x -->
              <text
                v-for="p in graficoLineas.ejeX" :key="'x' + p.i"
                :x="p.x" :y="graficoLineas.h - 4"
                text-anchor="middle" class="g-eje-x"
              >{{ p.etiqueta }}</text>

              <!-- zonas de hover -->
              <rect
                v-for="(d, i) in graficoLineas.dias" :key="'h' + i"
                :x="i === 0 ? 0 : (graficoLineas.reg[i - 1].x + graficoLineas.reg[i].x) / 2"
                :width="i === 0 || i === graficoLineas.dias.length - 1 ? (graficoLineas.w / graficoLineas.dias.length) : (graficoLineas.reg[i + 1] ? (graficoLineas.reg[i + 1].x - graficoLineas.reg[i - 1].x) / 2 : graficoLineas.w)"
                y="0" :height="graficoLineas.h" fill="transparent"
                @mouseenter="graficoHover = i" @mouseleave="graficoHover = null"
              />
            </svg>

            <div
              v-if="graficoHover !== null"
              class="grafico-tip"
              :style="{ left: (graficoLineas.reg[graficoHover].x / graficoLineas.w * 100) + '%' }"
            >
              <strong>{{ graficoLineas.dias[graficoHover].etiqueta }}</strong>
              <span><i class="pt pt-reg"></i>Registradas: {{ graficoLineas.dias[graficoHover].registradas }}</span>
              <span><i class="pt pt-apr"></i>Aprobadas: {{ graficoLineas.dias[graficoHover].aprobadas }}</span>
            </div>
          </div>

          <div class="grafico-leyenda">
            <span><i class="pt pt-reg"></i>Solicitudes registradas</span>
            <span><i class="pt pt-apr"></i>Solicitudes aprobadas</span>
          </div>
        </article>

        <!-- ACTIVIDADES RECIENTES -->
        <article class="dash-card dash-recientes">
          <header>
            <h2>Actividades recientes</h2>
            <button type="button" class="dash-ver" @click="router.push('/admin/actividades')">
              Ver todas →
            </button>
          </header>

          <p v-if="!actividadesRecientes.length" class="dash-vacio">
            Todavía no hay movimientos registrados.
          </p>
          <ul v-else class="recientes-lista">
            <li v-for="a in actividadesRecientes" :key="a.id">
              <i class="rec-ico" :class="'tono-' + a.tono"><IconoSigta :nombre="a.icono" :tamano="15" /></i>
              <div>
                <strong>{{ a.titulo }}</strong>
                <span>{{ a.detalle }}</span>
              </div>
              <small>{{ a.cuando }}</small>
            </li>
          </ul>
        </article>

        <!-- ACCIONES RÁPIDAS -->
        <article class="dash-card dash-acciones">
          <header><h2>Acciones rápidas</h2></header>
          <button
            v-for="ac in accionesRapidas"
            :key="ac.titulo"
            type="button"
            class="accion"
            :class="'a-' + ac.tono"
            @click="router.push(ac.ruta)"
          >
            <i><IconoSigta :nombre="ac.icono" :tamano="17" /></i>
            <div>
              <strong>{{ ac.titulo }}</strong>
              <span>{{ ac.desc }}</span>
            </div>
            <b>›</b>
          </button>
        </article>

      </section>


      <!-- =================================================
           SOLICITUDES PENDIENTES DE APROBACIÓN
      ================================================== -->

      <article class="dash-card dash-tabla">
        <header>
          <div>
            <h2>Solicitudes pendientes de aprobación</h2>
            <p>{{ pendientesFiltradas.length }} solicitud(es){{ busqueda ? ' que coinciden con la búsqueda' : ' esperan su decisión' }}</p>
          </div>
          <button type="button" class="dash-ver" @click="router.push('/admin/compras')">
            Ver todas las solicitudes →
          </button>
        </header>

        <p v-if="!pendientesFiltradas.length" class="dash-vacio">
          {{ pendientesAprobacion.length ? 'Ninguna solicitud coincide con la búsqueda.' : 'No hay solicitudes esperando su autorización.' }}
        </p>

        <div v-else class="tabla-scroll">
          <table>
            <thead>
              <tr>
                <th>N°</th>
                <th>Código</th>
                <th>Descripción</th>
                <th>Área solicitante</th>
                <th class="num">Monto estimado (Bs.)</th>
                <th>Fecha de solicitud</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(p, i) in pendientesFiltradas" :key="p.id">
                <td>{{ i + 1 }}</td>
                <td class="cod">{{ p.codigo }}</td>
                <td>{{ p.descripcion }}</td>
                <td>{{ p.area }}</td>
                <td class="num">{{ montoBs(p.monto) }}</td>
                <td>{{ fechaCorta(p.fecha) }}</td>
                <td><span class="pill-pend"><IconoSigta nombre="reloj" :tamano="12" /> {{ p.estado }}</span></td>
                <td><button type="button" class="btn-revisar" @click="router.push('/admin/compras')">Revisar</button></td>
              </tr>
            </tbody>
          </table>
        </div>
      </article>


    </main>

  </div>

</template>


<script setup>
import UsuarioHeader from '../components/UsuarioHeader.vue'

import {
  computed,
  onMounted,
  reactive,
  ref
} from 'vue'

import {
  useRouter
} from 'vue-router'


/* =========================================================
   MENÚ ÚNICO
========================================================= */

import AdminMenu
  from '../components/AdminMenu.vue'

import IconoSigta
  from '../components/IconoSigta.vue'

import { coincideProceso } from '../utils/portal'


const router =
  useRouter()


/* =========================================================
   USUARIO
========================================================= */

const usuario =
  ref(null)


/* =========================================================
   RESUMEN
========================================================= */

const resumen =
  reactive({

    usuarios: 0,

    tickets: 0,

    nuevos: 0,

    compras: 0,

    pendientes: 0,

    aceptadas: 0,

    rechazadas: 0,

    // Los informes de actividad todavía no tienen origen real:
    // se leen de la misma maqueta que usa /admin/actividades
    // para que ambas pantallas digan siempre lo mismo.
    actividades: 0,
  })


/* =========================================================
   CLASIFICACIÓN DE SOLICITUDES DE COMPRA

   Mismos grupos que usa la pantalla de Solicitudes, para que
   las tarjetas y las listas digan lo mismo.

   Las que están EN_REVISION_DAF no le corresponden al Director
   y no aparecen en sus pantallas, así que tampoco se cuentan en
   ninguna tarjeta: si se contaran solo en el total, este no
   cuadraría con la suma de las otras tres.
========================================================= */

const ESTADOS_RECHAZADA = [
  'RECHAZADO',
  'ANULADO',
]

const ESTADOS_APROBADA = [
  'APROBADO_PARA_DESEMBOLSO',
  'FONDOS_DESEMBOLSADOS',
  'COMPRA_REGISTRADA',
  'COMPRADO_Y_ENTREGADO',
  'DESCARGO_PENDIENTE_LIQUIDACION',
  'CERRADO_ARCHIVADO',
]

const ESTADOS_REVISION_DAF = [
  'CREADO_PENDIENTE_DAF',
  'EVALUADO_PENDIENTE_CERTIFICACION',
]


function grupoCompra(compra) {

  const estado =
    String(compra?.estado || '')
      .trim()
      .toUpperCase()

  if (ESTADOS_RECHAZADA.includes(estado)) {
    return 'RECHAZADA'
  }

  if (ESTADOS_APROBADA.includes(estado)) {
    return 'APROBADA'
  }

  if (ESTADOS_REVISION_DAF.includes(estado)) {
    return 'EN_REVISION_DAF'
  }

  return estado === 'VERIFICADO_PENDIENTE_AUTORIZACION' ? 'EN_ESPERA' : 'EN_REVISION_DAF'
}


/* =========================================================
   REGISTROS COMPLETOS (PARA LOS MODALES DE DETALLE)
========================================================= */

const usuariosLista =
  ref([])

const ticketsTodos = ref([])
const filtroProceso = ref('')
const ticketsLista = computed(() => ticketsTodos.value.filter(item => coincideProceso(item, filtroProceso.value)))

const comprasTodas = ref([])
const comprasLista = computed(() => comprasTodas.value.filter(item => coincideProceso(item, filtroProceso.value)))

function actualizarResumen() {
  const compras = comprasLista.value, tickets = ticketsLista.value
  resumen.tickets = tickets.length
  resumen.nuevos = tickets.filter(t=>['NUEVO','RECIBIDO'].includes(t.estado_codigo)).length
  resumen.pendientes = compras.filter(c=>grupoCompra(c)==='EN_ESPERA').length
  resumen.aceptadas = compras.filter(c=>grupoCompra(c)==='APROBADA').length
  resumen.rechazadas = compras.filter(c=>grupoCompra(c)==='RECHAZADA').length
  resumen.compras = resumen.pendientes + resumen.aceptadas + resumen.rechazadas
  resumen.actividades = tickets.filter(t=>t.informe_elevado_en && t.informe_final).length
}


/* =========================================================
   MENSAJE
========================================================= */

const mensaje =
  ref('')


/* =========================================================
   TOKEN
========================================================= */

const obtenerToken = () =>
  localStorage.getItem(
    'sigta_token'
  )


/* =========================================================
   INICIALES
========================================================= */

const inicialesUsuario =
  computed(() => {

    const nombre =
      usuario.value?.nombre
      ||
      usuario.value?.nombre_completo
      ||
      'Administrador'


    return nombre
      .trim()
      .split(/\s+/)
      .slice(0, 2)
      .map(
        palabra =>
          palabra
            .charAt(0)
            .toUpperCase()
      )
      .join('')
  })


/* =========================================================
   INICIO
========================================================= */

onMounted(
  async () => {

    const usuarioGuardado =
      localStorage.getItem(
        'sigta_usuario'
      )


    const token =
      obtenerToken()


    if (
      !usuarioGuardado
      ||
      !token
    ) {

      router.push(
        '/login'
      )

      return
    }


    try {

      usuario.value =
        JSON.parse(
          usuarioGuardado
        )

    } catch (error) {

      console.error(
        'Error leyendo usuario:',
        error
      )


      cerrarSesion()

      return
    }


    await cargarResumen()
  }
)


/* =========================================================
   HEADERS
========================================================= */

function headersAuth() {

  return {

    Authorization:
      `Token ${obtenerToken()}`,

    Accept:
      'application/json',
  }
}


/* =========================================================
   NORMALIZAR RESPUESTAS
========================================================= */

function convertirLista(
  datos
) {

  if (
    Array.isArray(datos)
  ) {

    return datos
  }


  if (
    Array.isArray(
      datos?.results
    )
  ) {

    return datos.results
  }


  return []
}


/* =========================================================
   CARGAR RESUMEN
========================================================= */

async function cargarResumen() {

  mensaje.value = ''


  try {

    const [
      usuariosRes,
      ticketsRes,
      comprasRes, mantenimientoRes
    ] =
      await Promise.all([


        /* USUARIOS */

        fetch(
          '/api/usuarios/usuarios/',
          {
            headers:
              headersAuth()
          }
        ),


        /* SOPORTE TÉCNICO */

        fetch(
          '/api/soporte/tickets/',
          {
            headers:
              headersAuth()
          }
        ),


        /* COMPRAS */

        fetch(
          '/api/compras/solicitudes/?bandeja=direccion',
          {
            headers:
              headersAuth()
          }
        ),

        fetch('/api/mantenimiento/requerimientos/', { headers: headersAuth() }),
      ])


    /* =====================================================
       SESIÓN VENCIDA
    ====================================================== */

    const respuestas = [

      usuariosRes,

      ticketsRes,

      comprasRes, mantenimientoRes
    ]


    const sinAutorizacion =
      respuestas.some(
        respuesta =>
          respuesta.status === 401
          ||
          respuesta.status === 403
      )


    if (
      sinAutorizacion
    ) {

      cerrarSesion()

      return
    }


    /* =====================================================
       LEER DATOS
    ====================================================== */

    const usuariosDatos =
      usuariosRes.ok
        ? await usuariosRes.json()
        : []


    const ticketsDatos =
      ticketsRes.ok
        ? await ticketsRes.json()
        : []


    const comprasDatos =
      comprasRes.ok
        ? await comprasRes.json()
        : []


    /* =====================================================
       NORMALIZAR
    ====================================================== */

    const usuarios =
      convertirLista(
        usuariosDatos
      )


    const tickets = [
      ...convertirLista(ticketsDatos).map(t=>({...t, proceso:'SOPORTE'})),
      ...convertirLista(mantenimientoRes.ok ? await mantenimientoRes.json() : []).map(t=>({...t, proceso:'MANTENIMIENTO'})),
    ]


    const compras =
      convertirLista(
        comprasDatos
      )


    /* =====================================================
       GUARDAR REGISTROS COMPLETOS
       (para los modales de detalle de cada panel)
    ====================================================== */

    usuariosLista.value =
      usuarios


    ticketsTodos.value =
      tickets


    comprasTodas.value =
      compras


    /* =====================================================
       CONTADORES
    ====================================================== */

    resumen.usuarios =
      usuarios.length


    resumen.tickets =
      tickets.length


    // Lo que espera SU decisión (la DAF ya certificó).
    resumen.pendientes =
      compras.filter(
        compra => grupoCompra(compra) === 'EN_ESPERA'
      ).length


    resumen.aceptadas =
      compras.filter(
        compra => grupoCompra(compra) === 'APROBADA'
      ).length


    resumen.rechazadas =
      compras.filter(
        compra => grupoCompra(compra) === 'RECHAZADA'
      ).length


    // El total es la suma de las otras tres tarjetas, no todas
    // las filas de la tabla: las que siguen en revisión de la DAF
    // no se le muestran al Director en ninguna pantalla.
    resumen.compras =
      resumen.pendientes
      + resumen.aceptadas
      + resumen.rechazadas


    resumen.nuevos =
      tickets.filter(
        ticket => {

          const codigo =
            normalizarEstado(
              ticket.estado_codigo
            )


          const nombre =
            normalizarEstado(
              ticket.estado_nombre
            )


          return (
            codigo === 'NUEVO'
            ||
            nombre === 'NUEVO'
          )
        }
      ).length


    /* =====================================================
       AVISO SI UN ENDPOINT NO RESPONDE
    ====================================================== */

    actualizarResumen()

    const errores = []


    if (!usuariosRes.ok) {
      errores.push('usuarios')
    }


    if (!ticketsRes.ok) {
      errores.push('soporte técnico')
    }


    if (!mantenimientoRes.ok) errores.push('mantenimiento')

    if (!comprasRes.ok) {
      errores.push('compras')
    }


    if (
      errores.length > 0
    ) {

      mensaje.value =
        `No fue posible cargar completamente: ${errores.join(', ')}.`

    }


    /* =====================================================
       DEBUG
    ====================================================== */

    console.log(
      'Dashboard usuarios:',
      usuarios
    )


    console.log(
      'Dashboard tickets:',
      tickets
    )


    console.log(
      'Dashboard expedientes de compra:',
      compras
    )


  } catch (error) {

    console.error(
      'Error cargando Dashboard:',
      error
    )


    mensaje.value =
      'No fue posible cargar todos los indicadores del panel.'
  }
}


/* =========================================================
   NORMALIZAR ESTADO
========================================================= */

function normalizarEstado(
  valor
) {

  return String(
    valor
    ||
    ''
  )
    .trim()
    .toUpperCase()
    .replace(/\s+/g, '_')
}


/* =========================================================
   MODAL DE DETALLE POR PANEL
========================================================= */

const statCategoria =
  ref('')

const statBusqueda =
  ref('')


const statConfig = {

  usuarios: {
    titulo: 'Usuarios',
    placeholder: 'Buscar por nombre o correo...',
  },

  tickets: {
    titulo: 'Requerimientos de soporte y mantenimiento',
    placeholder: 'Buscar por código o título...',
  },

  nuevos: {
    titulo: 'Requerimientos nuevos',
    placeholder: 'Buscar por código o título...',
  },

  compras: {
    titulo: 'Solicitudes de compra',
    placeholder: 'Buscar por código o título...',
  },
}


const statTitulo =
  computed(() =>
    statConfig[statCategoria.value]?.titulo
    || ''
  )


const statPlaceholder =
  computed(() =>
    statConfig[statCategoria.value]?.placeholder
    || 'Buscar...'
  )


const statItemsBase =
  computed(() => {

    if (statCategoria.value === 'usuarios') {

      return usuariosLista.value.map(
        u => ({
          id: u.id,
          titulo: u.nombre_completo || u.username || u.email || 'Usuario',
          subtitulo: u.email || '',
          meta: u.roles?.[0]?.nombre || u.roles?.[0]?.rol_nombre || 'Sin rol',
        })
      )
    }


    if (statCategoria.value === 'tickets') {

      return ticketsLista.value.map(
        t => ({
          id: t.id,
          titulo: `${t.codigo || 'S/C'} · ${t.titulo || 'Sin título'}`,
          subtitulo: t.estado_nombre || t.estado_codigo || t.estado || '',
          meta: t.area_nombre || '',
        })
      )
    }


    if (statCategoria.value === 'nuevos') {

      return ticketsLista.value
        .filter(
          t => {

            const codigo =
              normalizarEstado(t.estado_codigo)

            const nombre =
              normalizarEstado(t.estado_nombre)

            return (
              codigo === 'NUEVO'
              ||
              nombre === 'NUEVO'
            )
          }
        )
        .map(
          t => ({
            id: t.id,
            titulo: `${t.codigo || 'S/C'} · ${t.titulo || 'Sin título'}`,
            subtitulo: t.estado_nombre || t.estado_codigo || t.estado || '',
            meta: t.area_nombre || '',
          })
        )
    }


    if (statCategoria.value === 'compras') {

      // Las mismas que cuenta la tarjeta: sin las que siguen en
      // revisión de la DAF, o el listado mostraría más filas de
      // las que anuncia el número.
      return comprasLista.value
        .filter(
          c => grupoCompra(c) !== 'EN_REVISION_DAF'
        )
        .map(
          c => {

            // Cada fila lleva a la pantalla donde realmente está:
            // las pendientes a Solicitudes y las ya decididas al
            // Historial. Antes todas iban a Solicitudes, así que
            // una solicitud ya aprobada aterrizaba en una lista
            // vacía.
            const pendiente =
              grupoCompra(c) === 'EN_ESPERA'

            return {
              id: c.id,
              titulo: `${c.codigo || 'S/C'} · ${c.titulo || 'Sin título'}`,
              subtitulo: c.estado_nombre || c.estado || '',
              meta: c.area_nombre || '',
              ruta: pendiente
                ? '/admin/compras'
                : '/admin/historial',
              accion: pendiente
                ? 'Ir a revisar'
                : 'Ver en historial',
            }
          }
        )
    }


    return []
  })


const statItems =
  computed(() => {

    const texto =
      statBusqueda.value
        .trim()
        .toLowerCase()


    if (!texto) {
      return statItemsBase.value
    }


    return statItemsBase.value.filter(
      item =>
        [item.titulo, item.subtitulo, item.meta]
          .filter(Boolean)
          .join(' ')
          .toLowerCase()
          .includes(texto)
    )
  })


function abrirStatModal(
  categoria
) {

  statCategoria.value =
    categoria

  statBusqueda.value =
    ''
}


function cerrarStatModal() {

  statCategoria.value =
    ''

  statBusqueda.value =
    ''
}


/* =========================================================
   ENCABEZADO: SALUDO Y FECHA
========================================================= */

const saludo = computed(() => {
  const h = new Date().getHours()
  return h < 12 ? 'Buenos días' : h < 19 ? 'Buenas tardes' : 'Buenas noches'
})

const primerNombre = computed(() => {
  const n = usuario.value?.nombre || usuario.value?.nombre_completo || 'Director'
  return n.trim().split(/\s+/)[0]
})

const fechaLarga = computed(() => {
  const f = new Date().toLocaleDateString('es-BO', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
  })
  return f.charAt(0).toUpperCase() + f.slice(1)
})


/* =========================================================
   PERIODO Y TENDENCIAS
========================================================= */

function isoDia(d) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
}

/* Rango de fechas que elige el Director (por defecto: últimos 30 días). */
const hoyRef = new Date()
const rango = reactive({
  desde: isoDia(new Date(+hoyRef - 29 * 86400000)),
  hasta: isoDia(hoyRef),
})

const isoHoy = isoDia(hoyRef)

const rangoTexto = computed(() => {
  const f = (d) => d.toLocaleDateString('es-BO', { day: 'numeric', month: 'short', year: 'numeric' })
  const { desde, hasta } = rangoFechas.value
  return `${f(desde)} – ${f(hasta)}`
})

const rangoFechas = computed(() => {
  let d = new Date(rango.desde + 'T00:00:00')
  let h = new Date(rango.hasta + 'T23:59:59.999')
  if (isNaN(d)) d = new Date(+new Date() - 29 * 86400000)
  if (isNaN(h)) h = new Date()
  if (d > h) [d, h] = [h, d]
  const dias = Math.max(1, Math.round((+h - +d) / 86400000) + 1)
  return { desde: d, hasta: h, dias }
})

function fechaDe(valor) {
  const d = valor ? new Date(valor) : null
  return d && !isNaN(d) ? d : null
}

function claveDia(d) {
  return isoDia(d)
}

/* Cuenta registros cuya fecha cae en [desde, hasta] */
function contarEnRango(lista, campoFecha, desde, hasta, filtro) {
  return lista.filter(item => {
    if (filtro && !filtro(item)) return false
    const f = fechaDe(item[campoFecha])
    return f && f >= desde && f <= hasta
  }).length
}

/* Variación % del rango elegido contra el rango anterior de igual duración.
   null = el rango anterior no tiene registros (no hay base de comparación). */
function variacion(lista, campoFecha, filtro) {
  const { desde, hasta } = rangoFechas.value
  const dur = +hasta - +desde
  const actual = contarEnRango(lista, campoFecha, desde, hasta, filtro)
  const previo = contarEnRango(lista, campoFecha, new Date(+desde - dur - 1), new Date(+desde - 1), filtro)
  if (previo === 0) return null
  return Math.round(((actual - previo) / previo) * 100)
}

const tendencias = computed(() => ({
  actividades: variacion(ticketsLista.value, 'informe_elevado_en', t => t.informe_elevado_en && t.informe_final),
  pendientes: null,
  compras: variacion(comprasLista.value, 'creado_en', c => grupoCompra(c) !== 'EN_REVISION_DAF'),
  aceptadas: variacion(comprasLista.value, 'actualizado_en', c => grupoCompra(c) === 'APROBADA'),
  rechazadas: variacion(comprasLista.value, 'actualizado_en', c => grupoCompra(c) === 'RECHAZADA'),
}))


/* =========================================================
   GRÁFICO: SOLICITUDES POR DÍA
========================================================= */

const serieTendencia = computed(() => {
  const { desde, dias: total } = rangoFechas.value
  const n = Math.min(total, 120)          // tope de puntos para no saturar el SVG
  const inicio = new Date(desde)
  inicio.setHours(0, 0, 0, 0)

  const dias = []
  for (let i = 0; i < n; i++) {
    const d = new Date(+inicio + i * 86400000)
    dias.push({
      clave: claveDia(d),
      etiqueta: d.toLocaleDateString('es-BO', { day: 'numeric', month: 'short' }),
      registradas: 0,
      aprobadas: 0,
    })
  }
  const indice = Object.fromEntries(dias.map((d, i) => [d.clave, i]))

  for (const c of comprasLista.value) {
    if (grupoCompra(c) === 'EN_REVISION_DAF') continue
    const creado = fechaDe(c.creado_en)
    if (creado) {
      const k = claveDia(creado)
      if (k in indice) dias[indice[k]].registradas++
    }
    if (grupoCompra(c) === 'APROBADA') {
      const aprob = fechaDe(c.actualizado_en) || creado
      if (aprob) {
        const k = claveDia(aprob)
        if (k in indice) dias[indice[k]].aprobadas++
      }
    }
  }
  return dias
})

/* Geometría del SVG (viewBox 0 0 100 100, se estira con CSS) */
const GRAFICO = { w: 680, h: 210, mx: 34, my: 18 }

const graficoLineas = computed(() => {
  const s = serieTendencia.value
  const maxVal = Math.max(3, ...s.flatMap(d => [d.registradas, d.aprobadas]))
  const { w, h, mx, my } = GRAFICO
  const px = (i) => s.length <= 1 ? mx : mx + (i * (w - 2 * mx)) / (s.length - 1)
  const py = (v) => h - my - (v / maxVal) * (h - 2 * my)

  const puntos = (campo) => s.map((d, i) => ({ x: px(i), y: py(d[campo]), v: d[campo], etiqueta: d.etiqueta }))
  const linea = (pts) => pts.map((p, i) => `${i ? 'L' : 'M'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ')

  const reg = puntos('registradas')
  const apr = puntos('aprobadas')
  const rejilla = [0, 0.5, 1].map(f => ({ y: py(maxVal * f), v: Math.round(maxVal * f) }))

  // Con muchos días, solo se rotula 1 de cada N para no encimar el eje X.
  const paso = Math.max(1, Math.ceil(s.length / 8))
  const ejeX = s
    .map((d, i) => ({ x: reg[i].x, etiqueta: d.etiqueta, i }))
    .filter(p => p.i % paso === 0 || p.i === s.length - 1)

  return { w, h, mx, my, maxVal, reg, apr, dReg: linea(reg), dApr: linea(apr), rejilla, ejeX, dias: s }
})

const graficoHover = ref(null)   // índice del día señalado


/* =========================================================
   ACTIVIDADES RECIENTES
========================================================= */

function haceCuanto(valor) {
  const f = fechaDe(valor)
  if (!f) return ''
  const min = Math.round((Date.now() - +f) / 60000)
  if (min < 1) return 'hace un momento'
  if (min < 60) return `hace ${min} min`
  const hrs = Math.round(min / 60)
  if (hrs < 24) return `hace ${hrs} h`
  const dias = Math.round(hrs / 24)
  return dias === 1 ? 'hace 1 día' : `hace ${dias} días`
}

const actividadesRecientes = computed(() => {
  const items = comprasLista.value.map(c => {
    const g = grupoCompra(c)
    const cfg = g === 'APROBADA'
      ? { titulo: 'Solicitud de compra aprobada', icono: 'validar', tono: 'ok' }
      : g === 'RECHAZADA'
        ? { titulo: 'Solicitud rechazada', icono: 'error', tono: 'mal' }
        : g === 'EN_ESPERA'
          ? { titulo: 'Solicitud enviada a su verificación', icono: 'reloj', tono: 'espera' }
          : { titulo: 'Solicitud registrada en Compras', icono: 'solicitudes', tono: 'info' }
    return {
      id: 'c' + c.id,
      ...cfg,
      detalle: `${c.codigo || 'S/C'} · ${c.titulo || 'Sin título'}`,
      fecha: fechaDe(c.actualizado_en) || fechaDe(c.creado_en),
    }
  })
  return items
    .filter(i => i.fecha)
    .sort((a, b) => b.fecha - a.fecha)
    .slice(0, 6)
    .map(i => ({ ...i, cuando: haceCuanto(i.fecha) }))
})


/* =========================================================
   BUSCADOR
========================================================= */

const busqueda = ref('')


/* =========================================================
   SOLICITUDES PENDIENTES DE APROBACIÓN
========================================================= */

function montoBs(valor) {
  const n = Number(valor)
  return isNaN(n) ? '—' : n.toLocaleString('es-BO', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function fechaCorta(valor) {
  const f = fechaDe(valor)
  return f ? f.toLocaleDateString('es-BO', { day: '2-digit', month: '2-digit', year: 'numeric' }) : '—'
}

const pendientesAprobacion = computed(() =>
  comprasLista.value
    .filter(c => grupoCompra(c) === 'EN_ESPERA')
    .map(c => ({
      id: c.id,
      codigo: c.codigo || 'S/C',
      descripcion: c.titulo || c.descripcion || 'Sin descripción',
      area: c.area_nombre || '—',
      monto: c.monto_estimado,
      fecha: c.creado_en,
      estado: c.estado_nombre || 'Pendiente',
    }))
    .sort((a, b) => (fechaDe(a.fecha) || 0) - (fechaDe(b.fecha) || 0))
)

const pendientesFiltradas = computed(() => {
  const t = busqueda.value.trim().toLowerCase()
  if (!t) return pendientesAprobacion.value
  return pendientesAprobacion.value.filter(p =>
    [p.codigo, p.descripcion, p.area, p.estado].some(v => (v || '').toLowerCase().includes(t))
  )
})


/* =========================================================
   NOTIFICACIONES
========================================================= */

const notifAbierta = ref(false)


/* =========================================================
   ACCIONES RÁPIDAS
========================================================= */

const accionesRapidas = [
  { icono: 'solicitudes', titulo: 'Nueva solicitud', desc: 'Registrar una nueva solicitud', ruta: '/admin/portal-solicitante', tono: 'azul' },
  { icono: 'reloj', titulo: 'Verificar pendientes', desc: 'Revisar solicitudes en espera', ruta: { path: '/admin/mis-solicitudes', query: { vista: 'verificaciones' } }, tono: 'oro' },
  { icono: 'compras', titulo: 'Autorizar compras', desc: 'Gestionar y aprobar solicitudes', ruta: '/admin/compras', tono: 'azul' },
  { icono: 'reporte', titulo: 'Ver reportes', desc: 'Consultar estadísticas y reportes', ruta: '/admin/historial', tono: 'azul' },
]


/* =========================================================
   CERRAR SESIÓN
========================================================= */

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

.dashboard-layout {

  min-height: 100vh;

  display: flex;

  background: var(--sigta-azul-tenue);

  font-family: var(--sigta-fuente);
}


.main-content {

  flex: 1;

  min-width: 0;

  padding: 28px;

  overflow-x: hidden;
}


/* =========================================================
   TOPBAR
========================================================= */

.topbar {

  display: flex;

  justify-content:
    space-between;

  align-items: center;

  gap: 20px;

  margin-bottom: 24px;
}


.topbar h1 {

  margin: 0;

  color: var(--sigta-texto);

  font-size: 34px;
}


.topbar p {

  margin:
    5px
    0
    0;

  color: var(--sigta-texto-suave);

  font-size: 18px;
}


/* =========================================================
   USUARIO
========================================================= */

.user-box {

  min-width: 205px;

  display: flex;

  align-items: center;

  justify-content: flex-end;

  gap: 9px;

  padding:
    10px
    14px;

  background: var(--sigta-blanco);

  border-radius: 9px;

  box-shadow:
    0
    3px
    10px
    rgba(0,0,0,.07);
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


.user-box strong,
.user-box span {

  display: block;
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


/* =========================================================
   ESTADÍSTICAS
========================================================= */

/* Cinco tarjetas: Actividades, Pendientes, Total, Aceptadas y
   Rechazadas. La rejilla era de 4 columnas fijas, así que la
   quinta caía sola a una segunda fila. */

.stats-grid {

  display: grid;

  grid-template-columns:
    repeat(5,1fr);

  gap: 14px;

  margin-bottom: 22px;
}


.stat-card {

  min-width: 0;

  min-height: 120px;

  padding: 18px;

  background: var(--sigta-blanco);

  border-top:
    4px solid var(--sigta-mostaza);

  border-radius: 10px;

  box-shadow:
    0
    4px
    14px
    rgba(0,0,0,.05);

  cursor: pointer;

  transition:
    transform .15s ease,
    box-shadow .15s ease;
}


.stat-card:hover {

  transform: scale(1.04);

  box-shadow:
    0
    8px
    20px
    rgba(0,0,0,.1);
}


.stat-card span {

  display: block;

  margin-bottom: 7px;

  color: var(--sigta-texto-suave);

  /* 13px en vez de 15: con cinco columnas la etiqueta es lo
     primero que se parte en varias líneas. */
  font-size: 13px;

  font-weight: 800;

  letter-spacing: .4px;

  text-transform: uppercase;
}


.stat-card strong {

  display: block;

  margin-bottom: 6px;

  color: var(--sigta-azul);

  font-size: 34px;
}


.stat-card small {

  display: block;

  color: var(--sigta-texto-suave);

  font-size: 13px;

  line-height: 1.35;
}


/* =========================================================
   MENSAJE
========================================================= */

.dashboard-message {

  margin-bottom: 18px;

  padding:
    11px
    13px;

  border-radius: 7px;

  background: var(--sigta-mostaza-suave);

  color: var(--sigta-mostaza-oscuro);

  font-size: 16px;
}


/* =========================================================
   CONTENEDORES
========================================================= */

.content-card {

  margin-bottom: 20px;

  padding: 22px;

  background: var(--sigta-blanco);

  border-radius: 10px;

  box-shadow:
    0
    4px
    14px
    rgba(0,0,0,.05);
}


.section-kicker {

  display: block;

  margin-bottom: 5px;

  color: var(--sigta-texto-suave);

  font-size: 14px;

  font-weight: 900;

  letter-spacing: .8px;
}


.section-header {

  display: flex;

  align-items: flex-start;

  justify-content: space-between;

  gap: 14px;
}


.section-header h2 {

  margin: 0;

  color: var(--sigta-azul);

  font-size: 24px;
}


.section-header p {

  margin:
    5px
    0
    18px;

  color: var(--sigta-texto-suave);

  font-size: 16px;
}


.close-panel {

  flex-shrink: 0;

  width: 32px;

  height: 32px;

  border: none;

  border-radius: 50%;

  background: var(--sigta-azul-tenue);

  color: var(--sigta-texto-suave);

  font-size: 15px;

  line-height: 1;

  cursor: pointer;
}


.close-panel:hover {

  background: var(--sigta-borde);
}


/* =========================================================
   DETALLE DEL PANEL
========================================================= */

.stat-search {

  width: 100%;

  padding:
    12px
    14px;

  border:
    1px solid var(--sigta-borde);

  border-radius: 8px;

  background: white;

  color: var(--sigta-texto);

  font-family: inherit;

  font-size: 15px;

  outline: none;
}


.stat-search:focus {

  border-color: var(--sigta-texto-suave);
}


.stat-list {

  margin-top: 14px;

  display: flex;

  flex-direction: column;
}


.content-card > .detalle-vacio {

  display: block;

  margin-top: 14px;
}


.stat-item {

  display: flex;

  align-items: center;

  justify-content: space-between;

  gap: 12px;

  padding: 12px 4px;

  border-bottom: 1px solid var(--sigta-azul-tenue);
}


.stat-item:last-child {

  border-bottom: none;
}


.stat-item-main {

  min-width: 0;
}


.stat-item-main strong {

  display: block;

  color: var(--sigta-texto);

  font-size: 15px;
}


.stat-item-main span {

  display: block;

  margin-top: 2px;

  color: var(--sigta-texto-suave);

  font-size: 13px;
}


.stat-item-side {

  flex-shrink: 0;

  display: flex;

  flex-direction: column;

  align-items: flex-end;

  gap: 6px;
}


.stat-item-side > small {

  padding: 4px 8px;

  border-radius: 12px;

  background: var(--sigta-azul-tenue);

  color: var(--sigta-texto-suave);

  font-size: 12px;
  font-weight: 700;
}


.stat-item-revisar {

  padding: 0;

  border: none;

  background: transparent;

  color: var(--sigta-azul);

  font-size: 13px;
  font-weight: 700;

  text-decoration: underline;

  cursor: pointer;
}


.stat-item-revisar:hover {

  color: var(--sigta-azul);
}


/* =========================================================
   RESPONSIVE
========================================================= */

@media (
  max-width: 1200px
) {

  .stats-grid {

    grid-template-columns:
      repeat(3,1fr);
  }

}


@media (
  max-width: 900px
) {

  .stats-grid {

    grid-template-columns:
      repeat(2,1fr);
  }

}


@media (
  max-width: 760px
) {

  .dashboard-layout {

    display: block;
  }


  .main-content {

    padding: 18px;
  }


  .topbar {

    flex-direction: column;

    align-items: flex-start;
  }


  .user-box {

    justify-content:
      flex-start;
  }

}


@media (
  max-width: 520px
) {

  .stats-grid {

    grid-template-columns:
      1fr;
  }

}


/* =========================================================
   REDISEÑO DIRECTOR — BARRA SUPERIOR
========================================================= */

.dash-strip {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 20px;
}

.dash-search {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 9px;
  height: 44px;
  padding: 0 14px;
  border: 1px solid var(--sigta-borde);
  border-radius: 10px;
  background: var(--sigta-blanco);
  color: var(--sigta-texto-suave);
  box-shadow: 0 2px 8px rgba(11, 40, 79, .05);
}

.dash-search input {
  flex: 1;
  min-width: 0;
  border: 0;
  outline: none;
  background: transparent;
  font-family: inherit;
  font-size: 14px;
  color: var(--sigta-texto);
}

.dash-strip-right {
  display: flex;
  align-items: center;
  gap: 12px;
}

.dash-notif { position: relative; }

.dash-bell {
  position: relative;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--sigta-borde);
  border-radius: 10px;
  background: var(--sigta-blanco);
  color: var(--sigta-azul);
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(11, 40, 79, .05);
}

.dash-bell em {
  position: absolute;
  top: -5px;
  right: -5px;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 9px;
  background: var(--sigta-error);
  color: #fff;
  font-size: 11px;
  font-style: normal;
  font-weight: 800;
}

.dash-notif-panel {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 320px;
  z-index: 30;
  background: var(--sigta-blanco);
  border: 1px solid var(--sigta-borde);
  border-radius: 12px;
  box-shadow: 0 16px 40px rgba(11, 40, 79, .2);
  overflow: hidden;
}

.dash-notif-panel header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 14px;
  border-bottom: 1px solid var(--sigta-borde-suave);
}

.dash-notif-panel header strong { color: var(--sigta-azul); font-size: 14px; }
.dash-notif-panel header button { border: 0; background: transparent; cursor: pointer; color: var(--sigta-texto-suave); font-size: 15px; }

.dash-notif-vacio { margin: 0; padding: 22px 16px; text-align: center; color: var(--sigta-texto-suave); font-size: 13px; }

.dash-notif-panel ul { list-style: none; margin: 0; padding: 6px; max-height: 320px; overflow-y: auto; }
.dash-notif-panel li {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 9px 8px;
  border-radius: 8px;
}
.dash-notif-panel li:hover { background: var(--sigta-azul-tenue); }
.dash-notif-panel li > :deep(.icono-sigta) { color: var(--sigta-alerta); flex-shrink: 0; }
.dash-notif-panel li div { flex: 1; min-width: 0; }
.dash-notif-panel li strong { display: block; font-size: 12.5px; color: var(--sigta-azul); }
.dash-notif-panel li span { display: block; font-size: 12px; color: var(--sigta-texto-suave); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.dash-notif-panel li button {
  flex-shrink: 0;
  border: 1px solid var(--sigta-borde);
  border-radius: 6px;
  background: var(--sigta-blanco);
  color: var(--sigta-azul);
  font-size: 11.5px;
  font-weight: 700;
  padding: 5px 9px;
  cursor: pointer;
}


/* =========================================================
   REDISEÑO DIRECTOR — ENCABEZADO
========================================================= */

.dash-head {
  margin-bottom: 20px;
}

.dash-head h1 {
  margin: 0;
  color: var(--sigta-texto);
  font-size: 32px;
  font-weight: 800;
}

.dash-head p {
  margin: 6px 0 0;
  color: var(--sigta-texto-suave);
  font-size: 15.5px;
  max-width: 620px;
}


/* =========================================================
   REDISEÑO DIRECTOR — FILTROS
========================================================= */

.dash-filtros {
  display: flex;
  gap: 14px;
  margin-bottom: 20px;
}

.dash-filtros label {
  display: flex;
  align-items: center;
  gap: 7px;
  font-size: 13px;
  font-weight: 700;
  color: var(--sigta-texto-suave);
}

.dash-filtros label > :deep(.icono-sigta) {
  color: var(--sigta-azul-medio);
  flex-shrink: 0;
}

.dash-filtros select {
  height: 40px;
  padding: 0 12px;
  border: 1px solid var(--sigta-borde);
  border-radius: 9px;
  background: var(--sigta-blanco);
  color: var(--sigta-texto);
  font-family: inherit;
  font-size: 13.5px;
  cursor: pointer;
}

.dash-rango { flex-wrap: wrap; }

.dash-rango input[type="date"] {
  height: 40px;
  padding: 0 10px;
  border: 1px solid var(--sigta-borde);
  border-radius: 9px;
  background: var(--sigta-blanco);
  color: var(--sigta-texto);
  font-family: inherit;
  font-size: 13px;
  cursor: pointer;
}

.dash-rango input[type="date"]:focus {
  outline: none;
  border-color: var(--sigta-azul-medio);
  box-shadow: 0 0 0 3px rgba(29, 80, 144, .12);
}

.dash-rango b { color: var(--sigta-texto-tenue); font-weight: 700; }

.grafico-rango {
  flex-shrink: 0;
  padding: 5px 10px;
  border-radius: 7px;
  background: var(--sigta-azul-tenue);
  color: var(--sigta-azul);
  font-size: 11.5px;
  font-weight: 700;
  white-space: nowrap;
}


/* =========================================================
   REDISEÑO DIRECTOR — TARJETAS DE RESUMEN
========================================================= */

.stats-grid { grid-template-columns: repeat(5, 1fr); }

.stat-card {
  position: relative;
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 16px 15px;
  border: 1px solid var(--sigta-borde);
  border-top: 3px solid var(--sigta-borde);
  border-radius: 12px;
  background: var(--sigta-blanco);
  box-shadow: 0 3px 12px rgba(11, 40, 79, .05);
  cursor: pointer;
  transition: box-shadow .2s ease, transform .2s ease;
}
.stat-card:hover { box-shadow: 0 10px 24px rgba(11, 40, 79, .1); transform: translateY(-2px); }

.stat-card.t-azul { border-top-color: #2563C9; }
.stat-card.t-oro { border-top-color: var(--sigta-mostaza); }
.stat-card.t-verde { border-top-color: var(--sigta-exito); }
.stat-card.t-rojo { border-top-color: var(--sigta-error); }

.stat-ico {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 11px;
}
.t-azul .stat-ico { background: #eaf1fc; color: #2563C9; }
.t-oro .stat-ico { background: var(--sigta-mostaza-suave); color: var(--sigta-mostaza-oscuro); }
.t-verde .stat-ico { background: var(--sigta-exito-fondo); color: var(--sigta-exito); }
.t-rojo .stat-ico { background: var(--sigta-error-fondo); color: var(--sigta-error); }

.stat-body { min-width: 0; }
.stat-card .stat-body span {
  display: block;
  padding-right: 34px;
  color: var(--sigta-texto-suave);
  font-size: 10.5px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .2px;
  line-height: 1.25;
}
.stat-card .stat-body strong {
  display: block;
  margin: 3px 0 2px;
  color: var(--sigta-texto);
  font-size: 27px;
  font-weight: 800;
  line-height: 1;
}
.stat-card .stat-body small {
  display: block;
  color: var(--sigta-texto-suave);
  font-size: 11.5px;
  line-height: 1.3;
}

.stat-delta {
  position: absolute;
  top: 13px;
  right: 13px;
  font-size: 11px;
  font-weight: 800;
}
.stat-delta.sube { color: var(--sigta-exito); }
.stat-delta.baja { color: var(--sigta-error); }
.stat-delta.neutro { color: var(--sigta-texto-tenue); }


/* =========================================================
   REDISEÑO DIRECTOR — FILA GRÁFICO / RECIENTES / ACCIONES
========================================================= */

.dash-fila {
  display: grid;
  grid-template-columns: minmax(0, 1.55fr) minmax(0, 1fr) minmax(0, 1fr);
  align-items: start;
  gap: 16px;
  margin: 22px 0;
}

.dash-card {
  background: var(--sigta-blanco);
  border: 1px solid var(--sigta-borde);
  border-radius: 12px;
  padding: 18px;
  box-shadow: 0 3px 12px rgba(11, 40, 79, .05);
}

.dash-card > header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 14px;
}
.dash-card h2 { margin: 0; color: var(--sigta-azul); font-size: 17px; font-weight: 800; }
.dash-card-kicker { display: block; color: var(--sigta-texto-suave); font-size: 10px; font-weight: 900; letter-spacing: 1px; margin-bottom: 3px; }
.dash-card > header p { margin: 3px 0 0; color: var(--sigta-texto-suave); font-size: 12.5px; }

.dash-card > header select {
  height: 32px;
  padding: 0 9px;
  border: 1px solid var(--sigta-borde);
  border-radius: 7px;
  background: var(--sigta-blanco);
  font-family: inherit;
  font-size: 12px;
  color: var(--sigta-texto);
  cursor: pointer;
}

.dash-ver {
  flex-shrink: 0;
  border: 0;
  background: transparent;
  color: var(--sigta-azul-medio);
  font-family: inherit;
  font-size: 12.5px;
  font-weight: 700;
  cursor: pointer;
}
.dash-ver:hover { text-decoration: underline; }

.dash-vacio { margin: 0; padding: 26px 8px; text-align: center; color: var(--sigta-texto-suave); font-size: 13px; }


/* ---------- GRÁFICO ---------- */
.grafico-caja { position: relative; }

.grafico-svg {
  width: 100%;
  height: 210px;
  display: block;
  overflow: visible;
}

.g-rejilla line { stroke: var(--sigta-borde-suave); stroke-width: 1; }
.g-rejilla text { fill: var(--sigta-texto-tenue); font-size: 10px; }
.g-eje-x { fill: var(--sigta-texto-suave); font-size: 10px; }

.g-linea { fill: none; stroke-width: 2; stroke-linecap: round; stroke-linejoin: round; }
.g-linea.g-reg { stroke: #2563C9; }
.g-linea.g-apr { stroke: #A87F00; }

.g-punto { stroke: var(--sigta-blanco); stroke-width: 1.5; }
.g-punto.g-reg { fill: #2563C9; }
.g-punto.g-apr { fill: #A87F00; }
.g-punto.activo { r: 5.5; }

.g-cross { stroke: var(--sigta-texto-tenue); stroke-width: 1; stroke-dasharray: 3 3; }

.grafico-tip {
  position: absolute;
  top: 6px;
  transform: translateX(-50%);
  pointer-events: none;
  background: var(--sigta-azul-oscuro);
  color: #fff;
  border-radius: 8px;
  padding: 7px 10px;
  font-size: 11.5px;
  white-space: nowrap;
  box-shadow: 0 6px 16px rgba(0, 0, 0, .25);
}
.grafico-tip strong { display: block; margin-bottom: 3px; font-size: 12px; }
.grafico-tip span { display: flex; align-items: center; gap: 6px; }

.grafico-leyenda {
  display: flex;
  gap: 18px;
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px solid var(--sigta-borde-suave);
  font-size: 12.5px;
  color: var(--sigta-texto-suave);
}
.grafico-leyenda span { display: flex; align-items: center; gap: 7px; }

.pt { width: 10px; height: 10px; border-radius: 3px; flex-shrink: 0; }
.pt-reg { background: #2563C9; }
.pt-apr { background: #A87F00; }


/* ---------- ACTIVIDADES RECIENTES ---------- */
.recientes-lista { list-style: none; margin: 0; padding: 0; }
.recientes-lista li {
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 10px 0;
  border-bottom: 1px solid var(--sigta-borde-suave);
}
.recientes-lista li:last-child { border-bottom: 0; }
.rec-ico {
  flex-shrink: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}
.rec-ico.tono-ok { background: var(--sigta-exito-fondo); color: var(--sigta-exito); }
.rec-ico.tono-mal { background: var(--sigta-error-fondo); color: var(--sigta-error); }
.rec-ico.tono-espera { background: var(--sigta-mostaza-suave); color: var(--sigta-mostaza-oscuro); }
.rec-ico.tono-info { background: #eaf1fc; color: #2563C9; }
.recientes-lista li div { flex: 1; min-width: 0; }
.recientes-lista li strong { display: block; font-size: 13px; color: var(--sigta-texto); }
.recientes-lista li span { display: block; font-size: 12px; color: var(--sigta-texto-suave); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.recientes-lista li small { flex-shrink: 0; font-size: 11.5px; color: var(--sigta-texto-tenue); }


/* ---------- ACCIONES RÁPIDAS ---------- */
.dash-acciones .accion {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 11px;
  padding: 11px;
  margin-bottom: 8px;
  border: 1px solid var(--sigta-borde-suave);
  border-radius: 10px;
  background: var(--sigta-blanco);
  text-align: left;
  cursor: pointer;
  transition: border-color .18s ease, background .18s ease;
}
.dash-acciones .accion:last-child { margin-bottom: 0; }
.dash-acciones .accion:hover { border-color: var(--sigta-azul-medio); background: var(--sigta-azul-tenue); }
.dash-acciones .accion i {
  flex-shrink: 0;
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 9px;
}
.dash-acciones .a-azul i { background: #eaf1fc; color: #2563C9; }
.dash-acciones .a-oro i { background: var(--sigta-mostaza-suave); color: var(--sigta-mostaza-oscuro); }
.dash-acciones .accion div { flex: 1; min-width: 0; }
.dash-acciones .accion strong { display: block; font-size: 13px; color: var(--sigta-texto); }
.dash-acciones .accion span { display: block; font-size: 11.5px; color: var(--sigta-texto-suave); }
.dash-acciones .accion b { flex-shrink: 0; color: var(--sigta-texto-tenue); font-size: 18px; }


/* =========================================================
   REDISEÑO DIRECTOR — TABLA DE PENDIENTES
========================================================= */

.dash-tabla { margin-bottom: 10px; }

.tabla-scroll { overflow-x: auto; }

.dash-tabla table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
}
.dash-tabla th {
  text-align: left;
  padding: 10px 12px;
  color: var(--sigta-texto-suave);
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: .3px;
  border-bottom: 1px solid var(--sigta-borde);
  white-space: nowrap;
}
.dash-tabla td {
  padding: 12px;
  color: var(--sigta-texto);
  border-bottom: 1px solid var(--sigta-borde-suave);
}
.dash-tabla tbody tr:last-child td { border-bottom: 0; }
.dash-tabla tbody tr:hover td { background: var(--sigta-azul-tenue); }
.dash-tabla .cod { font-weight: 700; color: var(--sigta-azul); white-space: nowrap; }
.dash-tabla .num { text-align: right; white-space: nowrap; }

.pill-pend {
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 4px 9px;
  border-radius: 20px;
  background: var(--sigta-mostaza-suave);
  color: var(--sigta-alerta);
  font-size: 11.5px;
  font-weight: 700;
  white-space: nowrap;
}

.btn-revisar {
  border: 1px solid var(--sigta-borde);
  border-radius: 7px;
  background: var(--sigta-blanco);
  color: var(--sigta-azul);
  font-family: inherit;
  font-size: 12px;
  font-weight: 700;
  padding: 6px 12px;
  cursor: pointer;
}
.btn-revisar:hover { background: var(--sigta-azul); color: #fff; border-color: var(--sigta-azul); }


/* =========================================================
   REDISEÑO DIRECTOR — RESPONSIVE
========================================================= */

@media (max-width: 1180px) {
  .dash-fila { grid-template-columns: 1fr 1fr; }
  .dash-grafico { grid-column: 1 / -1; }
  .stats-grid { grid-template-columns: repeat(3, 1fr); }
}

@media (max-width: 820px) {
  .dash-fila { grid-template-columns: 1fr; }
  .stats-grid { grid-template-columns: 1fr 1fr; }
  .dash-strip { flex-wrap: wrap; }
  .dash-search { order: 3; flex-basis: 100%; }
}

</style>