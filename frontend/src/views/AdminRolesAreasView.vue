<template>

  <div class="layout">

    <!-- =====================================================
         MENÚ ADMIN ÚNICO
    ====================================================== -->

    <SuperuserMenu />


    <!-- =====================================================
         CONTENIDO
    ====================================================== -->

    <main class="content">

      <!-- =================================================
           ENCABEZADO
      ================================================== -->

      <header class="page-header">

        <div>

          <h1>
            Roles, permisos y áreas
          </h1>

          <p>
            Administre la estructura organizacional
            y determine qué puede visualizar y ejecutar
            cada rol dentro de SIA.
          </p>

        </div>

      
        <UsuarioHeader @actualizar="cargarTodo" />
      </header>


      <!-- =================================================
           MENSAJES
      ================================================== -->

      <div
        v-if="mensaje"
        :class="[
          'message',
          mensajeError
            ? 'error'
            : 'success'
        ]"
      >
        {{ mensaje }}
      </div>


      <!-- =================================================
           RESUMEN
      ================================================== -->

      <section class="summary-grid">

        <article class="summary-card">
          <span class="sc-icon" style="background:#e8f1fd;color:#2f6fd0" aria-hidden="true">
            <IconoSigta nombre="usuarios" :tamano="22" />
          </span>
          <div class="sc-body">
            <span>Roles</span>
            <strong>{{ roles.length }}</strong>
            <small>Registrados en SIA</small>
          </div>
        </article>


        <article class="summary-card">
          <span class="sc-icon" style="background:#fdf2d4;color:#c79a1e" aria-hidden="true">
            <IconoSigta nombre="llave" :tamano="22" />
          </span>
          <div class="sc-body">
            <span>Permisos</span>
            <strong>{{ permisos.length }}</strong>
            <small>Acciones controladas</small>
          </div>
        </article>


        <article class="summary-card">
          <span class="sc-icon" style="background:#e8f1fd;color:#2f6fd0" aria-hidden="true">
            <IconoSigta nombre="edificio" :tamano="22" />
          </span>
          <div class="sc-body">
            <span>Áreas</span>
            <strong>{{ areas.length }}</strong>
            <small>Áreas institucionales</small>
          </div>
        </article>


        <article class="summary-card">
          <span class="sc-icon" style="background:#fdf2d4;color:#c79a1e" aria-hidden="true">
            <IconoSigta nombre="escudo" :tamano="22" />
          </span>
          <div class="sc-body">
            <span>Roles activos</span>
            <strong>{{ rolesActivos }}</strong>
            <small>Disponibles para usuarios</small>
          </div>
        </article>

      </section>


      <!-- =================================================
           PESTAÑAS
      ================================================== -->

      <section class="tabs">

        <button
          :class="{
            active: pestaña === 'roles'
          }"
          @click="pestaña = 'roles'"
        >
          <IconoSigta nombre="usuarios" :tamano="17" />
          Roles
        </button>


        <button
          :class="{
            active: pestaña === 'permisos'
          }"
          @click="pestaña = 'permisos'"
        >
          <IconoSigta nombre="llave" :tamano="17" />
          Permisos
        </button>


        <button
          :class="{
            active: pestaña === 'areas'
          }"
          @click="pestaña = 'areas'"
        >
          <IconoSigta nombre="edificio" :tamano="17" />
          Áreas
        </button>

      </section>


      <!-- =================================================
           CARGANDO
      ================================================== -->

      <div
        v-if="cargando"
        class="loading"
      >
        Cargando configuración...
      </div>


      <!-- =================================================
           PESTAÑA ROLES
      ================================================== -->

      <section
        v-else-if="pestaña === 'roles'"
        class="panel"
      >

        <div class="panel-header">

          <div class="ph-title">

            <span class="ph-icon" aria-hidden="true">
              <IconoSigta nombre="usuarios" :tamano="22" />
            </span>

            <div>

              <span class="section-label">
                CONTROL DE ACCESO
              </span>

              <h2>
                Roles del sistema
              </h2>

              <p>
                Cada usuario recibe uno o más roles.
                Los permisos se asignan al rol,
                no directamente a cada usuario.
              </p>

            </div>

          </div>


          <button
            class="yellow-button"
            @click="nuevoRol"
          >
            <IconoSigta nombre="mas" :tamano="16" />
            Nuevo rol
          </button>

        </div>


        <div class="role-grid">

          <article
            v-for="rol in roles"
            :key="rol.id"
            class="role-card"
          >

            <div class="role-card-header">

              <span class="role-icon" aria-hidden="true">
                <IconoSigta :nombre="iconoRol(rol.codigo)" :tamano="20" />
              </span>

              <div class="role-card-title">

                <span class="role-code">
                  {{ rol.codigo }}
                </span>

                <h3>
                  {{ rol.nombre }}
                </h3>

              </div>


              <span
                :class="[
                  'status-badge',
                  rol.activo
                    ? 'active'
                    : 'inactive'
                ]"
              >
                {{
                  rol.activo
                    ? 'Activo'
                    : 'Inactivo'
                }}
              </span>

            </div>


            <p class="role-description">
              {{
                rol.descripcion
                ||
                'Sin descripción registrada.'
              }}
            </p>


            <div class="role-info">

              <div class="ri-item">

                <span class="ri-icon" aria-hidden="true">
                  <IconoSigta nombre="globo" :tamano="16" />
                </span>

                <div>
                  <span>Tipo</span>
                  <strong>
                    {{
                      rol.es_global
                        ? 'Global'
                        : 'Por área'
                    }}
                  </strong>
                </div>

              </div>


              <div class="ri-item">

                <span class="ri-icon" aria-hidden="true">
                  <IconoSigta nombre="llave" :tamano="16" />
                </span>

                <div>
                  <span>Permisos</span>
                  <strong>
                    {{
                      rol.cantidad_permisos
                      ??
                      cantidadPermisosRol(
                        rol.id
                      )
                    }}
                  </strong>
                </div>

              </div>

            </div>


            <div class="role-actions">

              <button
                class="secondary-button"
                @click="editarRol(rol)"
              >
                <IconoSigta nombre="editar" :tamano="15" />
                Editar
              </button>


              <button
                class="blue-button"
                @click="
                  abrirPermisosRol(
                    rol
                  )
                "
              >
                <IconoSigta nombre="llave" :tamano="15" />
                Administrar permisos
              </button>

            </div>

          </article>


          <div
            v-if="roles.length === 0"
            class="empty"
          >
            No existen roles registrados.
          </div>

        </div>

      </section>


      <!-- =================================================
           PESTAÑA PERMISOS
      ================================================== -->

      <section
        v-else-if="pestaña === 'permisos'"
        class="panel"
      >

        <div class="panel-header">

          <div class="ph-title">

            <span class="ph-icon" aria-hidden="true">
              <IconoSigta nombre="llave" :tamano="22" />
            </span>

            <div>

              <span class="section-label">
                MATRIZ DE PERMISOS
              </span>

              <h2>
                Permisos de SIA
              </h2>

              <p>
                Los nombres de las acciones están alineados
                con las actividades de los procesos.
              </p>

            </div>

          </div>

        </div>


        <!-- BUSCADOR -->

        <div class="permission-filters">

          <div class="pf-search">
            <IconoSigta nombre="buscar" :tamano="16" />
            <input
              v-model="buscarPermiso"
              placeholder="Buscar permiso por nombre o código..."
            />
          </div>


          <select
            v-model="filtroModulo"
          >

            <option value="">
              Todos los módulos
            </option>

            <option value="GENERAL">
              General
            </option>

            <option value="AUTOSERVICIO">
              Portal Solicitante
            </option>

            <option value="SOPORTE">
              Soporte Técnico
            </option>

            <option value="MANTENIMIENTO">
              Mantenimiento
            </option>

            <option value="COMPRAS">
              Compras
            </option>

            <option value="ADMINISTRACION">
              Administración
            </option>

            <option value="AUDITORIA">
              Auditoría
            </option>

            <option value="CONFIGURACION">
              Configuración
            </option>

          </select>

        </div>


        <!-- PERMISOS AGRUPADOS -->

        <div
          v-for="grupo in permisosAgrupados"
          :key="grupo.modulo"
          class="permission-group"
        >

          <div class="permission-group-header">

            <div>

              <span>
                MÓDULO
              </span>

              <h3>
                {{ grupo.nombre }}
              </h3>

            </div>


            <strong>
              {{ grupo.permisos.length }}
            </strong>

          </div>


          <div class="permission-list">

            <article
              v-for="permiso in grupo.permisos"
              :key="permiso.id"
              class="permission-row"
            >

              <div>

                <strong>
                  {{ permiso.nombre }}
                </strong>

                <p>
                  {{
                    permiso.descripcion
                    ||
                    'Sin descripción.'
                  }}
                </p>

              </div>


              <span
                :class="[
                  'status-badge',
                  permiso.activo
                    ? 'active'
                    : 'inactive'
                ]"
              >
                {{
                  permiso.activo
                    ? 'Activo'
                    : 'Inactivo'
                }}
              </span>

            </article>

          </div>

        </div>


        <div
          v-if="permisosFiltrados.length === 0"
          class="empty"
        >
          No se encontraron permisos.
        </div>

      </section>


      <!-- =================================================
           PESTAÑA ÁREAS
      ================================================== -->

      <section
        v-else
        class="panel"
      >

        <div class="panel-header">

          <div class="ph-title">

            <span class="ph-icon" aria-hidden="true">
              <IconoSigta nombre="edificio" :tamano="22" />
            </span>

            <div>

              <span class="section-label">
                ESTRUCTURA ORGANIZACIONAL
              </span>

              <h2>
                Áreas institucionales
              </h2>

              <p>
                Las áreas permiten identificar la unidad
                organizacional a la que pertenece cada usuario.
              </p>

            </div>

          </div>


          <button
            class="yellow-button"
            @click="nuevaArea"
          >
            <IconoSigta nombre="mas" :tamano="16" />
            Nueva área
          </button>

        </div>


        <div class="area-table">

          <div class="area-header">

            <span>
              Código
            </span>

            <span>
              Área
            </span>

            <span>
              Descripción
            </span>

            <span>
              Estado
            </span>

            <span>
              Acción
            </span>

          </div>


          <div
            v-for="area in areas"
            :key="area.id"
            class="area-row"
          >

            <strong>
              {{ area.codigo }}
            </strong>


            <span>
              {{ area.nombre }}
            </span>


            <span>
              {{
                area.descripcion
                ||
                '-'
              }}
            </span>


            <span>

              <span
                :class="[
                  'status-badge',
                  area.activo
                    ? 'active'
                    : 'inactive'
                ]"
              >
                {{
                  area.activo
                    ? 'Activa'
                    : 'Inactiva'
                }}
              </span>

            </span>


            <span>

              <button
                class="secondary-button"
                @click="editarArea(area)"
              >
                Editar
              </button>

            </span>

          </div>


          <div
            v-if="areas.length === 0"
            class="empty"
          >
            No existen áreas registradas.
          </div>

        </div>

      </section>

    </main>


    <!-- =====================================================
         MODAL ROL
    ====================================================== -->

    <div
      v-if="modalRol"
      class="overlay"
      @click.self="cerrarModalRol"
    >

      <section class="modal">

        <div class="modal-header">

          <div>

            <span>
              CONFIGURACIÓN DEL ROL
            </span>

            <h2>
              {{
                rolId
                  ? 'Editar rol'
                  : 'Nuevo rol'
              }}
            </h2>

          </div>


          <button
            type="button"
            class="close-button"
            @click="cerrarModalRol"
          >
            ×
          </button>

        </div>


        <form
          @submit.prevent="guardarRol"
        >

          <div class="field">

            <label>
              Código
            </label>

            <input
              v-model="formRol.codigo"
              maxlength="50"
              placeholder="Ej.: JEFE_UTIC"
              required
            />

            <small>
              Utilice un código claro relacionado
              con el rol institucional.
            </small>

          </div>


          <div class="field">

            <label>
              Nombre
            </label>

            <input
              v-model="formRol.nombre"
              maxlength="100"
              placeholder="Ej.: Jefe de UTIC"
              required
            />

          </div>


          <div class="field">

            <label>
              Descripción
            </label>

            <textarea
              v-model="formRol.descripcion"
              placeholder="Describa la responsabilidad del rol..."
            ></textarea>

          </div>


          <label class="check-card">

            <input
              v-model="formRol.es_global"
              type="checkbox"
            />

            <div>

              <strong>
                Rol global
              </strong>

              <span>
                No necesita estar asociado
                a un área específica.
              </span>

            </div>

          </label>


          <label class="check-card">

            <input
              v-model="formRol.activo"
              type="checkbox"
            />

            <div>

              <strong>
                Rol activo
              </strong>

              <span>
                Podrá asignarse a usuarios.
              </span>

            </div>

          </label>


          <div class="modal-actions">

            <button
              type="button"
              class="secondary-button"
              @click="cerrarModalRol"
            >
              Cancelar
            </button>


            <button
              type="submit"
              class="primary-button"
              :disabled="guardando || mostrarGuardadoOk"
            >
              {{ guardando ? 'Guardando…' : 'Guardar rol' }}
            </button>

          </div>

        </form>

      </section>

    </div>


    <!-- =====================================================
         MODAL ÁREA
    ====================================================== -->

    <div
      v-if="modalArea"
      class="overlay"
      @click.self="cerrarModalArea"
    >

      <section class="modal">

        <div class="modal-header">

          <div>

            <span>
              ESTRUCTURA ORGANIZACIONAL
            </span>

            <h2>
              {{
                areaId
                  ? 'Editar área'
                  : 'Nueva área'
              }}
            </h2>

          </div>


          <button
            type="button"
            class="close-button"
            @click="cerrarModalArea"
          >
            ×
          </button>

        </div>


        <form
          @submit.prevent="guardarArea"
        >

          <div class="field">

            <label>
              Código
            </label>

            <input
              v-model="formArea.codigo"
              maxlength="30"
              placeholder="Ej.: UTIC"
              required
            />

          </div>


          <div class="field">

            <label>
              Nombre
            </label>

            <input
              v-model="formArea.nombre"
              maxlength="100"
              placeholder="Ej.: Unidad de Tecnologías de Información"
              required
            />

          </div>


          <div class="field">

            <label>
              Descripción
            </label>

            <textarea
              v-model="formArea.descripcion"
              placeholder="Descripción del área..."
            ></textarea>

          </div>


          <label class="check-card">

            <input
              v-model="formArea.activo"
              type="checkbox"
            />

            <div>

              <strong>
                Área activa
              </strong>

              <span>
                Disponible para asignación
                de usuarios y requerimientos.
              </span>

            </div>

          </label>


          <div class="modal-actions">

            <button
              type="button"
              class="secondary-button"
              @click="cerrarModalArea"
            >
              Cancelar
            </button>


            <button
              type="submit"
              class="primary-button"
              :disabled="guardando || mostrarGuardadoOk"
            >
              {{ guardando ? 'Guardando…' : 'Guardar área' }}
            </button>

          </div>

        </form>

      </section>

    </div>


    <!-- CONFIRMACIÓN DE CAMBIO DE ESTADO DEL ÁREA -->

    <div
      v-if="modalConfirmacionArea"
      class="overlay confirmation-overlay"
      @click.self="cerrarConfirmacionArea"
    >

      <section class="modal area-confirmation-modal">

        <div
          :class="[
            'area-confirmation-icon',
            accionEstadoArea
          ]"
        >
          !
        </div>

        <h2>
          {{ accionEstadoArea === 'inactivar' ? 'Inactivar área' : 'Activar área' }}
        </h2>

        <p class="area-confirmation-question">
          {{ accionEstadoArea === 'inactivar'
            ? '¿Está seguro de que desea inactivar esta área?'
            : '¿Está seguro de que desea activar esta área?' }}
        </p>

        <dl class="area-confirmation-data">
          <div>
            <dt>Área:</dt>
            <dd>{{ formArea.nombre.trim() }}</dd>
          </div>
        </dl>

        <div :class="['area-confirmation-notice', accionEstadoArea]">
          {{ accionEstadoArea === 'inactivar'
            ? 'El área dejará de estar disponible para nuevas asignaciones de usuarios y requerimientos.'
            : 'El área volverá a estar disponible para asignación de usuarios y requerimientos.' }}
        </div>

        <div class="modal-actions">
          <button
            type="button"
            class="secondary-button"
            :disabled="guardando"
            @click="cerrarConfirmacionArea"
          >
            Cancelar
          </button>

          <button
            type="button"
            :class="accionEstadoArea === 'inactivar'
              ? 'area-disable-button'
              : 'area-enable-button'"
            :disabled="guardando"
            @click="confirmarCambioEstadoArea"
          >
            {{ guardando
              ? 'Guardando...'
              : (accionEstadoArea === 'inactivar'
                  ? 'Inactivar área'
                  : 'Activar área') }}
          </button>
        </div>

      </section>

    </div>


    <!-- =====================================================
         MODAL PERMISOS DEL ROL
    ====================================================== -->

    <div
      v-if="modalPermisos"
      class="overlay"
      @click.self="cerrarModalPermisos"
    >

      <section class="modal permissions-modal">

        <div class="modal-header">

          <div>

            <span>
              MATRIZ DE PERMISOS
            </span>

            <h2>
              {{ rolSeleccionado?.nombre }}
            </h2>

            <p>
              {{ rolSeleccionado?.codigo }}
            </p>

          </div>


          <button
            type="button"
            class="close-button"
            @click="cerrarModalPermisos"
          >
            ×
          </button>

        </div>


        <div class="permission-warning">

          Los permisos determinan qué puede visualizar
          y ejecutar este rol dentro del sistema.

        </div>


        <div class="role-permissions-scroll">

          <section
            v-for="grupo in permisosPorModuloTodos"
            :key="grupo.modulo"
            class="role-permission-group"
          >

            <div class="role-permission-title">

              <h3>
                {{ grupo.nombre }}
              </h3>

              <span>
                {{ grupo.permisos.length }}
              </span>

            </div>


            <label
              v-for="permiso in grupo.permisos"
              :key="permiso.id"
              class="permission-checkbox"
            >

              <input
                type="checkbox"
                :checked="
                  permisoAsignado(
                    permiso.id
                  )
                "
                :disabled="
                  modificandoPermiso === permiso.id
                "
                @change="
                  cambiarPermisoRol(
                    permiso,
                    $event.target.checked
                  )
                "
              />


              <div>

                <strong>
                  {{ permiso.nombre }}
                </strong>

                <span>
                  {{ permiso.codigo }}
                </span>

                <p>
                  {{ permiso.descripcion }}
                </p>

              </div>

            </label>

          </section>

        </div>


        <div class="modal-actions">

          <button
            type="button"
            class="primary-button"
            @click="cerrarModalPermisos"
          >
            Finalizar
          </button>

        </div>

      </section>

    </div>


    <!-- =====================================================
         TARJETA DE GUARDADO (componente compartido)
    ====================================================== -->

    <TarjetaGuardado :visible="mostrarGuardadoOk" :texto="textoGuardado" @cerrar="ocultarGuardado" />

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

import SuperuserMenu
  from '../components/SuperuserMenu.vue'

import IconoSigta
  from '../components/IconoSigta.vue'

import TarjetaGuardado
  from '../components/TarjetaGuardado.vue'

import { usarGuardado }
  from '../utils/guardado.js'


const router =
  useRouter()


/* Ícono representativo por tipo de rol */
function iconoRol(codigo) {
  const c = String(codigo || '').toUpperCase()
  if (c.includes('SUPER')) return 'corona'
  if (c.includes('DAF') || c.includes('TESORER') || c.includes('FINANC')) return 'reporte'
  if (c.includes('ADMIN') || c.includes('DIRECTOR')) return 'perfil'
  if (c.includes('UTIC') || c.includes('SOPORTE') || c.includes('AGENTE')) return 'soporte'
  if (c.includes('MANTEN') || c.includes('SERVICIOS') || c.includes('AUXILIAR')) return 'mantenimiento'
  if (c.includes('COMPRA') || c.includes('ALMACEN')) return 'compras'
  if (c.includes('SOLICITANTE')) return 'solicitudes'
  return 'roles'
}


/* =========================================================
   DATOS
========================================================= */

const roles =
  ref([])

const areas =
  ref([])

const permisos =
  ref([])

const rolPermisos =
  ref([])


/* =========================================================
   INTERFAZ
========================================================= */

const pestaña =
  ref('roles')

const cargando =
  ref(true)

const guardando =
  ref(false)

/* Tarjeta gelatinosa de "guardado" (componente + helper compartidos) */
const {
  mostrar: mostrarGuardadoOk,
  texto: textoGuardado,
  animar: animarGuardado,
  ocultar: ocultarGuardado,
} = usarGuardado()

const mensaje =
  ref('')

const mensajeError =
  ref(false)


/* =========================================================
   MODALES
========================================================= */

const modalRol =
  ref(false)

const modalArea =
  ref(false)

const modalPermisos =
  ref(false)

const modalConfirmacionArea =
  ref(false)

const estadoOriginalArea =
  ref(null)

const accionEstadoArea =
  ref('')


const rolId =
  ref(null)

const areaId =
  ref(null)

const rolSeleccionado =
  ref(null)


/* =========================================================
   PERMISOS
========================================================= */

const buscarPermiso =
  ref('')

const filtroModulo =
  ref('')

const modificandoPermiso =
  ref(null)


/* =========================================================
   FORMULARIOS
========================================================= */

const formRol =
  reactive({

    codigo: '',

    nombre: '',

    descripcion: '',

    es_global: false,

    activo: true,
  })


const formArea =
  reactive({

    codigo: '',

    nombre: '',

    descripcion: '',

    activo: true,
  })

const codigoAreaFormulario = computed(() =>
  formArea.codigo
    .trim()
    .toUpperCase()
    .replace(/\s+/g, '_')
)


/* =========================================================
   TOKEN
========================================================= */

const obtenerToken = () =>
  localStorage.getItem(
    'sigta_token'
  )


function headers() {

  return {

    'Content-Type':
      'application/json',

    Accept:
      'application/json',

    Authorization:
      `Token ${obtenerToken()}`,
  }
}


/* =========================================================
   INICIO
========================================================= */

onMounted(
  async () => {

    if (
      !obtenerToken()
    ) {

      router.push(
        '/login'
      )

      return
    }


    await cargarTodo()
  }
)


/* =========================================================
   NORMALIZAR LISTAS
========================================================= */

function normalizarLista(
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
   CARGAR TODO
========================================================= */

async function cargarTodo() {

  cargando.value = true


  try {

    const [
      rolesRes,
      areasRes,
      permisosRes,
      rolPermisosRes
    ] =
      await Promise.all([

        fetch(
          '/api/usuarios/roles/',
          {
            headers:
              headers()
          }
        ),

        fetch(
          '/api/usuarios/areas/',
          {
            headers:
              headers()
          }
        ),

        fetch(
          '/api/usuarios/permisos/',
          {
            headers:
              headers()
          }
        ),

        fetch(
          '/api/usuarios/rol-permisos/',
          {
            headers:
              headers()
          }
        ),

      ])


    const respuestas = [
      rolesRes,
      areasRes,
      permisosRes,
      rolPermisosRes
    ]


    if (
      respuestas.some(
        r =>
          r.status === 401
          ||
          r.status === 403
      )
    ) {

      cerrarSesion()

      return
    }


    if (
      !rolesRes.ok
      ||
      !areasRes.ok
      ||
      !permisosRes.ok
      ||
      !rolPermisosRes.ok
    ) {

      throw new Error(
        'No fue posible cargar la configuración.'
      )
    }


    roles.value =
      normalizarLista(
        await rolesRes.json()
      )


    areas.value =
      normalizarLista(
        await areasRes.json()
      )


    permisos.value =
      normalizarLista(
        await permisosRes.json()
      )


    rolPermisos.value =
      normalizarLista(
        await rolPermisosRes.json()
      )


  } catch (error) {

    console.error(
      error
    )


    mostrarMensaje(
      'No fue posible cargar roles, permisos y áreas.',
      true
    )

  } finally {

    cargando.value = false
  }
}


/* =========================================================
   CONTADORES
========================================================= */

const rolesActivos =
  computed(() => {

    return roles.value.filter(
      rol =>
        rol.activo
    ).length
  })


function cantidadPermisosRol(
  rolIdValor
) {

  return rolPermisos.value.filter(
    rp =>
      Number(
        rp.rol
      )
      ===
      Number(
        rolIdValor
      )
      &&
      rp.activo !== false
  ).length
}


/* =========================================================
   PERMISOS FILTRADOS
========================================================= */

const permisosFiltrados =
  computed(() => {

    const buscar =
      buscarPermiso.value
        .trim()
        .toLowerCase()


    return permisos.value.filter(
      permiso => {

        const coincideModulo =
          !filtroModulo.value
          ||
          permiso.modulo
          ===
          filtroModulo.value


        const coincideTexto =
          !buscar
          ||
          permiso.nombre
            ?.toLowerCase()
            .includes(
              buscar
            )
          ||
          permiso.codigo
            ?.toLowerCase()
            .includes(
              buscar
            )
          ||
          permiso.descripcion
            ?.toLowerCase()
            .includes(
              buscar
            )


        return (
          coincideModulo
          &&
          coincideTexto
        )
      }
    )
  })


/* =========================================================
   AGRUPAR PERMISOS
========================================================= */

const nombresModulo = {

  GENERAL:
    'General',

  AUTOSERVICIO:
    'Portal Solicitante',

  SOPORTE:
    'Soporte Técnico',

  MANTENIMIENTO:
    'Mantenimiento',

  COMPRAS:
    'Compras',

  ADMINISTRACION:
    'Administración',

  AUDITORIA:
    'Auditoría',

  CONFIGURACION:
    'Configuración',
}


function agruparPermisos(
  lista
) {

  const grupos = {}


  for (
    const permiso
    of lista
  ) {

    const modulo =
      permiso.modulo
      ||
      'GENERAL'


    if (
      !grupos[modulo]
    ) {

      grupos[modulo] = {
        modulo,

        nombre:
          permiso.modulo_nombre
          ||
          nombresModulo[modulo]
          ||
          modulo,

        permisos: [],
      }
    }


    grupos[modulo]
      .permisos
      .push(
        permiso
      )
  }


  return Object.values(
    grupos
  )
}


const permisosAgrupados =
  computed(() => {

    return agruparPermisos(
      permisosFiltrados.value
    )
  })


const permisosPorModuloTodos =
  computed(() => {

    return agruparPermisos(
      permisos.value.filter(
        permiso =>
          permiso.activo !== false
      )
    )
  })


/* =========================================================
   ROL
========================================================= */

function nuevoRol() {

  rolId.value = null


  Object.assign(
    formRol,
    {
      codigo: '',

      nombre: '',

      descripcion: '',

      es_global: false,

      activo: true,
    }
  )


  modalRol.value = true
}


function editarRol(
  rol
) {

  rolId.value =
    rol.id


  Object.assign(
    formRol,
    {
      codigo:
        rol.codigo
        ||
        '',

      nombre:
        rol.nombre
        ||
        '',

      descripcion:
        rol.descripcion
        ||
        '',

      es_global:
        Boolean(
          rol.es_global
        ),

      activo:
        Boolean(
          rol.activo
        ),
    }
  )


  modalRol.value = true
}


function cerrarModalRol() {

  modalRol.value = false

  rolId.value = null
}


async function guardarRol() {

  guardando.value = true


  try {

    let url =
      '/api/usuarios/roles/'


    let method =
      'POST'


    const editando =
      Boolean(
        rolId.value
      )


    if (
      editando
    ) {

      url +=
        `${rolId.value}/`

      method =
        'PATCH'
    }


    const respuesta =
      await fetch(
        url,
        {
          method,

          headers:
            headers(),

          body:
            JSON.stringify({
              codigo:
                formRol.codigo
                  .trim()
                  .toUpperCase()
                  .replace(
                    /\s+/g,
                    '_'
                  ),

              nombre:
                formRol.nombre
                  .trim(),

              descripcion:
                formRol.descripcion
                  .trim(),

              es_global:
                formRol.es_global,

              activo:
                formRol.activo,
            })
        }
      )


    const datos =
      await leerJson(
        respuesta
      )


    if (
      !respuesta.ok
    ) {

      mostrarMensaje(
        obtenerError(
          datos
        ),
        true
      )

      return
    }


    guardando.value = false

    await animarGuardado(
      editando
        ? 'Rol actualizado'
        : 'Rol creado'
    )


    modalRol.value =
      false


    mostrarMensaje(
      editando
        ? 'Rol actualizado correctamente.'
        : 'Rol creado correctamente.'
    )


    await cargarTodo()


  } catch (error) {

    console.error(
      error
    )


    mostrarMensaje(
      'No fue posible guardar el rol.',
      true
    )

  } finally {

    guardando.value = false
    mostrarGuardadoOk.value = false
  }
}


/* =========================================================
   ÁREA
========================================================= */

function nuevaArea() {

  areaId.value = null

  estadoOriginalArea.value = null


  Object.assign(
    formArea,
    {
      codigo: '',

      nombre: '',

      descripcion: '',

      activo: true,
    }
  )


  modalArea.value = true
}


function editarArea(
  area
) {

  areaId.value =
    area.id

  estadoOriginalArea.value =
    Boolean(area.activo)


  Object.assign(
    formArea,
    {
      codigo:
        area.codigo
        ||
        '',

      nombre:
        area.nombre
        ||
        '',

      descripcion:
        area.descripcion
        ||
        '',

      activo:
        Boolean(
          area.activo
        ),
    }
  )


  modalArea.value = true
}


function cerrarModalArea() {

  modalArea.value = false

  modalConfirmacionArea.value = false

  areaId.value = null

  estadoOriginalArea.value = null

  accionEstadoArea.value = ''
}


async function guardarArea() {

  const editando = Boolean(areaId.value)

  if (
    editando
    && estadoOriginalArea.value !== formArea.activo
  ) {
    accionEstadoArea.value = formArea.activo
      ? 'activar'
      : 'inactivar'
    modalConfirmacionArea.value = true
    return
  }

  await persistirArea()
}


function cerrarConfirmacionArea() {

  if (guardando.value) return

  modalConfirmacionArea.value = false

  accionEstadoArea.value = ''
}


async function confirmarCambioEstadoArea() {

  await persistirArea(accionEstadoArea.value)
}


async function persistirArea(accionEstadoConfirmada = '') {

  guardando.value = true


  try {

    let url =
      '/api/usuarios/areas/'


    let method =
      'POST'


    const editando =
      Boolean(
        areaId.value
      )


    if (
      editando
    ) {

      url +=
        `${areaId.value}/`

      method =
        'PATCH'
    }


    const respuesta =
      await fetch(
        url,
        {
          method,

          headers:
            headers(),

          body:
            JSON.stringify({
              codigo:
                codigoAreaFormulario.value,

              nombre:
                formArea.nombre
                  .trim(),

              descripcion:
                formArea.descripcion
                  .trim(),

              activo:
                formArea.activo,
            })
        }
      )


    const datos =
      await leerJson(
        respuesta
      )


    if (
      !respuesta.ok
    ) {

      mostrarMensaje(
        obtenerError(
          datos
        ),
        true
      )

      return
    }


    guardando.value = false

    await animarGuardado(
      accionEstadoConfirmada === 'inactivar'
        ? 'Área inactivada'
        : accionEstadoConfirmada === 'activar'
          ? 'Área activada'
          : editando
            ? 'Área actualizada'
            : 'Área creada'
    )


    modalConfirmacionArea.value = false

    modalArea.value = false


    mostrarMensaje(
      accionEstadoConfirmada === 'inactivar'
        ? 'Área inactivada correctamente.'
        : accionEstadoConfirmada === 'activar'
          ? 'Área activada correctamente.'
          : editando
            ? 'Área actualizada correctamente.'
            : 'Área creada correctamente.'
    )


    await cargarTodo()


  } catch (error) {

    console.error(
      error
    )


    mostrarMensaje(
      'No fue posible guardar el área.',
      true
    )

  } finally {

    guardando.value = false
    mostrarGuardadoOk.value = false
  }
}


/* =========================================================
   PERMISOS DEL ROL
========================================================= */

function abrirPermisosRol(
  rol
) {

  rolSeleccionado.value =
    rol


  modalPermisos.value =
    true
}


function cerrarModalPermisos() {

  modalPermisos.value =
    false


  rolSeleccionado.value =
    null
}


function permisoAsignado(
  permisoId
) {

  if (
    !rolSeleccionado.value
  ) {

    return false
  }


  return rolPermisos.value.some(
    rp =>

      Number(
        rp.rol
      )
      ===
      Number(
        rolSeleccionado.value.id
      )

      &&

      Number(
        rp.permiso
      )
      ===
      Number(
        permisoId
      )

      &&

      rp.activo !== false
  )
}


function encontrarAsignacion(
  permisoId
) {

  if (
    !rolSeleccionado.value
  ) {

    return null
  }


  return rolPermisos.value.find(
    rp =>

      Number(
        rp.rol
      )
      ===
      Number(
        rolSeleccionado.value.id
      )

      &&

      Number(
        rp.permiso
      )
      ===
      Number(
        permisoId
      )
  )
}


/* =========================================================
   ASIGNAR / QUITAR PERMISO
========================================================= */

async function cambiarPermisoRol(
  permiso,
  asignar
) {

  if (
    !rolSeleccionado.value
  ) {

    return
  }


  modificandoPermiso.value =
    permiso.id


  try {

    if (
      asignar
    ) {

      const respuesta =
        await fetch(
          '/api/usuarios/rol-permisos/',
          {
            method:
              'POST',

            headers:
              headers(),

            body:
              JSON.stringify({
                rol:
                  rolSeleccionado.value.id,

                permiso:
                  permiso.id,

                activo:
                  true,
              })
          }
        )


      const datos =
        await leerJson(
          respuesta
        )


      if (
        !respuesta.ok
      ) {

        throw new Error(
          obtenerError(
            datos
          )
        )
      }


      mostrarMensaje(
        `Permiso "${permiso.nombre}" asignado al rol.`
      )

    } else {

      const asignacion =
        encontrarAsignacion(
          permiso.id
        )


      if (
        !asignacion
      ) {

        return
      }


      const respuesta =
        await fetch(
          `/api/usuarios/rol-permisos/${asignacion.id}/`,
          {
            method:
              'DELETE',

            headers:
              headers(),
          }
        )


      const datos =
        await leerJson(
          respuesta
        )


      if (
        !respuesta.ok
      ) {

        throw new Error(
          obtenerError(
            datos
          )
        )
      }


      mostrarMensaje(
        `Permiso "${permiso.nombre}" retirado del rol.`
      )
    }


    await cargarTodo()


    /* Mantener actualizado rol seleccionado */

    rolSeleccionado.value =
      roles.value.find(
        rol =>
          rol.id
          ===
          rolSeleccionado.value?.id
      )
      ||
      rolSeleccionado.value


  } catch (error) {

    console.error(
      error
    )


    mostrarMensaje(
      error.message
      ||
      'No fue posible modificar el permiso.',
      true
    )


    await cargarTodo()

  } finally {

    modificandoPermiso.value =
      null
  }
}


/* =========================================================
   UTILIDADES
========================================================= */

async function leerJson(
  respuesta
) {

  try {

    return await respuesta.json()

  } catch {

    return {}
  }
}


function obtenerError(
  datos
) {

  if (
    datos.detail
  ) {

    return datos.detail
  }


  if (
    datos.detalle
  ) {

    return datos.detalle
  }


  if (
    datos.mensaje
  ) {

    return datos.mensaje
  }


  const entrada =
    Object.entries(
      datos
      ||
      {}
    )[0]


  if (
    entrada
  ) {

    const [
      campo,
      valor
    ] =
      entrada


    return (
      `${campo}: ${
        Array.isArray(
          valor
        )
          ? valor.join(', ')
          : String(valor)
      }`
    )
  }


  return (
    'Revise la información ingresada.'
  )
}


function mostrarMensaje(
  texto,
  esError = false
) {

  mensaje.value =
    texto


  mensajeError.value =
    esError


  setTimeout(
    () => {

      mensaje.value =
        ''

    },
    4000
  )
}


/* =========================================================
   SESIÓN
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

.layout {

  min-height: 100vh;

  display: flex;

  background: var(--sigta-azul-tenue);

  font-family: var(--sigta-fuente);
}


.content {

  flex: 1;

  min-width: 0;

  padding: 28px;

  overflow-x: hidden;
}


/* =========================================================
   ENCABEZADO
========================================================= */

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 22px;
}


.breadcrumb {

  display: block;

  margin-bottom: 7px;

  color: var(--sigta-texto-suave);

  font-size: 15px;
}


.page-header h1 {

  margin: 0;

  color: var(--sigta-texto);

  font-size: 28px;
}


.page-header p {

  max-width: 780px;

  margin:
    6px
    0
    0;

  color: var(--sigta-texto-suave);

  font-size: 17px;

  line-height: 1.5;
}


/* =========================================================
   MENSAJE
========================================================= */

.message {

  margin-bottom: 17px;

  padding:
    11px
    13px;

  border-radius: 7px;

  font-size: 15px;
}


.message.success {

  background: var(--sigta-exito-fondo);

  color: var(--sigta-exito);
}


.message.error {

  background: var(--sigta-error-fondo);

  color: var(--sigta-error);
}


/* =========================================================
   RESUMEN
========================================================= */

.summary-grid {

  display: grid;

  grid-template-columns:
    repeat(4,1fr);

  gap: 14px;

  margin-bottom: 20px;
}


.summary-card {

  min-height: 110px;

  padding: 17px;

  display: flex;

  align-items: center;

  gap: 14px;

  background: white;

  border-top:
    4px solid var(--sigta-mostaza);

  border-radius: 9px;

  box-shadow:
    0
    3px
    12px
    rgba(0,0,0,.04);
}


.summary-card .sc-icon {

  flex-shrink: 0;

  width: 46px;

  height: 46px;

  display: flex;

  align-items: center;

  justify-content: center;

  border-radius: 12px;
}


.summary-card .sc-body {

  min-width: 0;
}


.summary-card span {

  display: block;

  color: var(--sigta-texto-suave);

  font-size: 14px;

  font-weight: 800;

  text-transform: uppercase;
}


.summary-card strong {

  display: block;

  margin:
    7px
    0
    5px;

  color: var(--sigta-azul);

  font-size: 25px;
}


.summary-card small {

  color: var(--sigta-texto-suave);

  font-size: 14px;
}


/* =========================================================
   TABS
========================================================= */

.tabs {

  display: flex;

  gap: 4px;

  margin-bottom: 15px;

  padding: 5px;

  border-radius: 9px;

  background: var(--sigta-azul-texto-claro);
}


.tabs button {

  min-width: 140px;

  min-height: 38px;

  padding:
    0
    15px;

  display: inline-flex;

  align-items: center;

  justify-content: center;

  gap: 7px;

  border: none;

  border-radius: 7px;

  background: transparent;

  color: var(--sigta-texto-suave);

  font-size: 15px;

  font-weight: 700;

  cursor: pointer;
}

.tabs button .icono-sigta {

  flex-shrink: 0;
}


.tabs button.active {

  background: white;

  color: var(--sigta-azul);

  box-shadow:
    0
    2px
    7px
    rgba(0,0,0,.07);
}


/* =========================================================
   PANEL
========================================================= */

.panel {

  padding: 21px;

  border-top:
    4px solid var(--sigta-mostaza);

  border-radius: 10px;

  background: white;

  box-shadow:
    0
    4px
    14px
    rgba(0,0,0,.05);
}


.panel-header {

  display: flex;

  align-items: flex-start;

  justify-content:
    space-between;

  gap: 15px;

  margin-bottom: 20px;
}


.section-label {

  display: block;

  margin-bottom: 5px;

  color: var(--sigta-texto-suave);

  font-size: 13px;

  font-weight: 900;

  letter-spacing: .8px;
}


.panel-header h2 {

  margin: 0;

  color: var(--sigta-texto);

  font-size: 17px;
}


.panel-header p {

  margin:
    5px
    0
    0;

  color: var(--sigta-texto-suave);

  font-size: 15px;
}


/* =========================================================
   BOTONES
========================================================= */

.yellow-button,
.primary-button,
.blue-button,
.secondary-button {

  min-height: 36px;

  padding:
    0
    12px;

  border-radius: 6px;

  font-size: 14px;

  font-weight: 800;

  cursor: pointer;
}


.yellow-button {

  border: none;

  background: var(--sigta-mostaza);

  color: var(--sigta-azul);
}


.primary-button {

  border: none;

  background: var(--sigta-azul);

  color: white;
}


.blue-button {

  border: 1px solid var(--sigta-azul);

  background: var(--sigta-azul-tenue);

  color: var(--sigta-azul);

  transition: background .15s ease, color .15s ease, transform .15s ease, box-shadow .15s ease;
}

.blue-button:hover {

  background: var(--sigta-azul);

  color: white;

  transform: translateY(-1px);

  box-shadow: 0 4px 10px rgba(0,42,92,.18);
}


.secondary-button {

  border:
    1px solid var(--sigta-borde);

  background: white;

  color: var(--sigta-texto-suave);

  transition: border-color .15s ease, color .15s ease, background .15s ease, transform .15s ease;
}

.secondary-button:hover {

  border-color: var(--sigta-azul);

  color: var(--sigta-azul);

  background: var(--sigta-azul-tenue);

  transform: translateY(-1px);
}


.primary-button:disabled {

  opacity: .55;

  cursor: not-allowed;
}


/* =========================================================
   ROLES
========================================================= */

.role-grid {

  display: grid;

  grid-template-columns:
    repeat(3,1fr);

  gap: 13px;
}


.role-card {

  min-width: 0;

  padding: 15px;

  border:
    1px solid var(--sigta-borde);

  border-radius: 9px;

  background: var(--sigta-azul-tenue);
}


.role-card-header {

  display: flex;

  align-items: flex-start;

  justify-content:
    space-between;

  gap: 10px;
}


.role-card-header .role-icon {

  flex-shrink: 0;

  width: 40px;

  height: 40px;

  display: flex;

  align-items: center;

  justify-content: center;

  border-radius: 10px;

  background: var(--sigta-azul-tenue);

  color: var(--sigta-azul);
}


.role-card-title {

  flex: 1;

  min-width: 0;
}


/* Iconos dentro de botones */
.yellow-button,
.blue-button,
.secondary-button {

  display: inline-flex;

  align-items: center;

  justify-content: center;

  gap: 6px;
}

.yellow-button .icono-sigta,
.blue-button .icono-sigta,
.secondary-button .icono-sigta {

  flex-shrink: 0;
}


/* Encabezado de panel con icono */
.ph-title {

  display: flex;

  align-items: flex-start;

  gap: 12px;
}


.ph-title > .ph-icon {

  flex-shrink: 0;

  width: 44px;

  height: 44px;

  display: flex;

  align-items: center;

  justify-content: center;

  border-radius: 12px;

  background: var(--sigta-azul-tenue);

  color: var(--sigta-azul);
}


/* Fila de datos del rol con icono */
.role-info .ri-item {

  display: flex;

  align-items: center;

  gap: 9px;
}


.role-info .ri-item > .ri-icon {

  flex-shrink: 0;

  width: 30px;

  height: 30px;

  display: flex;

  align-items: center;

  justify-content: center;

  border-radius: 8px;

  background: var(--sigta-azul-tenue);

  color: var(--sigta-azul);
}


.role-code {

  display: block;

  margin-bottom: 4px;

  color: var(--sigta-azul);

  font-size: 13px;

  font-weight: 900;
}


.role-card h3 {

  margin: 0;

  color: var(--sigta-texto);

  font-size: 18px;
}


.role-description {

  min-height: 42px;

  margin:
    9px
    0;

  color: var(--sigta-texto-suave);

  font-size: 14px;

  line-height: 1.45;
}


.role-info {

  display: grid;

  grid-template-columns:
    1fr
    1fr;

  gap: 8px;

  margin-bottom: 12px;

  padding:
    10px
    0;

  border-top:
    1px solid var(--sigta-borde);

  border-bottom:
    1px solid var(--sigta-borde);
}


.role-info span,
.role-info strong {

  display: block;
}


.role-info span {

  color: var(--sigta-texto-suave);

  font-size: 13px;
}


.role-info strong {

  margin-top: 3px;

  color: var(--sigta-azul);

  font-size: 15px;
}


.role-actions {

  display: flex;

  justify-content:
    flex-end;

  gap: 7px;
}


/* =========================================================
   ESTADOS
========================================================= */

.status-badge {

  display: inline-block;

  padding:
    4px
    7px;

  border-radius: 14px;

  font-size: 13px;

  font-weight: 800;
}


.status-badge.active {

  background: var(--sigta-exito-fondo);

  color: var(--sigta-exito);
}


.status-badge.inactive {

  background: var(--sigta-error-fondo);

  color: var(--sigta-error);
}


/* =========================================================
   FILTROS PERMISOS
========================================================= */

.permission-filters {

  display: grid;

  grid-template-columns:
    1fr
    250px;

  gap: 10px;

  margin-bottom: 17px;
}


.permission-filters input,
.permission-filters select {

  height: 40px;

  padding:
    0
    11px;

  border:
    1px solid var(--sigta-borde);

  border-radius: 7px;

  background: white;

  color: var(--sigta-azul);

  font-size: 15px;

  outline: none;
}


.permission-filters .pf-search {

  display: flex;

  align-items: center;

  gap: 8px;

  height: 40px;

  padding: 0 11px;

  border: 1px solid var(--sigta-borde);

  border-radius: 7px;

  background: white;

  color: var(--sigta-texto-suave);
}


.permission-filters .pf-search input {

  height: auto;

  flex: 1;

  min-width: 0;

  padding: 0;

  border: 0;

  border-radius: 0;

  background: transparent;
}


/* =========================================================
   GRUPOS DE PERMISOS
========================================================= */

.permission-group {

  margin-bottom: 16px;

  overflow: hidden;

  border:
    1px solid var(--sigta-borde);

  border-radius: 8px;
}


.permission-group-header {

  display: flex;

  align-items: center;

  justify-content:
    space-between;

  padding:
    12px
    14px;

  background: var(--sigta-azul-tenue);
}


.permission-group-header span {

  display: block;

  color: var(--sigta-texto-suave);

  font-size: 13px;
}


.permission-group-header h3 {

  margin:
    3px
    0
    0;

  color: var(--sigta-texto);

  font-size: 17px;
}


.permission-group-header > strong {

  width: 27px;

  height: 27px;

  display: flex;

  align-items: center;

  justify-content: center;

  border-radius: 50%;

  background: var(--sigta-azul);

  color: white;

  font-size: 14px;
}


.permission-row {

  display: flex;

  align-items: flex-start;

  justify-content:
    space-between;

  gap: 15px;

  padding:
    13px
    14px;

  border-top:
    1px solid var(--sigta-azul-tenue);
}


.permission-row strong {

  color: var(--sigta-azul);

  font-size: 15px;
}


.permission-code {

  display: block;

  margin-top: 4px;

  color: var(--sigta-azul);

  font-size: 13px;

  font-weight: 700;
}


.permission-row p {

  margin:
    5px
    0
    0;

  color: var(--sigta-texto-suave);

  font-size: 14px;
}


/* =========================================================
   ÁREAS
========================================================= */

.area-table {

  overflow-x: auto;
}


.area-header,
.area-row {

  display: grid;

  grid-template-columns:
    150px
    220px
    minmax(280px,1fr)
    120px
    110px;

  gap: 10px;

  align-items: center;

  min-width: 880px;
}


.area-header {

  padding:
    11px
    13px;

  background: var(--sigta-azul-tenue);

  color: var(--sigta-texto-suave);

  font-size: 14px;

  font-weight: 800;

  text-transform: uppercase;
}


.area-row {

  padding:
    13px;

  border-top:
    1px solid var(--sigta-azul-tenue);

  color: var(--sigta-texto-suave);

  font-size: 15px;
}


.area-row > strong {

  color: var(--sigta-azul);
}


/* =========================================================
   MODALES
========================================================= */

.overlay {

  position: fixed;

  inset: 0;

  z-index: 1000;

  display: flex;

  align-items: center;

  justify-content: center;

  padding: 20px;

  background:
    rgba(
      7,
      35,
      60,
      .65
    );
}


.modal {

  width: 520px;

  max-width: 100%;

  max-height: 92vh;

  overflow-y: auto;

  padding: 23px;

  border-top:
    4px solid var(--sigta-mostaza);

  border-radius: 11px;

  background: white;

  box-shadow:
    0
    20px
    60px
    rgba(0,0,0,.25);
}


.permissions-modal {

  width: 820px;
}


.modal-header {

  display: flex;

  align-items: flex-start;

  justify-content:
    space-between;

  gap: 12px;

  margin-bottom: 17px;
}


.modal-header > div > span {

  display: block;

  color: var(--sigta-texto-suave);

  font-size: 13px;

  font-weight: 900;
}


.modal-header h2 {

  margin:
    4px
    0
    0;

  color: var(--sigta-texto);

  font-size: 18px;
}


.modal-header p {

  margin:
    4px
    0
    0;

  color: var(--sigta-texto-suave);

  font-size: 14px;
}


.close-button {

  border: none;

  background: transparent;

  color: var(--sigta-texto-suave);

  font-size: 25px;

  cursor: pointer;
}


/* =========================================================
   CAMPOS
========================================================= */

.field {

  display: flex;

  flex-direction: column;

  gap: 5px;

  margin-top: 12px;
}


.field label {

  color: var(--sigta-azul);

  font-size: 15px;

  font-weight: 800;
}


.field input,
.field textarea {

  width: 100%;

  padding:
    10px
    11px;

  border:
    1px solid var(--sigta-borde);

  border-radius: 7px;

  color: var(--sigta-azul);

  font-family: inherit;

  font-size: 15px;

  outline: none;
}


.field textarea {

  min-height: 90px;

  resize: vertical;
}


.field small {

  color: var(--sigta-texto-suave);

  font-size: 13px;
}


.check-card {

  display: flex;

  align-items:
    flex-start;

  gap: 9px;

  margin-top: 13px;

  padding: 11px;

  border:
    1px solid var(--sigta-borde);

  border-radius: 7px;

  cursor: pointer;
}


.check-card strong,
.check-card span {

  display: block;
}


.check-card strong {

  color: var(--sigta-azul);

  font-size: 15px;
}


.check-card span {

  margin-top: 3px;

  color: var(--sigta-texto-suave);

  font-size: 13px;
}


.modal-actions {

  display: flex;

  justify-content:
    flex-end;

  gap: 8px;

  margin-top: 20px;
}

.confirmation-overlay {
  z-index: 1010;
}

.area-confirmation-modal {
  width: 500px;
  text-align: center;
}

.area-confirmation-modal h2 {
  margin: 12px 0 7px;
  color: var(--sigta-azul);
  font-size: 21px;
}

.area-confirmation-icon {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  margin: 0 auto;
  border-radius: 50%;
  font-size: 25px;
  font-weight: 900;
}

.area-confirmation-icon.inactivar {
  background: var(--sigta-error-fondo);
  color: var(--sigta-error);
}

.area-confirmation-icon.activar {
  background: var(--sigta-exito-fondo);
  color: var(--sigta-exito);
}

.area-confirmation-question {
  margin: 0;
  color: var(--sigta-texto-suave);
  font-size: 15px;
}

.area-confirmation-data {
  margin: 18px 0;
  padding: 13px;
  border: 1px solid var(--sigta-borde);
  border-radius: 8px;
  background: var(--sigta-azul-tenue);
  text-align: left;
}

.area-confirmation-data div {
  display: grid;
  grid-template-columns: 55px 1fr;
  gap: 9px;
  padding: 4px 0;
}

.area-confirmation-data dt {
  color: var(--sigta-azul);
  font-weight: 800;
}

.area-confirmation-data dd {
  margin: 0;
  overflow-wrap: anywhere;
}

.area-confirmation-notice {
  padding: 11px 12px;
  border-left: 4px solid var(--sigta-mostaza);
  border-radius: 7px;
  background: #fff9e6;
  color: var(--sigta-texto-suave);
  text-align: left;
  line-height: 1.45;
}

.area-enable-button,
.area-disable-button {
  min-height: 36px;
  padding: 0 14px;
  border: none;
  border-radius: 6px;
  color: white;
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
}

.area-enable-button {
  background: var(--sigta-azul);
}

.area-disable-button {
  background: var(--sigta-error);
}

.area-enable-button:disabled,
.area-disable-button:disabled {
  cursor: not-allowed;
  opacity: .55;
}


/* =========================================================
   MATRIZ DE ROL
========================================================= */

.permission-warning {

  margin-bottom: 14px;

  padding:
    10px
    12px;

  border-radius: 7px;

  background: var(--sigta-azul-tenue);

  color: var(--sigta-azul);

  font-size: 14px;

  line-height: 1.45;
}


.role-permissions-scroll {

  max-height: 580px;

  overflow-y: auto;

  padding-right: 4px;
}


.role-permission-group {

  margin-bottom: 14px;

  border:
    1px solid var(--sigta-borde);

  border-radius: 8px;

  overflow: hidden;
}


.role-permission-title {

  display: flex;

  justify-content:
    space-between;

  align-items: center;

  padding:
    10px
    12px;

  background: var(--sigta-azul-tenue);
}


.role-permission-title h3 {

  margin: 0;

  color: var(--sigta-texto);

  font-size: 16px;
}


.role-permission-title span {

  color: var(--sigta-azul);

  font-size: 14px;

  font-weight: 800;
}


.permission-checkbox {

  display: flex;

  align-items:
    flex-start;

  gap: 10px;

  padding:
    11px
    12px;

  border-top:
    1px solid var(--sigta-azul-tenue);

  cursor: pointer;
}


.permission-checkbox input {

  margin-top: 3px;
}


.permission-checkbox strong,
.permission-checkbox span {

  display: block;
}


.permission-checkbox strong {

  color: var(--sigta-azul);

  font-size: 15px;
}


.permission-checkbox span {

  margin-top: 3px;

  color: var(--sigta-azul);

  font-size: 13px;
}


.permission-checkbox p {

  margin:
    4px
    0
    0;

  color: var(--sigta-texto-suave);

  font-size: 13px;
}


/* =========================================================
   VACÍO / LOADING
========================================================= */

.loading,
.empty {

  padding: 35px;

  text-align: center;

  color: var(--sigta-texto-suave);

  font-size: 15px;
}


/* =========================================================
   RESPONSIVE
========================================================= */

@media (
  max-width: 1100px
) {

  .summary-grid {

    grid-template-columns:
      repeat(2,1fr);
  }


  .role-grid {

    grid-template-columns:
      repeat(2,1fr);
  }

}


@media (
  max-width: 760px
) {

  .layout {

    display: block;
  }


  .content {

    padding: 16px;
  }


  .page-header {

    flex-direction: column;
    align-items: flex-start;
  }


  .summary-grid,
  .role-grid {

    grid-template-columns:
      1fr;
  }


  .tabs {

    overflow-x: auto;
  }


  .permission-filters {

    grid-template-columns:
      1fr;
  }

}

</style>
