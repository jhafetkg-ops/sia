<template>

  <div class="admin-layout">

    <!-- =====================================================
         MENÚ ÚNICO DEL ADMINISTRADOR
    ====================================================== -->

    <SuperuserMenu />


    <!-- =====================================================
         CONTENIDO
    ====================================================== -->

    <main class="main-content">

      <div class="admin-topbar">

        <div class="session-panel">
          <button
            type="button"
            class="notification-button"
            title="Notificaciones"
          >
            <IconoSigta nombre="notificaciones" :tamano="20" />
            <span></span>
          </button>

          <div class="session-divider" aria-hidden="true"></div>

          <div class="session-profile" role="group" aria-label="Usuario conectado">
            <div class="session-avatar" aria-hidden="true">
              {{ inicialesSesion }}
            </div>

            <div class="session-copy">
              <strong :title="nombreSesion">{{ nombreSesion }}</strong>
              <small>{{ rolSesion }}</small>
            </div>
          </div>
        </div>

      </div>

      <!-- =================================================
           ENCABEZADO
      ================================================== -->

      <header class="page-header">

        <div class="page-title">

          <span class="page-icon">
            <IconoSigta nombre="usuarios" :tamano="36" />
          </span>

          <h1>
            Gestión de Usuarios
          </h1>

          <p>
            Alta, consulta, modificación, activación
            e inactivación de usuarios.
          </p>

        </div>


        <button
          class="btn-primary"
          @click="abrirNuevo"
        >
          <IconoSigta nombre="mas" :tamano="23" />
          <span>Nuevo usuario</span>
        </button>

      
        <UsuarioHeader @actualizar="cargarDatos" />
      </header>


      <!-- =================================================
           RESUMEN
      ================================================== -->

      <section class="stats-grid">

        <article class="stat-card total">

          <span class="stat-icon">
            <IconoSigta nombre="usuarios" :tamano="28" />
          </span>

          <div>

          <span class="stat-label">
            Total usuarios
          </span>

          <strong>
            {{ usuarios.length }}
          </strong>

          <small>
            Registrados en SIA
          </small>

          </div>

        </article>


        <article class="stat-card activos">

          <span class="stat-icon">
            <IconoSigta nombre="usuario_check" :tamano="28" />
          </span>

          <div>

          <span class="stat-label">
            Usuarios activos
          </span>

          <strong>
            {{ cantidadActivos }}
          </strong>

          <small>
            Con acceso habilitado
          </small>

          </div>

        </article>


        <article class="stat-card inactivos">

          <span class="stat-icon">
            <IconoSigta nombre="usuario_x" :tamano="28" />
          </span>

          <div>

          <span class="stat-label">
            Usuarios inactivos
          </span>

          <strong>
            {{ cantidadInactivos }}
          </strong>

          <small>
            Sin acceso al sistema
          </small>

          </div>

        </article>


        <article class="stat-card pendientes">

          <span class="stat-icon">
            <IconoSigta nombre="reloj" :tamano="28" />
          </span>

          <div>

          <span class="stat-label">
            Primer ingreso pendiente
          </span>

          <strong>
            {{ cantidadPrimerIngreso }}
          </strong>

          <small>
            Deben cambiar contraseña
          </small>

          </div>

        </article>

      </section>


      <!-- =================================================
           FILTROS
      ================================================== -->

      <section class="filters-card">

        <div class="search-box">

          <label>
            <IconoSigta nombre="buscar" :tamano="19" />
            Buscar usuario
          </label>

          <input
            v-model="busqueda"
            type="text"
            placeholder="Nombre o correo institucional..."
          />

        </div>


        <div class="filter-box">

          <label>
            <IconoSigta nombre="filtro" :tamano="19" />
            Estado
          </label>

          <select
            v-model="filtroEstado"
          >

            <option value="">
              Todos los estados
            </option>

            <option value="activo">
              Activos
            </option>

            <option value="inactivo">
              Inactivos
            </option>

          </select>

        </div>

      </section>


      <!-- =================================================
           MENSAJE GENERAL
      ================================================== -->

      <div
        v-if="mensaje"
        :class="[
          'alert',
          error
            ? 'error'
            : 'success'
        ]"
      >
        {{ mensaje }}
      </div>


      <!-- =================================================
           TABLA
      ================================================== -->

      <section class="table-card">

        <div class="table-header">

          <div>

            <h2>
              <IconoSigta nombre="usuarios" :tamano="28" />
              Usuarios registrados
            </h2>

            <p>
              Administre las cuentas y permisos
              institucionales.
            </p>

          </div>


          <span class="result-count">
            {{ usuariosFiltrados.length }}
            resultado(s)
          </span>

        </div>


        <div
          v-if="cargando"
          class="loading"
        >
          Cargando usuarios...
        </div>


        <div
          v-else-if="
            usuariosFiltrados.length === 0
          "
          class="empty"
        >
          No se encontraron usuarios.
        </div>


        <div
          v-else
          class="table-wrapper"
        >

          <table role="table" aria-label="Usuarios registrados">

            <colgroup>
              <col class="col-id" />
              <col class="col-user" />
              <col class="col-email" />
              <col class="col-role" />
              <col class="col-area" />
              <col class="col-status" />
              <col class="col-first-login" />
              <col class="col-actions" />
            </colgroup>

            <thead>

              <tr>

                <th class="id-column">
                  ID
                </th>

                <th>
                  Usuario
                </th>

                <th>
                  Correo
                </th>

                <th>
                  Rol
                </th>

                <th>
                  Área
                </th>

                <th>
                  Estado
                </th>

                <th>
                  Primer ingreso
                </th>

                <th>
                  Acciones
                </th>

              </tr>

            </thead>


            <tbody>

              <tr
                v-for="usuario in usuariosPaginados"
                :key="usuario.id"
              >

                <!-- ID -->
                <td class="id-column" data-label="ID">
                  {{ usuario.id }}
                </td>

                <!-- USUARIO -->
                <td data-label="Usuario">

                  <div class="user-cell">

                    <div class="table-avatar">

                      {{
                        obtenerIniciales(
                          usuario.nombre_completo
                        )
                      }}

                    </div>


                    <div class="user-details">

                      <strong class="cell-text" :title="usuario.nombre_completo">
                        {{ usuario.nombre_completo }}
                      </strong>

                    </div>

                  </div>

                </td>


                <!-- CORREO -->
                <td data-label="Correo">

                  <span class="cell-text" :title="usuario.email">
                    {{ usuario.email || 'Sin correo' }}
                  </span>

                </td>


                <!-- ROL -->
                <td data-label="Rol">

                  <span class="role-badge" :title="usuario.roles?.[0]?.rol_nombre || 'Sin rol'">

                    {{
                      usuario.roles?.[0]?.rol_nombre
                      || 'Sin rol'
                    }}

                  </span>

                </td>


                <!-- ÁREA -->
                <td data-label="Área">

                  <span class="cell-text" :title="usuario.roles?.[0]?.area_nombre || 'Global'">
                    {{
                      usuario.roles?.[0]?.area_nombre
                      || 'Global'
                    }}
                  </span>

                </td>


                <!-- ESTADO -->
                <td data-label="Estado">

                  <span
                    :class="[
                      'badge',
                      usuario.is_active
                        ? 'activo'
                        : 'inactivo'
                    ]"
                  >

                    {{
                      usuario.is_active
                        ? 'Activo'
                        : 'Inactivo'
                    }}

                  </span>

                </td>


                <!-- PRIMER INGRESO -->
                <td data-label="Primer ingreso">

                  <span
                    :class="[
                      'first-login',
                      usuario.must_change_password
                        ? 'pending'
                        : 'completed'
                    ]"
                  >

                    {{
                      usuario.must_change_password
                        ? 'Pendiente'
                        : 'Completado'
                    }}

                  </span>

                </td>


                <!-- ACCIONES -->
                <td data-label="Acciones">

                  <div class="actions">

                    <button
                      type="button"
                      class="btn-edit"
                      title="Editar usuario"
                      :aria-label="'Editar usuario ' + (usuario.nombre_completo || usuario.id)"
                      @click="
                        editarUsuario(
                          usuario
                        )
                      "
                    >
                      <IconoSigta nombre="editar" :tamano="16" />
                      <span>Editar</span>
                    </button>

                    <button
                      type="button"
                      class="btn-reset-password"
                      title="Restablecer contraseña"
                      :aria-label="'Restablecer contraseña de ' + (usuario.nombre_completo || usuario.id)"
                      @click="abrirRestablecerPassword(usuario)"
                    >
                      <IconoSigta nombre="llave" :tamano="16" />
                      <span>Restablecer contraseña</span>
                    </button>


                    <button
                      v-if="usuario.is_active"
                      type="button"
                      class="btn-disable"
                      title="Inactivar usuario"
                      :aria-label="'Inactivar usuario ' + (usuario.nombre_completo || usuario.id)"
                      @click="
                        solicitarCambioEstado(usuario, 'inactivar')
                      "
                    >
                      <IconoSigta nombre="basura" :tamano="16" />
                      <span>Inactivar</span>
                    </button>


                    <button
                      v-else
                      type="button"
                      class="btn-enable"
                      title="Activar usuario"
                      :aria-label="'Activar usuario ' + (usuario.nombre_completo || usuario.id)"
                      @click="
                        solicitarCambioEstado(usuario, 'activar')
                      "
                    >
                      <IconoSigta nombre="validar" :tamano="16" />
                      <span>Activar</span>
                    </button>

                  </div>

                </td>

              </tr>

            </tbody>

          </table>

        </div>

        <div
          v-if="!cargando && usuariosFiltrados.length"
          class="table-footer"
        >
          <span>
            Mostrando {{ rangoInicio }} a {{ rangoFin }} de {{ usuariosFiltrados.length }} resultados
          </span>

          <div class="pagination">
            <button
              type="button"
              :disabled="paginaActual === 1"
              title="Página anterior"
              @click="irPagina(paginaActual - 1)"
            >
              ‹
            </button>

            <button
              v-for="pagina in paginasVisibles"
              :key="pagina"
              type="button"
              :class="{ active: pagina === paginaActual }"
              @click="irPagina(pagina)"
            >
              {{ pagina }}
            </button>

            <button
              type="button"
              :disabled="paginaActual === totalPaginas"
              title="Página siguiente"
              @click="irPagina(paginaActual + 1)"
            >
              ›
            </button>
          </div>
        </div>

      </section>


      <!-- =================================================
           MODAL
      ================================================== -->

      <div
        v-if="mostrarModal"
        class="modal-overlay"
        @click.self="cerrarModal"
      >

        <div class="modal">

          <!-- ENCABEZADO MODAL -->

          <div class="modal-header">

            <div>

              <span class="modal-kicker">
                Administración de identidad
              </span>

              <h2>

                {{
                  editando
                    ? 'Editar usuario'
                    : 'Nuevo usuario'
                }}

              </h2>


              <p>

                {{
                  editando
                    ? 'Modifique los datos permitidos del usuario.'
                    : 'Registre una nueva cuenta institucional en SIA.'
                }}

              </p>

            </div>


            <button
              type="button"
              class="close"
              @click="cerrarModal"
            >
              ×
            </button>

          </div>


          <!-- FORMULARIO -->

          <form
            @submit.prevent="guardarUsuario"
          >

            <div class="grid">

              <!-- NOMBRE -->

              <div v-if="editando" class="field full">

                <label>
                  Nombre completo
                  <span>*</span>
                </label>

                <input
                  :value="form.nombre_completo"
                  type="text"
                  placeholder="Ingresa el nombre completo"
                  required
                  @input="alEscribirNombre('nombre_completo', $event)"
                />

              </div>

              <template v-else>
                <div class="field">
                  <label>Primer nombre <span>*</span></label>
                  <input :value="form.primer_nombre" type="text" placeholder="Ingresa tu primer nombre" required :disabled="usuarioCreado" @input="alEscribirNombre('primer_nombre', $event)" />
                </div>
                <div class="field">
                  <label>Segundo nombre</label>
                  <input :value="form.segundo_nombre" type="text" placeholder="Ingresa tu segundo nombre" :disabled="usuarioCreado" @input="alEscribirNombre('segundo_nombre', $event)" />
                </div>
                <div class="field">
                  <label>Apellido paterno <span>*</span></label>
                  <input :value="form.apellido_paterno" type="text" placeholder="Ingresa tu apellido paterno" required :disabled="usuarioCreado" @input="alEscribirNombre('apellido_paterno', $event)" />
                </div>
                <div class="field">
                  <label>Apellido materno <span>*</span></label>
                  <input :value="form.apellido_materno" type="text" placeholder="Ingresa tu apellido materno" required :disabled="usuarioCreado" @input="alEscribirNombre('apellido_materno', $event)" />
                </div>
              </template>


              <!-- EMAIL -->

              <div class="field full">

                <label>
                  Correo institucional
                  <span>*</span>
                </label>

                <input
                  :value="correoGenerado"
                  type="email"
                  placeholder="Se genera con el nombre y los apellidos"
                  readonly
                  required
                />

                <small>
                  Se utilizará para iniciar sesión
                  y recibir notificaciones.
                </small>

              </div>


              <!-- ROL -->

              <div class="field">

                <label>
                  Rol
                  <span>*</span>
                </label>

                <select
                  v-model="form.tipo_usuario"
                  required
                  @change="cambioRol"
                >

                  <option
                    value=""
                    disabled
                  >
                    Seleccione tipo
                  </option>


                  <option value="JEFE">Jefe</option>
                  <option value="TECNICO">Técnico</option>
                  <option value="DIRECTOR">Director</option>
                  <option value="USUARIO">Usuario</option>
                  <option value="SUPERUSER">Superuser</option>

                </select>

              </div>


              <!-- ÁREA -->

              <div v-if="requiereArea" class="field">

                <label>
                  Área
                  <span>*</span>
                </label>


                <select
                  v-model="form.area_id"
                  required
                  @change="form.especialidad = ''"
                >

                  <option value="">

                    Seleccione área

                  </option>


                  <option
                    v-for="area in areasFormulario"
                    :key="area.id"
                    :value="area.id"
                  >
                    {{ area.nombre }}
                  </option>

                </select>


              </div>

              <div v-if="form.tipo_usuario === 'TECNICO' && form.area_id" class="field">
                <label>Especialidad <span>*</span></label>
                <select v-model="form.especialidad" required>
                  <option value="" disabled>Seleccione especialidad</option>
                  <option v-for="opcion in especialidadesDisponibles" :key="opcion.valor" :value="opcion.valor">
                    {{ opcion.nombre }}
                  </option>
                </select>
              </div>


              <!-- CONTRASEÑA -->

              <div class="field full">

                <label>

                  {{
                    editando
                      ? 'Nueva contraseña temporal'
                      : 'Contraseña temporal'
                  }}

                  <span
                    v-if="
                      !editando
                    "
                  >
                    *
                  </span>

                </label>


                <div class="password-field">
                  <input
                    v-model="form.password"
                    :type="mostrarPassword ? 'text' : 'password'"
                    readonly
                    :placeholder="editando ? 'No se modifica desde esta pantalla' : '••••••••••'"
                  />
                  <button
                    v-if="!editando"
                    type="button"
                    class="password-eye"
                    :disabled="!form.password"
                    :aria-label="mostrarPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
                    :title="mostrarPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'"
                    @click="mostrarPassword = !mostrarPassword"
                  >👁</button>
                </div>


                <small>

                  {{
                    editando
                      ? 'Déjelo vacío si no desea cambiar la contraseña.'
                      : (form.password
                          ? 'Copie esta contraseña ahora: no podrá consultarse posteriormente.'
                          : 'Se generará automáticamente al crear el usuario.')
                  }}

                </small>

              </div>

            </div>


            <!-- ERROR MODAL -->

            <div
              v-if="mensajeModal"
              :class="usuarioCreado ? 'modal-success' : 'modal-error'"
            >
              {{ mensajeModal }}
            </div>


            <!-- ACCIONES MODAL -->

            <div class="modal-actions">

              <button
                type="button"
                class="btn-cancel"
                @click="cerrarModal"
              >
                {{ usuarioCreado ? 'Cerrar' : 'Cancelar' }}
              </button>


              <button
                v-if="!usuarioCreado"
                type="submit"
                class="btn-save"
                :disabled="guardando"
              >

                {{
                  guardando
                    ? 'Guardando...'
                    : (
                        editando
                          ? 'Guardar cambios'
                          : 'Crear usuario'
                      )
                }}

              </button>

            </div>

          </form>

        </div>

      </div>

      <!-- MODAL GELATINOSO: usuario creado -->
      <div
        v-if="confirmacionCreacion"
        class="modal-overlay jelly-overlay"
      >
        <div class="modal confirm-modal jelly-modal">
          <div class="jelly-check" aria-hidden="true">
            <IconoSigta nombre="validar" :tamano="46" />
          </div>
          <h2>¡Usuario creado!</h2>
          <p>La cuenta institucional quedó registrada en SIA.</p>
          <dl class="confirm-user-data">
            <div><dt>Correo:</dt><dd>{{ datosCreacion.correo }}</dd></div>
            <div v-if="datosCreacion.password"><dt>Contraseña temporal:</dt><dd>{{ datosCreacion.password }}</dd></div>
          </dl>
          <div v-if="datosCreacion.password" class="jelly-note">
            Copie la contraseña ahora: no podrá consultarse posteriormente.
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-save jelly-ok" @click="cerrarConfirmacionCreacion">
              Listo
            </button>
          </div>
        </div>
      </div>

      <div
        v-if="usuarioConfirmacion"
        class="modal-overlay"
        @click.self="cerrarConfirmacion"
      >
        <div class="modal confirm-modal">
          <div class="confirm-icon" :class="accionConfirmacion">!</div>
          <h2>{{ accionConfirmacion === 'inactivar' ? 'Inactivar usuario' : 'Activar usuario' }}</h2>
          <p>
            {{ accionConfirmacion === 'inactivar'
              ? '¿Está seguro de que desea inactivar a este usuario?'
              : '¿Está seguro de que desea activar nuevamente a este usuario?' }}
          </p>
          <dl class="confirm-user-data">
            <div><dt>Nombre:</dt><dd>{{ usuarioConfirmacion.nombre_completo }}</dd></div>
            <div><dt>Correo:</dt><dd>{{ usuarioConfirmacion.email }}</dd></div>
            <div><dt>Rol:</dt><dd>{{ usuarioConfirmacion.roles?.[0]?.rol_nombre || 'Sin rol' }}</dd></div>
          </dl>
          <div class="confirm-warning" :class="accionConfirmacion">
            {{ accionConfirmacion === 'inactivar'
              ? 'El usuario no podrá acceder a SIA mientras se encuentre inactivo.'
              : 'El usuario recuperará el acceso a SIA.' }}
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-cancel" :disabled="procesandoEstado" @click="cerrarConfirmacion">Cancelar</button>
            <button
              type="button"
              :class="accionConfirmacion === 'inactivar' ? 'btn-confirm-disable' : 'btn-confirm-enable'"
              :disabled="procesandoEstado"
              @click="confirmarCambioEstado"
            >
              {{ procesandoEstado
                ? 'Procesando...'
                : (accionConfirmacion === 'inactivar' ? 'Inactivar usuario' : 'Activar usuario') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Animación de inactivación / eliminación -->
      <div v-if="animacionUsuario && tipoAnimacion === 'inactivar'" class="modal-overlay anim-overlay">
        <div class="trash-anim" :class="faseAnimacion">
          <div class="ta-letters" aria-hidden="true">
            <span v-for="(l, i) in letrasEliminar" :key="i" :style="{ '--i': i }">{{ l }}</span>
          </div>
          <div class="ta-can" aria-hidden="true">
            <IconoSigta nombre="basura" :tamano="46" />
          </div>
          <div class="ta-check" aria-hidden="true">
            <IconoSigta nombre="validar" :tamano="40" />
          </div>
          <p class="ta-text">
            {{ faseAnimacion === 'listo' ? 'Usuario inactivado' : 'Inactivando usuario…' }}
          </p>
        </div>
      </div>

      <!-- Animación de activación -->
      <div v-if="animacionUsuario && tipoAnimacion === 'activar'" class="modal-overlay anim-overlay">
        <div class="activar-anim" :class="faseAnimacion">
          <div class="aa-rings" aria-hidden="true"><span></span><span></span><span></span></div>
          <div class="aa-letters" aria-hidden="true">
            <span v-for="(l, i) in letrasActivar" :key="i" :style="{ '--i': i }">{{ l }}</span>
          </div>
          <div class="aa-icon" aria-hidden="true">
            <IconoSigta nombre="usuario_check" :tamano="46" />
          </div>
          <div class="aa-check" aria-hidden="true">
            <IconoSigta nombre="validar" :tamano="40" />
          </div>
          <p class="aa-text">
            {{ faseAnimacion === 'listo' ? 'Usuario activado' : 'Activando usuario…' }}
          </p>
        </div>
      </div>

      <div
        v-if="usuarioRestablecimiento && !passwordRestablecida"
        class="modal-overlay"
        @click.self="cerrarRestablecimiento"
      >
        <div class="modal confirm-modal">
          <div class="confirm-icon reset-password">!</div>
          <h2>Restablecer contraseña</h2>
          <p>¿Está seguro de que desea restablecer la contraseña de este usuario?</p>
          <dl class="confirm-user-data">
            <div><dt>Usuario:</dt><dd>{{ usuarioRestablecimiento.nombre_completo }}</dd></div>
            <div><dt>Correo:</dt><dd>{{ usuarioRestablecimiento.email }}</dd></div>
          </dl>
          <div class="confirm-warning">
            La contraseña actual dejará de funcionar. Se generará una nueva contraseña temporal y el usuario deberá cambiarla en su próximo inicio de sesión.
          </div>
          <div v-if="errorRestablecimiento" class="modal-error">
            {{ errorRestablecimiento }}
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-cancel" :disabled="restableciendoPassword" @click="cerrarRestablecimiento">
              Cancelar
            </button>
            <button type="button" class="btn-confirm-reset" :disabled="restableciendoPassword" @click="confirmarRestablecimiento">
              {{ restableciendoPassword ? 'Restableciendo...' : 'Restablecer contraseña' }}
            </button>
          </div>
        </div>
      </div>

      <div
        v-if="usuarioRestablecimiento && passwordRestablecida"
        class="modal-overlay"
      >
        <div class="modal generated-password-modal">
          <div class="confirm-icon activar">✓</div>
          <h2>Contraseña temporal generada</h2>
          <dl class="confirm-user-data">
            <div><dt>Usuario:</dt><dd>{{ usuarioRestablecimiento.nombre_completo }}</dd></div>
            <div><dt>Correo:</dt><dd>{{ usuarioRestablecimiento.email }}</dd></div>
          </dl>
          <div class="field full">
            <label>Contraseña temporal</label>
            <div class="password-field">
              <input
                :value="passwordRestablecida"
                :type="mostrarPasswordRestablecida ? 'text' : 'password'"
                readonly
              />
              <button
                type="button"
                class="password-eye"
                :aria-label="mostrarPasswordRestablecida ? 'Ocultar contraseña' : 'Mostrar contraseña'"
                :title="mostrarPasswordRestablecida ? 'Ocultar contraseña' : 'Mostrar contraseña'"
                @click="mostrarPasswordRestablecida = !mostrarPasswordRestablecida"
              >👁</button>
            </div>
          </div>
          <div class="one-time-notice">
            <strong>Esta contraseña temporal se mostrará únicamente en este momento.</strong>
            <span>El usuario deberá cambiarla al iniciar sesión nuevamente.</span>
          </div>
          <div class="modal-actions">
            <button type="button" class="btn-save" @click="cerrarRestablecimiento">Entendido</button>
          </div>
        </div>
      </div>

    </main>

    <TarjetaGuardado :visible="mostrarGuardadoOk" :texto="textoGuardado" @cerrar="ocultarGuardado" />

  </div>

</template>


<script setup>
import UsuarioHeader from '../components/UsuarioHeader.vue'

import {
  computed,
  onMounted,
  reactive,
  ref,
  watch,
} from 'vue'

import {
  useRouter
} from 'vue-router'


/* =========================================================
   COMPONENTE MENÚ
========================================================= */

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

const {
  mostrar: mostrarGuardadoOk,
  texto: textoGuardado,
  animar: animarGuardado,
  ocultar: ocultarGuardado,
} = usarGuardado()


/* =========================================================
   DATOS
========================================================= */

const usuarios =
  ref([])

const roles =
  ref([])

const areas =
  ref([])


/* =========================================================
   ESTADOS
========================================================= */

const cargando =
  ref(true)

const guardando =
  ref(false)

const mostrarModal =
  ref(false)

const editando =
  ref(false)

const usuarioEditandoId =
  ref(null)

const busqueda =
  ref('')

const filtroEstado =
  ref('')

const paginaActual =
  ref(1)

const porPagina =
  3

const mensaje =
  ref('')

const mensajeModal =
  ref('')

const error =
  ref(false)

const mostrarPassword = ref(false)
const usuarioCreado = ref(false)

/* Modal gelatinoso de confirmación al crear un usuario */
const confirmacionCreacion = ref(false)
const datosCreacion = ref({ correo: '', password: '' })

const usuarioConfirmacion = ref(null)
const accionConfirmacion = ref('')
const procesandoEstado = ref(false)

/* Animación al inactivar/eliminar un usuario */
const animacionUsuario = ref(false)
const tipoAnimacion = ref('')
const faseAnimacion = ref('')
const letrasEliminar = ['e', 'l', 'i', 'm', 'i', 'n', 'a', 'r']
const letrasActivar = ['a', 'c', 't', 'i', 'v', 'a', 'r']
const usuarioRestablecimiento = ref(null)
const passwordRestablecida = ref('')
const mostrarPasswordRestablecida = ref(false)
const restableciendoPassword = ref(false)
const errorRestablecimiento = ref('')

const usuarioSesion =
  ref(leerUsuarioSesion())

const nombreSesion =
  computed(() => {
    const nombre = usuarioSesion.value?.nombre_completo
      || usuarioSesion.value?.nombre
      || 'Admin'

    return nombre.replace(/\s*\((?:superuser|superusuario)\)\s*$/i, '').trim()
      || 'Admin'
  })

const rolSesion =
  computed(() => {
    const rol = usuarioSesion.value?.roles?.[0]?.rol_nombre?.trim() || ''

    if (usuarioSesion.value?.is_superuser
      || /^(?:admin(?:istrador)?\s*\(superuser\)|superuser|superusuario)$/i.test(rol)) {
      return 'Superusuario'
    }

    return rol || 'Superusuario'
  })

const inicialesSesion =
  computed(() =>
    nombreSesion.value.charAt(0).toLocaleUpperCase('es')
  )


/* =========================================================
   FORMULARIO
========================================================= */

const form =
  reactive({

    nombre_completo: '',

    primer_nombre: '',

    segundo_nombre: '',

    apellido_paterno: '',

    apellido_materno: '',

    email: '',

    password: '',

    tipo_usuario: '',

    rol_id: '',

    area_id: '',

    especialidad: '',
  })

function normalizarParteCorreo(valor) {
  return String(valor || '')
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '')
}

/* Pone en may\u00fascula la primera letra de cada palabra del nombre */
function capitalizarNombre(valor) {
  return String(valor || '').replace(
    /(^|[\s'-])(\p{Ll})/gu,
    (_, separador, letra) => separador + letra.toUpperCase()
  )
}

function alEscribirNombre(campo, evento) {
  form[campo] = capitalizarNombre(evento.target.value)
}

const correoGenerado = computed(() => {
  if (editando.value) return form.email
  const primero = normalizarParteCorreo(form.primer_nombre)
  const paterno = normalizarParteCorreo(form.apellido_paterno)
  const materno = normalizarParteCorreo(form.apellido_materno)
  if (!primero || !paterno || !materno) return ''
  return `${primero[0]}${paterno}${materno[0]}@emi.edu.bo`
})


/* =========================================================
   TOKEN
========================================================= */

const token = () =>
  localStorage.getItem(
    'sigta_token'
  )


/* =========================================================
   HEADERS
========================================================= */

const headers = () => ({

  'Content-Type':
    'application/json',

  Accept:
    'application/json',

  Authorization:
    `Token ${token()}`,
})


const headersLectura = () => ({

  Accept:
    'application/json',

  Authorization:
    `Token ${token()}`,
})

function leerUsuarioSesion() {

  try {

    return JSON.parse(
      localStorage.getItem('sigta_usuario')
      || '{}'
    )

  } catch {

    return {}
  }
}


/* =========================================================
   CONTADORES
========================================================= */

const cantidadActivos =
  computed(() => {

    return usuarios.value.filter(
      usuario =>
        usuario.is_active
    ).length
  })


const cantidadInactivos =
  computed(() => {

    return usuarios.value.filter(
      usuario =>
        !usuario.is_active
    ).length
  })


const cantidadPrimerIngreso =
  computed(() => {

    return usuarios.value.filter(
      usuario =>
        usuario.must_change_password
    ).length
  })


/* =========================================================
   FILTRADO
========================================================= */

const usuariosFiltrados =
  computed(() => {

    const texto =
      busqueda.value
        .toLowerCase()
        .trim()


    return usuarios.value.filter(
      usuario => {

        const coincideTexto =

          !texto

          ||

          usuario.nombre_completo
            ?.toLowerCase()
            .includes(texto)

          ||

          usuario.email
            ?.toLowerCase()
            .includes(texto)


        const coincideEstado =

          !filtroEstado.value

          ||

          (
            filtroEstado.value
            === 'activo'

            &&
            usuario.is_active
          )

          ||

          (
            filtroEstado.value
            === 'inactivo'

            &&
            !usuario.is_active
          )


        return (
          coincideTexto
          &&
          coincideEstado
        )
      }
    )
  })

const totalPaginas =
  computed(() =>
    Math.max(
      1,
      Math.ceil(
        usuariosFiltrados.value.length
        / porPagina
      )
    )
  )

const usuariosPaginados =
  computed(() => {

    const inicio =
      (paginaActual.value - 1)
      * porPagina

    return usuariosFiltrados.value.slice(
      inicio,
      inicio + porPagina
    )
  })

const rangoInicio =
  computed(() =>
    usuariosFiltrados.value.length
      ? ((paginaActual.value - 1) * porPagina) + 1
      : 0
  )

const rangoFin =
  computed(() =>
    Math.min(
      paginaActual.value * porPagina,
      usuariosFiltrados.value.length
    )
  )

const paginasVisibles =
  computed(() => {

    const maximoVisible =
      6

    if (totalPaginas.value <= maximoVisible) {

      return Array.from(
        { length: totalPaginas.value },
        (_, indice) => indice + 1
      )
    }

    const mitad =
      Math.floor(maximoVisible / 2)

    let inicio =
      Math.max(
        1,
        paginaActual.value - mitad
      )

    let fin =
      inicio + maximoVisible - 1

    if (fin > totalPaginas.value) {

      fin = totalPaginas.value
      inicio = fin - maximoVisible + 1
    }

    return Array.from(
      { length: fin - inicio + 1 },
      (_, indice) => inicio + indice
    )
  })

watch(
  [
    busqueda,
    filtroEstado,
  ],
  () => {
    paginaActual.value = 1
  }
)

watch(
  () => usuariosFiltrados.value.length,
  () => {

    if (paginaActual.value > totalPaginas.value) {

      paginaActual.value =
        totalPaginas.value
    }
  }
)

function irPagina(
  pagina
) {

  paginaActual.value =
    Math.min(
      Math.max(1, pagina),
      totalPaginas.value
    )
}


/* =========================================================
   ROL GLOBAL
========================================================= */

const requiereArea = computed(() => ['JEFE', 'TECNICO'].includes(form.tipo_usuario))

const areasFormulario = computed(() => {
  const oficiales = ['DAF', 'MANTENIMIENTO', 'UTIC']
  return areas.value.filter(area => oficiales.includes(String(area.codigo).toUpperCase()))
})

const areaSeleccionada = computed(() =>
  areas.value.find(area => Number(area.id) === Number(form.area_id))
)

const especialidadesDisponibles = computed(() => {
  const codigo = String(areaSeleccionada.value?.codigo || '').toUpperCase()
  if (codigo === 'UTIC') return [
    { valor: 'REDES', nombre: 'Redes' },
    { valor: 'HARDWARE_COMPUTADORAS', nombre: 'Hardware y computadoras' },
    { valor: 'SISTEMAS_CENTRALIZADOS_DATOS', nombre: 'Sistemas centralizados y datos' },
    { valor: 'EQUIPOS_AUXILIARES', nombre: 'Equipos auxiliares' },
  ]
  if (codigo === 'MANTENIMIENTO') return [
    { valor: 'CHOFER', nombre: 'Chofer' },
    { valor: 'TECNICO_MANTENIMIENTO', nombre: 'Técnico' },
  ]
  if (codigo === 'DAF') return [
    { valor: 'TECNICO_DAF', nombre: 'Técnico de la DAF' },
    { valor: 'ALMACEN_COMPRAS', nombre: 'Técnico de Almacén y Compras' },
    { valor: 'TESORERIA', nombre: 'Técnico de Tesorería' },
  ]
  return []
})

function codigoRolInterno() {
  if (form.tipo_usuario === 'SUPERUSER') return 'SUPERUSER'
  if (form.tipo_usuario === 'DIRECTOR') return 'ADMIN'
  if (form.tipo_usuario === 'USUARIO') return 'SOLICITANTE'
  const area = String(areaSeleccionada.value?.codigo || '').toUpperCase()
  if (form.tipo_usuario === 'JEFE') {
    return { UTIC: 'JEFE_UTIC', MANTENIMIENTO: 'SERVICIOS_GENERALES' }[area]
  }
  if (form.tipo_usuario === 'TECNICO') {
    if (area === 'UTIC') return 'ESPECIALISTA'
    if (area === 'MANTENIMIENTO') return 'AUXILIAR_SERVICIOS_GENERALES'
    return { TECNICO_DAF: 'DAF', ALMACEN_COMPRAS: 'ENCARGADO_COMPRAS_ALMACEN', TESORERIA: 'TESORERIA' }[form.especialidad]
  }
  return ''
}


/* =========================================================
   AL MONTAR
========================================================= */

onMounted(
  async () => {

    if (!token()) {

      router.push(
        '/login'
      )

      return
    }


    await cargarDatos()
  }
)


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
   CARGAR USUARIOS, ROLES Y ÁREAS
========================================================= */

async function cargarDatos() {

  cargando.value =
    true


  try {

    const [
      usuariosRespuesta,
      rolesRespuesta,
      areasRespuesta,
    ] = await Promise.all([


      /* USUARIOS */

      fetch(
        '/api/usuarios/usuarios/',
        {
          headers:
            headersLectura(),
        }
      ),


      /* ROLES
         CORREGIDO:
         ahora también manda token
      */

      fetch(
        '/api/usuarios/roles/',
        {
          headers:
            headersLectura(),
        }
      ),


      /* ÁREAS
         CORREGIDO:
         ahora también manda token
      */

      fetch(
        '/api/usuarios/areas/',
        {
          headers:
            headersLectura(),
        }
      ),

    ])


    /* ===============================================
       VALIDAR SESIÓN
    ================================================ */

    const respuestas = [

      usuariosRespuesta,

      rolesRespuesta,

      areasRespuesta,
    ]


    const sinPermiso =
      respuestas.some(
        respuesta =>
          respuesta.status === 401
          ||
          respuesta.status === 403
      )


    if (sinPermiso) {

      cerrarSesion()

      return
    }


    /* ===============================================
       VALIDAR ERRORES
    ================================================ */

    if (!usuariosRespuesta.ok) {

      throw new Error(
        'No se pudieron cargar los usuarios.'
      )
    }


    if (!rolesRespuesta.ok) {

      throw new Error(
        'No se pudieron cargar los roles.'
      )
    }


    if (!areasRespuesta.ok) {

      throw new Error(
        'No se pudieron cargar las áreas.'
      )
    }


    /* ===============================================
       LEER JSON
    ================================================ */

    const datosUsuarios =
      await usuariosRespuesta.json()


    const datosRoles =
      await rolesRespuesta.json()


    const datosAreas =
      await areasRespuesta.json()


    /* ===============================================
       GUARDAR
    ================================================ */

    usuarios.value =
      convertirLista(
        datosUsuarios
      )


    roles.value =
      convertirLista(
        datosRoles
      )


    areas.value =
      convertirLista(
        datosAreas
      )


    console.log(
      'Usuarios:',
      usuarios.value
    )


    console.log(
      'Roles:',
      roles.value
    )


    console.log(
      'Áreas:',
      areas.value
    )


  } catch (e) {

    console.error(
      'Error cargando usuarios:',
      e
    )


    mostrarMensaje(
      e.message
      ||
      'No se pudieron cargar los datos.',
      true
    )

  } finally {

    cargando.value =
      false
  }
}


/* =========================================================
   NUEVO USUARIO
========================================================= */

function abrirNuevo() {

  editando.value =
    false

  usuarioEditandoId.value =
    null

  limpiarFormulario()

  form.password = 'Temporal2026*'

  mostrarModal.value =
    true
}


/* =========================================================
   EDITAR USUARIO
========================================================= */

function editarUsuario(
  usuario
) {

  editando.value =
    true


  usuarioEditandoId.value =
    usuario.id


  form.nombre_completo =
    usuario.nombre_completo
    || ''


  form.email =
    usuario.email
    || ''


  form.password = ''


  /*
   * Se convierte a Number para que
   * coincida correctamente con:
   *
   * :value="rol.id"
   */

  form.rol_id =
    usuario.roles?.[0]?.rol_id
      ? Number(
          usuario.roles[0].rol_id
        )
      : ''

  const asignacion = usuario.roles?.[0] || {}
  const codigoRol = asignacion.rol_codigo
  const mapaTipo = {
    SUPERUSER: 'SUPERUSER', ADMIN: 'DIRECTOR', DIRECTOR: 'DIRECTOR', SOLICITANTE: 'USUARIO',
    JEFE_UTIC: 'JEFE', SERVICIOS_GENERALES: 'JEFE',
    ESPECIALISTA: 'TECNICO', AUXILIAR_SERVICIOS_GENERALES: 'TECNICO', DAF: 'TECNICO',
    ENCARGADO_COMPRAS_ALMACEN: 'TECNICO', TESORERIA: 'TECNICO',
  }
  form.tipo_usuario = mapaTipo[codigoRol] || ''


  /*
   * Igual para Área.
   */

  form.area_id =
    usuario.roles?.[0]?.area_id
      ? Number(
          usuario.roles[0].area_id
        )
      : ''

  if (!form.area_id) {
    const codigoArea = {
      JEFE_UTIC: 'UTIC', ESPECIALISTA: 'UTIC',
      DAF: 'DAF', ENCARGADO_COMPRAS_ALMACEN: 'DAF', TESORERIA: 'DAF',
      SERVICIOS_GENERALES: 'MANTENIMIENTO', AUXILIAR_SERVICIOS_GENERALES: 'MANTENIMIENTO',
    }[codigoRol]
    form.area_id = areas.value.find(area => area.codigo === codigoArea)?.id || ''
  }

  form.especialidad = asignacion.especialidad || ({
    DAF: 'TECNICO_DAF', ENCARGADO_COMPRAS_ALMACEN: 'ALMACEN_COMPRAS', TESORERIA: 'TESORERIA',
    AUXILIAR_SERVICIOS_GENERALES: 'TECNICO_MANTENIMIENTO',
  }[codigoRol] || '')


  mensajeModal.value =
    ''


  mostrarModal.value =
    true
}


/* =========================================================
   LIMPIAR
========================================================= */

function limpiarFormulario() {

  form.nombre_completo = ''

  form.primer_nombre = ''

  form.segundo_nombre = ''

  form.apellido_paterno = ''

  form.apellido_materno = ''

  form.email = ''

  form.password = ''

  form.tipo_usuario = ''

  form.rol_id = ''

  form.area_id = ''

  form.especialidad = ''

  mensajeModal.value = ''

  mostrarPassword.value = false

  usuarioCreado.value = false
}


/* =========================================================
   CERRAR MODAL
========================================================= */

function cerrarModal() {

  mostrarModal.value =
    false

  limpiarFormulario()
}


function cerrarConfirmacionCreacion() {
  confirmacionCreacion.value = false
  cerrarModal()
}


/* =========================================================
   CAMBIO DE ROL
========================================================= */

function cambioRol() {
  form.rol_id = ''
  form.especialidad = ''
  if (!requiereArea.value) {
    form.area_id = ''
  }
}


/* =========================================================
   GUARDAR USUARIO
========================================================= */

async function guardarUsuario() {

  mensajeModal.value = ''


  /* ===============================================
     CAMPOS OBLIGATORIOS
  ================================================ */

  if (
    (editando.value
      ? !form.nombre_completo.trim()
      : (!form.primer_nombre.trim()
          || !form.apellido_paterno.trim()
          || !form.apellido_materno.trim()))
    ||
    !form.tipo_usuario
  ) {

    mensajeModal.value =
      'Complete los campos obligatorios.'

    return
  }

  if (
    form.tipo_usuario === 'JEFE'
    &&
    String(areaSeleccionada.value?.codigo || '').toUpperCase() === 'DAF'
  ) {

    mensajeModal.value =
      'La DAF no tiene jefatura: la solicitud de compra llega directamente a la DAF.'

    return
  }


  /* ===============================================
     CORREO EMI
  ================================================ */

  if (
    !correoGenerado.value.endsWith('@emi.edu.bo')
  ) {

    mensajeModal.value =
      'Ingrese un correo institucional @emi.edu.bo.'

    return
  }


  /* ===============================================
     ÁREA OBLIGATORIA
  ================================================ */

  if (
    requiereArea.value
    &&
    !form.area_id
  ) {

    mensajeModal.value =
      'Seleccione el área del usuario.'

    return
  }

  if (form.tipo_usuario === 'TECNICO' && !form.especialidad) {
    mensajeModal.value = 'Seleccione la especialidad del técnico.'
    return
  }


  guardando.value =
    true


  try {

    const codigoRol = codigoRolInterno()
    const rolInterno = roles.value.find(rol => rol.codigo === codigoRol)
    if (!rolInterno) {
      mensajeModal.value = 'No se encontró el rol interno para la selección realizada.'
      return
    }

    const payload = {

      nombre_completo:
        editando.value
          ? form.nombre_completo.trim()
          : [
              form.primer_nombre,
              form.segundo_nombre,
              form.apellido_paterno,
              form.apellido_materno,
            ]
              .map(valor => valor.trim())
              .filter(Boolean)
              .join(' '),

      email:
        correoGenerado.value,

      rol_id: Number(rolInterno.id),

      area_id:
        form.area_id
          ? Number(form.area_id)
          : null,

      especialidad: form.especialidad || '',
    }

    if (!editando.value) {
      payload.primer_nombre = form.primer_nombre.trim()
      payload.segundo_nombre = form.segundo_nombre.trim()
      payload.apellido_paterno = form.apellido_paterno.trim()
      payload.apellido_materno = form.apellido_materno.trim()
      payload.password = form.password
    }


    /*
     * La contraseña solamente se manda
     * si se escribió una.
     */

    if (editando.value && form.password) {

      payload.password =
        form.password
    }


    let url =
      '/api/usuarios/usuarios/'


    let method =
      'POST'


    if (
      editando.value
    ) {

      url =
        `/api/usuarios/usuarios/${usuarioEditandoId.value}/`


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
            JSON.stringify(
              payload
            ),
        }
      )


    let datos = {}


    try {

      datos =
        await respuesta.json()

    } catch {

      datos = {}
    }


    if (!respuesta.ok) {

      console.error(
        'Error guardando usuario:',
        datos
      )


      mensajeModal.value =
        obtenerError(
          datos
        )


      return
    }


    const eraEdicion =
      editando.value


    if (eraEdicion) {
      cerrarModal()
      guardando.value = false
      await cargarDatos()
      await animarGuardado('Usuario actualizado')
    } else {
      form.password = datos.password_temporal || ''
      usuarioCreado.value = true
      mensajeModal.value = 'Usuario creado correctamente.'
      datosCreacion.value = {
        correo: correoGenerado.value,
        password: form.password,
      }
      confirmacionCreacion.value = true
      await cargarDatos()
    }


  } catch (e) {

    console.error(
      'Error guardando usuario:',
      e
    )


    mensajeModal.value =
      'No fue posible guardar el usuario.'

  } finally {

    guardando.value =
      false

    mostrarGuardadoOk.value =
      false
  }
}


/* =========================================================
   INACTIVAR
========================================================= */

async function inactivarUsuario(
  usuario
) {
  try {

    const respuesta =
      await fetch(
        `/api/usuarios/usuarios/${usuario.id}/`,
        {

          method:
            'DELETE',

          headers:
            headers(),
        }
      )


    let datos = {}


    try {

      datos =
        await respuesta.json()

    } catch {

      datos = {}
    }


    if (!respuesta.ok) {

      mostrarMensaje(
        datos.detalle
        ||
        datos.detail
        ||
        'No se pudo inactivar el usuario.',
        true
      )


      return false
    }


    mostrarMensaje(
      'Usuario inactivado correctamente.'
    )


    await cargarDatos()

    return true


  } catch (e) {

    console.error(
      e
    )


    mostrarMensaje(
      'Error al inactivar el usuario.',
      true
    )
    return false
  }
}

function solicitarCambioEstado(usuario, accion) {
  usuarioConfirmacion.value = usuario
  accionConfirmacion.value = accion
}

function cerrarConfirmacion() {
  if (procesandoEstado.value) return
  usuarioConfirmacion.value = null
  accionConfirmacion.value = ''
}

function esperar(ms) {
  return new Promise(resolve => setTimeout(resolve, ms))
}

async function confirmarCambioEstado() {
  if (!usuarioConfirmacion.value) return
  procesandoEstado.value = true
  const usuario = usuarioConfirmacion.value
  const accion = accionConfirmacion.value

  // Cierra el modal de confirmación y arranca la animación + la petición en paralelo.
  usuarioConfirmacion.value = null
  accionConfirmacion.value = ''
  tipoAnimacion.value = accion
  faseAnimacion.value = 'accion'
  animacionUsuario.value = true

  const reducirMovimiento = typeof window !== 'undefined'
    && window.matchMedia
    && window.matchMedia('(prefers-reduced-motion: reduce)').matches

  const peticion = accion === 'inactivar'
    ? inactivarUsuario(usuario)
    : activarUsuario(usuario)

  if (reducirMovimiento) {
    const completado = await peticion
    if (completado) {
      faseAnimacion.value = 'listo'
      await esperar(500)
    }
  } else {
    await esperar(accion === 'inactivar' ? 1100 : 950)
    faseAnimacion.value = 'giro'
    await esperar(750)
    const completado = await peticion
    if (completado) {
      faseAnimacion.value = 'listo'
      await esperar(950)
    }
  }

  animacionUsuario.value = false
  tipoAnimacion.value = ''
  faseAnimacion.value = ''
  procesandoEstado.value = false
}


/* =========================================================
   ACTIVAR
========================================================= */

async function activarUsuario(
  usuario
) {

  try {

    const respuesta =
      await fetch(
        `/api/usuarios/usuarios/${usuario.id}/activar/`,
        {

          method:
            'POST',

          headers:
            headers(),

          body:
            JSON.stringify({}),
        }
      )


    let datos = {}


    try {

      datos =
        await respuesta.json()

    } catch {

      datos = {}
    }


    if (!respuesta.ok) {

      mostrarMensaje(
        datos.detalle
        ||
        datos.detail
        ||
        'No se pudo activar el usuario.',
        true
      )


      return false
    }


    mostrarMensaje(
      'Usuario activado correctamente.'
    )


    await cargarDatos()

    return true


  } catch (e) {

    console.error(
      e
    )


    mostrarMensaje(
      'Error al activar el usuario.',
      true
    )
    return false
  }
}


/* =========================================================
   RESTABLECER CONTRASEÑA
========================================================= */

function abrirRestablecerPassword(usuario) {
  usuarioRestablecimiento.value = usuario
  passwordRestablecida.value = ''
  mostrarPasswordRestablecida.value = false
  errorRestablecimiento.value = ''
}

function cerrarRestablecimiento() {
  if (restableciendoPassword.value) return
  usuarioRestablecimiento.value = null
  passwordRestablecida.value = ''
  mostrarPasswordRestablecida.value = false
  errorRestablecimiento.value = ''
}

async function confirmarRestablecimiento() {
  if (!usuarioRestablecimiento.value) return

  restableciendoPassword.value = true
  errorRestablecimiento.value = ''

  try {
    const respuesta = await fetch(
      `/api/usuarios/usuarios/${usuarioRestablecimiento.value.id}/restablecer-password/`,
      {
        method: 'POST',
        headers: headers(),
        body: JSON.stringify({}),
      }
    )

    let datos = {}
    try {
      datos = await respuesta.json()
    } catch {
      datos = {}
    }

    if (!respuesta.ok || !datos.password_temporal) {
      errorRestablecimiento.value =
        respuesta.status === 401 || respuesta.status === 403
          ? 'No tiene autorización para restablecer esta contraseña.'
          : 'No fue posible restablecer la contraseña. Intente nuevamente.'
      return
    }

    await cargarDatos()
    restableciendoPassword.value = false
    await animarGuardado('Contraseña restablecida')
    passwordRestablecida.value = datos.password_temporal
  } catch (error) {
    console.error('Error restableciendo contraseña:', error)
    errorRestablecimiento.value =
      'No fue posible restablecer la contraseña. Intente nuevamente.'
  } finally {
    restableciendoPassword.value = false
    mostrarGuardadoOk.value = false
  }
}


/* =========================================================
   ERRORES DEL BACKEND
========================================================= */

function obtenerError(
  datos
) {

  if (
    datos.email
  ) {

    return Array.isArray(
      datos.email
    )
      ? datos.email[0]
      : String(
          datos.email
        )
  }


  if (
    datos.password
  ) {

    return Array.isArray(
      datos.password
    )
      ? datos.password[0]
      : String(
          datos.password
        )
  }


  if (
    datos.area_id
  ) {

    return Array.isArray(
      datos.area_id
    )
      ? datos.area_id[0]
      : String(
          datos.area_id
        )
  }


  if (
    datos.rol_id
  ) {

    return Array.isArray(
      datos.rol_id
    )
      ? datos.rol_id[0]
      : String(
          datos.rol_id
        )
  }


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


  /*
   * Si DRF devuelve otros campos
   * mostramos el primero.
   */

  const errores =
    Object.entries(
      datos
    )


  if (
    errores.length > 0
  ) {

    const [
      campo,
      valor
    ] =
      errores[0]


    const texto =
      Array.isArray(valor)
        ? valor.join(', ')
        : String(valor)


    return (
      `${campo}: ${texto}`
    )
  }


  return (
    'Revise los datos ingresados.'
  )
}


/* =========================================================
   MENSAJE
========================================================= */

function mostrarMensaje(
  texto,
  esError = false
) {

  mensaje.value =
    texto


  error.value =
    esError


  setTimeout(
    () => {

      mensaje.value = ''

    },
    3500
  )
}


/* =========================================================
   INICIALES
========================================================= */

function obtenerIniciales(
  nombre
) {

  if (!nombre) {

    return 'U'
  }


  return nombre
    .replace(/\s*\((?:superuser|superusuario)\)\s*$/i, '')
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
}


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

.admin-layout {

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
   ENCABEZADO
========================================================= */

.topbar {

  display: flex;

  justify-content:
    space-between;

  align-items: center;

  gap: 20px;

  margin-bottom: 21px;
}


.breadcrumb {

  display: block;

  margin-bottom: 7px;

  color: var(--sigta-texto-suave);

  font-size: 15px;
}


.topbar h1 {

  margin: 0;

  color: var(--sigta-texto);

  font-size: 28px;
}


.topbar p {

  margin:
    5px
    0
    0;

  color: var(--sigta-texto-suave);

  font-size: 18px;
}


.btn-primary {

  min-height: 43px;

  padding:
    0
    18px;

  border: none;

  border-radius: 8px;

  background: var(--sigta-mostaza);

  color: var(--sigta-azul);

  font-size: 17px;

  font-weight: 800;

  cursor: pointer;
}


.btn-primary:hover {

  background: var(--sigta-mostaza);
}


/* =========================================================
   ESTADÍSTICAS
========================================================= */

.stats-grid {

  display: grid;

  grid-template-columns:
    repeat(4,1fr);

  gap: 13px;

  margin-bottom: 18px;
}


.stat-card {

  min-height: 105px;

  padding: 16px;

  border-top:
    3px solid var(--sigta-mostaza);

  border-radius: 9px;

  background: white;

  box-shadow:
    0
    3px
    12px
    rgba(0,0,0,.05);
}


.stat-card span {

  display: block;

  color: var(--sigta-texto-suave);

  font-size: 15px;

  font-weight: 800;

  text-transform: uppercase;
}


.stat-card strong {

  display: block;

  margin:
    7px
    0;

  color: var(--sigta-azul);

  font-size: 25px;
}


.stat-card small {

  color: var(--sigta-texto-suave);

  font-size: 14px;
}


/* =========================================================
   FILTROS
========================================================= */

.filters-card {

  display: grid;

  grid-template-columns:
    1fr 210px;

  gap: 12px;

  margin-bottom: 16px;

  padding: 14px;

  border-radius: 9px;

  background: var(--sigta-blanco);

  box-shadow:
    0
    3px
    12px
    rgba(0,0,0,.04);
}


.search-box,
.filter-box {

  display: flex;

  flex-direction: column;

  gap: 6px;
}


.filters-card label {

  color: var(--sigta-texto-suave);

  font-size: 15px;

  font-weight: 700;
}


.filters-card input,
.filters-card select {

  width: 100%;

  height: 41px;

  padding:
    0
    12px;

  border:
    1px solid var(--sigta-borde);

  border-radius: 7px;

  background: white;

  color: var(--sigta-azul);

  font-size: 17px;

  outline: none;
}


.filters-card input:focus,
.filters-card select:focus {

  border-color: var(--sigta-texto-suave);

  box-shadow:
    0
    0
    0
    3px
    rgba(11,87,149,.08);
}


/* =========================================================
   ALERTAS
========================================================= */

.alert {

  margin-bottom: 14px;

  padding:
    11px
    14px;

  border-radius: 7px;

  font-size: 17px;
}


.alert.success {

  background: var(--sigta-exito-fondo);

  color: var(--sigta-exito);
}


.alert.error {

  background: var(--sigta-error-fondo);

  color: var(--sigta-error);
}


/* =========================================================
   TABLA
========================================================= */

.table-card {

  overflow: hidden;

  border-radius: 10px;

  background: white;

  box-shadow:
    0
    4px
    14px
    rgba(0,0,0,.06);
}


.table-header {

  display: flex;

  align-items: center;

  justify-content:
    space-between;

  gap: 12px;

  padding:
    17px
    18px;

  border-bottom:
    1px solid var(--sigta-borde);
}


.table-header h2 {

  margin: 0;

  color: var(--sigta-texto);

  font-size: 21px;
}


.table-header p {

  margin:
    3px
    0
    0;

  color: var(--sigta-texto-suave);

  font-size: 15px;
}


.result-count {

  padding:
    5px
    8px;

  border-radius: 15px;

  background: var(--sigta-azul-tenue);

  color: var(--sigta-texto-suave);

  font-size: 14px;

  font-weight: 700;
}


.table-wrapper {

  width: 100%;

  overflow-x: auto;
}


table {

  width: 100%;

  min-width: 1100px;

  border-collapse:
    collapse;
}


th {

  padding:
    13px
    14px;

  background: var(--sigta-azul-tenue);

  color: var(--sigta-texto-suave);

  text-align: left;

  font-size: 15px;

  font-weight: 800;

  text-transform:
    uppercase;
}


td {

  padding:
    14px;

  border-top:
    1px solid var(--sigta-azul-tenue);

  color: var(--sigta-texto-suave);

  font-size: 16px;

  vertical-align: middle;
}


td strong {

  color: var(--sigta-azul);
}


/* =========================================================
   USUARIO TABLA
========================================================= */

.user-cell {

  display: flex;

  align-items: center;

  gap: 9px;
}


.table-avatar {

  width: 32px;

  height: 32px;

  flex-shrink: 0;

  display: flex;

  align-items: center;

  justify-content: center;

  border-radius: 50%;

  background: var(--sigta-azul-tenue);

  color: var(--sigta-azul);

  font-size: 15px;

  font-weight: 900;
}


.user-cell strong,
.user-cell small {

  display: block;
}


.user-cell small {

  margin-top: 2px;

  color: var(--sigta-texto-suave);

  font-size: 13px;
}


/* =========================================================
   BADGES
========================================================= */

.badge {

  display: inline-block;

  padding:
    5px
    9px;

  border-radius: 20px;

  font-size: 14px;

  font-weight: 700;
}


.badge.activo {

  background: var(--sigta-exito-fondo);

  color: var(--sigta-exito);
}


.badge.inactivo {

  background: var(--sigta-error-fondo);

  color: var(--sigta-error);
}


.role-badge {

  display: inline-block;

  padding:
    5px
    7px;

  border-radius: 5px;

  background: var(--sigta-azul-tenue);

  color: var(--sigta-texto-suave);

  font-size: 14px;
}


.first-login {

  font-size: 15px;

  font-weight: 700;
}


.first-login.pending {

  color: var(--sigta-mostaza-oscuro);
}


.first-login.completed {

  color: var(--sigta-exito);
}


/* =========================================================
   ACCIONES
========================================================= */

.actions {

  display: flex;

  gap: 6px;
}


.actions button {

  padding:
    6px
    9px;

  border: none;

  border-radius: 5px;

  font-size: 14px;

  font-weight: 700;

  cursor: pointer;
}


.btn-edit {

  background: var(--sigta-azul-tenue);

  color: var(--sigta-azul);
}


.btn-disable {

  background: var(--sigta-error-fondo);

  color: var(--sigta-error);
}


.btn-enable {

  background: var(--sigta-exito-fondo);

  color: var(--sigta-exito);
}

.btn-reset-password {
  background: #fff7d6;
  color: var(--sigta-azul);
}


/* =========================================================
   CARGA / VACÍO
========================================================= */

.loading,
.empty {

  padding: 45px;

  text-align: center;

  color: var(--sigta-texto-suave);

  font-size: 17px;
}


/* =========================================================
   MODAL
========================================================= */

.modal-overlay {

  position: fixed;

  inset: 0;

  display: flex;

  align-items: center;

  justify-content: center;

  padding: 20px;

  background:
    rgba(7,35,60,.58);

  z-index: 1000;
}


.modal {

  width: 100%;

  max-width: 610px;

  max-height: 90vh;

  overflow-y: auto;

  padding: 24px;

  border-top:
    4px solid var(--sigta-mostaza);

  border-radius: 12px;

  background: white;

  box-shadow:
    0
    20px
    60px
    rgba(0,0,0,.25);
}


.modal-header {

  display: flex;

  justify-content:
    space-between;

  gap: 15px;

  margin-bottom: 20px;
}


.modal-kicker {

  display: block;

  margin-bottom: 5px;

  color: var(--sigta-texto-suave);

  font-size: 14px;

  text-transform:
    uppercase;

  font-weight: 800;
}


.modal-header h2 {

  margin: 0;

  color: var(--sigta-texto);

  font-size: 20px;
}


.modal-header p {

  margin:
    4px
    0
    0;

  color: var(--sigta-texto-suave);

  font-size: 16px;
}


.close {

  border: none;

  background: transparent;

  color: var(--sigta-texto-suave);

  font-size: 27px;

  cursor: pointer;
}


/* =========================================================
   FORMULARIO
========================================================= */

.grid {

  display: grid;

  grid-template-columns:
    1fr
    1fr;

  gap: 14px;
}


.field {

  display: flex;

  flex-direction: column;

  gap: 6px;
}


.field.full {

  grid-column:
    1 / -1;
}


.field label {

  color: var(--sigta-azul);

  font-size: 16px;

  font-weight: 700;
}


.field label span {

  color: var(--sigta-error);
}


.field input,
.field select {

  width: 100%;

  height: 42px;

  padding:
    0
    12px;

  border:
    1px solid var(--sigta-borde);

  border-radius: 7px;

  background: white;

  color: var(--sigta-azul);

  outline: none;

  font-size: 17px;
}


.field input:focus,
.field select:focus {

  border-color: var(--sigta-texto-suave);

  box-shadow:
    0
    0
    0
    3px
    rgba(11,87,149,.1);
}


.field select:disabled {

  background: var(--sigta-azul-tenue);

  color: var(--sigta-texto-suave);

  cursor: not-allowed;
}


.field small {

  color: var(--sigta-texto-suave);

  font-size: 14px;

  line-height: 1.4;
}

.id-column {
  width: 54px;
  padding-right: 8px;
  padding-left: 12px;
  text-align: center;
  white-space: nowrap;
}

.password-field {
  position: relative;
}

.password-field input {
  padding-right: 48px;
}

.password-eye {
  position: absolute;
  top: 50%;
  right: 8px;
  transform: translateY(-50%);
  width: 34px;
  height: 34px;
  border: 0;
  border-radius: 6px;
  background: var(--sigta-azul-tenue);
  cursor: pointer;
}

.password-eye:disabled {
  cursor: not-allowed;
  opacity: .45;
}


/* =========================================================
   ERROR MODAL
========================================================= */

.modal-error {

  margin-top: 14px;

  padding: 10px;

  border-radius: 6px;

  background: var(--sigta-error-fondo);

  color: var(--sigta-error);

  font-size: 16px;
}

.modal-success {
  margin-top: 14px;
  padding: 10px;
  border-radius: 6px;
  background: var(--sigta-exito-fondo);
  color: var(--sigta-exito);
  font-size: 16px;
}

.confirm-modal {
  max-width: 500px;
  text-align: center;
}

.confirm-modal h2 {
  margin: 12px 0 8px;
  color: var(--sigta-azul);
}

.confirm-modal > p {
  color: var(--sigta-texto-suave);
}


/* =========================================================
   MODAL GELATINOSO (usuario creado)
========================================================= */

.jelly-overlay {
  z-index: 1300;
  animation: jelly-fade .25s ease both;
}

@keyframes jelly-fade {
  from { opacity: 0; }
  to   { opacity: 1; }
}

.jelly-modal {
  max-width: 440px;
  border-top-color: #17a34a;
  transform-origin: center bottom;
  animation: jelly-in .85s cubic-bezier(.25, .8, .3, 1) both;
}

@keyframes jelly-in {
  0%   { transform: scale(0, 0); }
  20%  { transform: scale(1.22, .78); }
  36%  { transform: scale(.82, 1.18); }
  52%  { transform: scale(1.11, .89); }
  68%  { transform: scale(.94, 1.06); }
  82%  { transform: scale(1.04, .96); }
  92%  { transform: scale(.99, 1.01); }
  100% { transform: scale(1, 1); }
}

.jelly-check {
  width: 74px;
  height: 74px;
  margin: 4px auto 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #e3f7ec;
  color: #17a34a;
  animation: jelly-check-pop .6s cubic-bezier(.2, 1.6, .35, 1) .2s both;
}

@keyframes jelly-check-pop {
  0%   { transform: scale(0); }
  55%  { transform: scale(1.18); }
  100% { transform: scale(1); }
}

.jelly-note {
  margin: 0 0 4px;
  padding: 9px 12px;
  border-radius: 8px;
  background: var(--sigta-mostaza-suave, #fdf2d4);
  color: #8a6d1e;
  font-size: 13px;
  font-weight: 600;
}

.jelly-modal .modal-actions {
  justify-content: center;
}

.jelly-ok {
  min-width: 130px;
  background: #17a34a;
  transition: transform .12s ease;
}

.jelly-ok:hover {
  transform: scale(1.04);
}

.jelly-ok:active {
  transform: scale(.96);
}

@media (prefers-reduced-motion: reduce) {
  .jelly-overlay,
  .jelly-modal,
  .jelly-check {
    animation: none;
  }
}

.confirm-icon {
  display: grid;
  place-items: center;
  width: 48px;
  height: 48px;
  margin: 0 auto;
  border-radius: 50%;
  font-size: 26px;
  font-weight: 800;
}

.confirm-icon.inactivar {
  background: var(--sigta-error-fondo);
  color: var(--sigta-error);
}

.confirm-icon.activar {
  background: var(--sigta-exito-fondo);
  color: var(--sigta-exito);
}

.confirm-icon.reset-password {
  background: #fff7d6;
  color: var(--sigta-azul);
}

.confirm-user-data {
  margin: 20px 0;
  padding: 14px;
  border: 1px solid var(--sigta-borde);
  border-radius: 8px;
  background: var(--sigta-azul-tenue);
  text-align: left;
}

.confirm-user-data div {
  display: grid;
  grid-template-columns: 80px 1fr;
  gap: 8px;
  padding: 4px 0;
}

.confirm-user-data dt { font-weight: 700; color: var(--sigta-azul); }
.confirm-user-data dd { margin: 0; overflow-wrap: anywhere; }

.confirm-warning {
  padding: 12px;
  border-left: 4px solid var(--sigta-mostaza);
  border-radius: 6px;
  background: #fff9e6;
  text-align: left;
}

.btn-confirm-disable,
.btn-confirm-enable {
  min-height: 40px;
  padding: 0 16px;
  border: 0;
  border-radius: 7px;
  color: white;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
}

.btn-confirm-disable { background: var(--sigta-error); }
.btn-confirm-enable { background: var(--sigta-azul); }

.btn-confirm-reset {
  min-height: 40px;
  padding: 0 16px;
  border: 0;
  border-radius: 7px;
  background: var(--sigta-azul);
  color: white;
  font-size: 16px;
  font-weight: 700;
  cursor: pointer;
}

.btn-confirm-reset:disabled {
  cursor: not-allowed;
  opacity: .6;
}

.generated-password-modal {
  max-width: 520px;
}

.generated-password-modal h2 {
  margin: 12px 0 18px;
  color: var(--sigta-azul);
  text-align: center;
}

.one-time-notice {
  margin-top: 16px;
  padding: 12px;
  border-left: 4px solid var(--sigta-mostaza);
  border-radius: 6px;
  background: #fff9e6;
  color: var(--sigta-texto-suave);
}

.one-time-notice strong,
.one-time-notice span {
  display: block;
}

.one-time-notice span {
  margin-top: 4px;
}


/* =========================================================
   ACCIONES MODAL
========================================================= */

.modal-actions {

  display: flex;

  justify-content:
    flex-end;

  gap: 10px;

  margin-top: 22px;
}


.btn-cancel,
.btn-save {

  min-height: 40px;

  padding:
    0
    16px;

  border-radius: 7px;

  font-size: 16px;

  font-weight: 700;

  cursor: pointer;
}


.btn-cancel {

  border:
    1px solid var(--sigta-borde);

  background: white;

  color: var(--sigta-texto-suave);
}


.btn-save {

  border: none;

  background: var(--sigta-azul);

  color: white;
}


.btn-save:disabled {

  opacity: .6;

  cursor: not-allowed;
}


/* =========================================================
   RESPONSIVE
========================================================= */

@media (
  max-width: 1050px
) {

  .stats-grid {

    grid-template-columns:
      repeat(2,1fr);
  }

}


@media (
  max-width: 760px
) {

  .admin-layout {

    display: block;
  }


  .main-content {

    padding: 18px;
  }


  .topbar {

    align-items:
      flex-start;

    flex-direction:
      column;
  }


  .stats-grid {

    grid-template-columns:
      1fr
      1fr;
  }


  .filters-card {

    grid-template-columns:
      1fr;
  }


  .grid {

    grid-template-columns:
      1fr;
  }


  .field.full {

    grid-column: auto;
  }

}


@media (
  max-width: 480px
) {

  .stats-grid {

    grid-template-columns:
      1fr;
  }


  .modal-actions {

    flex-direction:
      column-reverse;
  }


  .btn-cancel,
  .btn-save {

    width: 100%;
  }

}

/* =========================================================
   DISEÑO REFERENCIA
========================================================= */

.admin-layout {
  background:
    radial-gradient(circle at 28% 0%, rgba(38, 113, 204, .08), transparent 31%),
    linear-gradient(180deg, #f7fbff 0%, #eef6fd 100%);
}

.main-content {
  padding: 0;
  color: #07194a;
}

.admin-topbar {
  min-height: 64px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 18px;
  padding: 0 34px;
  border-bottom: 1px solid #e4edf7;
  background: rgba(255, 255, 255, .86);
  box-shadow: 0 8px 24px rgba(30, 76, 124, .08);
}

.session-panel {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 16px;
  min-width: 0;
  max-width: 100%;
}

.notification-button {
  position: relative;
  display: inline-grid;
  place-items: center;
  width: 36px;
  height: 36px;
  flex: 0 0 36px;
  border: 0;
  border-radius: 7px;
  background: transparent;
  color: #075ebd;
  cursor: pointer;
}

.notification-button span {
  position: absolute;
  top: 5px;
  right: 6px;
  width: 10px;
  height: 10px;
  border: 2px solid #fff;
  border-radius: 50%;
  background: #ffc228;
}

.session-divider {
  width: 1px;
  height: 28px;
  flex: 0 0 1px;
  background: #e4edf7;
}

.session-profile {
  display: grid;
  grid-template-columns: 36px minmax(0, 1fr);
  align-items: center;
  gap: 10px;
  min-width: 0;
  max-width: 240px;
  padding: 6px 0;
}

.session-avatar {
  display: grid;
  place-items: center;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: #075ebd;
  color: #fff;
  font-size: 16px;
  line-height: 1;
  font-weight: 700;
}

.session-copy {
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 1px;
  text-align: left;
}

.session-copy strong {
  color: #14304f;
  font-size: 14px;
  line-height: 1.35;
  font-weight: 700;
  white-space: normal;
  overflow-wrap: anywhere;
}

.session-copy small {
  color: #5b7189;
  font-size: 12px;
  line-height: 1.4;
  overflow-wrap: anywhere;
}

.page-header,
.stats-grid,
.filters-card,
.alert,
.table-card {
  width: min(100%, 1510px);
  margin-right: auto;
  margin-left: auto;
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 24px;
  margin-top: 40px;
  margin-bottom: 28px;
  padding: 0 34px;
}

.page-title {
  display: grid;
  grid-template-columns: 52px minmax(0, 1fr);
  column-gap: 18px;
  align-items: center;
}

.page-icon {
  grid-row: span 2;
  color: #126fd4;
}

.page-title h1 {
  margin: 0;
  color: #061546;
  font-size: 40px !important;
  line-height: 1.05 !important;
  font-weight: 900;
  letter-spacing: 0;
}

.page-title p {
  margin: 8px 0 0;
  color: #5b7199;
  font-size: 18px;
}

.btn-primary {
  min-width: 224px;
  min-height: 56px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 0 24px;
  border: 1px solid #ffbd18;
  border-radius: 8px;
  background: linear-gradient(180deg, #ffc635, #ffb616);
  color: #061546;
  box-shadow: 0 10px 22px rgba(255, 184, 22, .24);
  font-size: 18px;
  font-weight: 900;
}

.btn-primary:hover {
  background: linear-gradient(180deg, #ffd151, #ffbd18);
}

.stats-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 16px;
  margin-bottom: 22px;
  padding: 0 34px;
}

.stat-card {
  min-height: 136px;
  display: grid;
  grid-template-columns: 70px minmax(0, 1fr);
  align-items: center;
  gap: 18px;
  padding: 22px 24px;
  border: 1px solid #edf3f9;
  border-top: 0;
  border-radius: 8px;
  background: rgba(255, 255, 255, .95);
  box-shadow: 0 16px 34px rgba(21, 72, 122, .10);
}

.stat-card .stat-icon {
  display: grid;
  place-items: center;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  overflow: hidden;
}

.stat-card .stat-icon > svg {
  display: block;
}

.stat-card.total .stat-icon {
  background: #eaf3ff;
  color: #126fd4;
}

.stat-card.activos .stat-icon {
  background: #dff5eb;
  color: #08a555;
}

.stat-card.inactivos .stat-icon {
  background: #fde7e7;
  color: #d92924;
}

.stat-card.pendientes .stat-icon {
  background: #fff2c9;
  color: #dc9b00;
}

.stat-label {
  color: #31507d;
  font-size: 14px;
  font-weight: 900;
  text-transform: uppercase;
}

.stat-card strong {
  margin: 7px 0 4px;
  color: #061b5d;
  font-size: 40px;
  line-height: 1;
  font-weight: 900;
}

.stat-card small {
  color: #526a94;
  font-size: 15px;
}

.filters-card {
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 26px;
  margin-bottom: 22px;
  padding: 22px 24px;
  border: 1px solid #e7eff8;
  border-radius: 8px;
  background: rgba(255, 255, 255, .95);
  box-shadow: 0 16px 34px rgba(21, 72, 122, .10);
}

.filters-card label {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #061b5d;
  font-size: 16px;
  font-weight: 900;
}

.filters-card label .icono-sigta {
  color: #075ebd;
}

.filters-card input,
.filters-card select {
  height: 48px;
  padding: 0 18px;
  border-color: #c9d8e9;
  border-radius: 6px;
  color: #0d2b67;
  font-size: 16px;
}

.filters-card input::placeholder {
  color: #778aac;
}

.table-card {
  margin-bottom: 26px;
  overflow: hidden;
  border: 1px solid #e3edf7;
  border-radius: 8px;
  background: rgba(255, 255, 255, .98);
  box-shadow: 0 18px 38px rgba(21, 72, 122, .12);
}

.table-header {
  padding: 22px 24px;
  border-bottom-color: #dce8f5;
}

.table-header h2 {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #061b5d;
  font-size: 23px !important;
  font-weight: 900;
}

.table-header h2 .icono-sigta {
  color: #126fd4;
}

.table-header p {
  color: #5b7199;
  font-size: 16px;
}

.result-count {
  padding: 8px 16px;
  border-radius: 999px;
  background: #edf4fb;
  color: #405f8f;
  font-size: 15px;
  font-weight: 850;
}

table {
  min-width: 1220px;
}

th {
  padding: 15px 20px;
  background: linear-gradient(180deg, #f5f9fd, #edf5fc);
  color: #48628d;
  font-size: 14px;
  letter-spacing: 0;
}

td {
  padding: 13px 20px;
  border-top-color: #e4edf6;
  color: #536b96;
  font-size: 16px;
}

tbody tr {
  transition: background .15s ease;
}

tbody tr:hover {
  background: #f8fbfe;
}

.id-column {
  width: 56px;
  text-align: left;
}

.user-cell {
  gap: 14px;
}

.table-avatar {
  width: 42px;
  height: 42px;
  background: #eaf3ff;
  color: #061b5d;
  font-size: 17px;
}

.user-cell strong {
  color: #061b5d;
  font-size: 16px;
  font-weight: 900;
}

.role-badge {
  padding: 8px 12px;
  border-radius: 6px;
  background: #edf3f9;
  color: #536b96;
  font-size: 15px;
}

.badge,
.first-login {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-height: 30px;
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 14px;
  font-weight: 850;
}

.badge::before,
.first-login::before {
  content: "";
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.badge.activo::before,
.first-login.completed::before {
  background: #08a555;
}

.badge.inactivo::before {
  background: #d92924;
}

.first-login.pending::before {
  background: #d4a000;
}

.first-login.pending {
  background: #fff3c8;
}

.first-login.completed {
  background: #dff5eb;
}

.actions {
  align-items: center;
  gap: 10px;
  flex-wrap: nowrap;
}

.actions button {
  min-height: 48px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 0 14px;
  border: 1px solid transparent;
  border-radius: 6px;
  font-size: 14px;
  line-height: 1.1;
  white-space: nowrap;
}

.btn-edit {
  border-color: #cfe1f7 !important;
  background: #eef6ff;
  color: #0863c4;
}

.btn-reset-password {
  border-color: #ffe6aa !important;
  background: #fff4d3;
  color: #061b5d;
}

.btn-disable {
  border-color: #ffd3d3 !important;
  background: #fde9e9;
  color: #c51f1a;
}

.btn-enable {
  border-color: #c8ead9 !important;
  background: #e7f7ef;
  color: #087340;
}

.table-footer {
  min-height: 66px;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 32px;
  padding: 14px 20px 18px;
  border-top: 1px solid #e4edf6;
  color: #48628d;
  font-size: 15px;
}

.pagination {
  display: inline-flex;
  align-items: center;
  gap: 8px;
}

.pagination button {
  min-width: 40px;
  height: 40px;
  border: 1px solid #d7e5f3;
  border-radius: 7px;
  background: #fff;
  color: #082764;
  font-size: 16px;
  font-weight: 850;
  cursor: pointer;
}

.pagination button.active {
  border-color: #075ebd;
  background: #0b72d9;
  color: #fff;
  box-shadow: 0 8px 18px rgba(8, 91, 188, .22);
}

.pagination button:disabled {
  color: #9aadc5;
  cursor: not-allowed;
}

@media (max-width: 1180px) {

  .stats-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {

  .main-content {
    padding: 0;
  }

  .admin-topbar {
    padding: 14px 18px;
    align-items: flex-start;
    flex-direction: column;
  }

  .session-panel {
    width: 100%;
    justify-content: flex-end;
  }

  .page-header {
    align-items: stretch;
    flex-direction: column;
    margin-top: 24px;
    padding: 0 18px;
  }

  .page-title {
    grid-template-columns: 42px minmax(0, 1fr);
    column-gap: 12px;
  }

  .page-icon .icono-sigta {
    width: 32px;
    height: 32px;
  }

  .page-title h1 {
    font-size: 30px !important;
  }

  .page-title p {
    font-size: 16px;
  }

  .btn-primary {
    width: 100%;
  }

  .stats-grid,
  .filters-card,
  .table-card {
    width: calc(100% - 36px);
    padding-right: 0;
    padding-left: 0;
  }

  .stats-grid {
    grid-template-columns: 1fr;
    padding: 0;
  }

  .filters-card {
    grid-template-columns: 1fr;
    padding: 18px;
  }

  .table-header,
  .table-footer {
    align-items: flex-start;
    flex-direction: column;
  }

  .table-footer {
    gap: 14px;
  }
}

/* Ajuste fino de escala para pantallas 1366-1920. */
.admin-topbar {
  min-height: 58px;
  padding: 0 28px;
}

.page-header,
.stats-grid,
.filters-card,
.alert,
.table-card {
  width: min(calc(100% - 56px), 1460px);
}

.page-header {
  margin-top: 28px;
  margin-bottom: 20px;
  padding: 0;
}

.page-title {
  grid-template-columns: 46px minmax(0, 1fr);
  column-gap: 14px;
}

.page-title h1 {
  font-size: 34px !important;
}

.page-title p {
  margin-top: 5px;
  font-size: 16px;
}

.page-icon .icono-sigta {
  width: 34px;
  height: 34px;
}

.btn-primary {
  min-width: 190px;
  min-height: 48px;
  padding: 0 20px;
  font-size: 16px;
}

.stats-grid {
  gap: 14px;
  margin-bottom: 18px;
  padding: 0;
}

.stat-card {
  min-height: 112px;
  grid-template-columns: 58px minmax(0, 1fr);
  gap: 14px;
  padding: 18px 18px;
}

.stat-card .stat-icon {
  width: 52px;
  height: 52px;
}

.stat-label {
  font-size: 13px;
}

.stat-card strong {
  margin: 5px 0 2px;
  font-size: 34px;
}

.stat-card small {
  font-size: 14px;
  line-height: 1.25;
}

.filters-card {
  grid-template-columns: minmax(0, 1fr) 300px;
  gap: 24px;
  margin-bottom: 18px;
  padding: 18px 20px;
}

.filters-card input,
.filters-card select {
  height: 42px;
}

.table-header {
  padding: 18px 20px;
}

.table-header h2 {
  font-size: 21px !important;
}

.table-header p {
  font-size: 15px;
}

.table-card {
  container: users-table / inline-size;
}

.table-wrapper {
  overflow: visible;
}

table {
  width: 100%;
  min-width: 0;
  table-layout: fixed;
}

th,
td {
  box-sizing: border-box;
  min-width: 0;
  padding: 10px 8px;
  white-space: nowrap;
  overflow-wrap: normal;
}

th {
  font-size: 12px;
}

td {
  font-size: 13px;
}

col.col-id {
  width: 44px;
}

/* Los controles reservan 560px; el resto se reparte entre los datos. */
col.col-user {
  width: calc((100% - 560px) * .30);
}

col.col-email {
  width: calc((100% - 560px) * .32);
}

col.col-role {
  width: calc((100% - 560px) * .23);
}

col.col-area {
  width: calc((100% - 560px) * .15);
}

col.col-status {
  width: 92px;
}

col.col-first-login {
  width: 124px;
}

col.col-actions {
  width: 300px;
}

.cell-text,
.role-badge {
  display: block;
  min-width: 0;
  max-width: 100%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.table-avatar {
  width: 28px;
  height: 28px;
  font-size: 12px;
}

.user-cell {
  min-width: 0;
  gap: 8px;
}

.user-details {
  min-width: 0;
}

.user-cell strong {
  font-size: 13px;
  line-height: 1.4;
  font-weight: 700;
}

.role-badge {
  width: fit-content;
  padding: 5px 8px;
  font-size: 13px;
}

.badge,
.first-login {
  min-height: 28px;
  padding: 5px 8px;
  gap: 6px;
  font-size: 12px;
  white-space: nowrap;
}

.badge::before,
.first-login::before {
  flex-shrink: 0;
}

.actions {
  display: flex;
  gap: 6px;
  width: 100%;
  flex-wrap: nowrap;
  align-items: stretch;
}

.actions button {
  flex: 1 1 auto;
  min-width: 0;
  width: auto;
  height: auto;
  min-height: 42px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 5px;
  padding: 6px;
  white-space: normal;
  line-height: 1.2;
  font-size: 12.5px;
}

.actions button .icono-sigta {
  flex-shrink: 0;
}

.actions button:focus-visible {
  outline: 2px solid #075ebd;
  outline-offset: 2px;
}

.table-footer {
  min-height: 58px;
  padding: 12px 20px;
}

.pagination button {
  min-width: 36px;
  height: 36px;
}

@container users-table (max-width: 979px) {
  table,
  tbody {
    display: block;
    width: 100%;
  }

  colgroup {
    display: none;
  }

  thead {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip-path: inset(50%);
  }

  tbody tr {
    display: block;
    padding: 12px 8px;
  }

  tbody tr + tr {
    border-top: 1px solid #e4edf6;
  }

  td {
    display: grid;
    grid-template-columns: 104px minmax(0, 1fr);
    align-items: center;
    gap: 12px;
    width: auto;
    padding: 5px 8px;
    border: 0;
  }

  td.id-column {
    width: auto;
  }

  td::before {
    content: attr(data-label);
    color: #48628d;
    font-size: 12px;
    font-weight: 600;
  }

  .badge,
  .first-login {
    justify-self: start;
  }

  .actions {
    flex-wrap: wrap;
  }

  .actions button {
    flex: 1 1 120px;
  }

  .table-header,
  .table-footer {
    flex-wrap: wrap;
    gap: 12px;
  }

  .pagination {
    gap: 4px;
  }

  .pagination button {
    min-width: 28px;
    height: 32px;
  }
}

@media (max-width: 760px) {

  .admin-topbar {
    min-height: auto;
    padding: 14px 18px;
  }

  .page-header,
  .stats-grid,
  .filters-card,
  .alert,
  .table-card {
    width: calc(100% - 36px);
  }

  .page-header {
    margin-top: 22px;
    padding: 0;
  }

  .stats-grid {
    grid-template-columns: 1fr;
  }

  .filters-card {
    grid-template-columns: 1fr;
  }
}

/* =========================================================
   ANIMACIÓN AL INACTIVAR / ELIMINAR USUARIO
========================================================= */

.anim-overlay {
  z-index: 1200;
}

.trash-anim,
.activar-anim {
  position: relative;
  width: 300px;
  height: 210px;
  border-radius: 26px;
  overflow: hidden;
  animation: ta-pop .34s cubic-bezier(.2, 1.4, .4, 1) both;
}

.trash-anim {
  background: linear-gradient(140deg, #5b1780 0%, #9b1fb8 55%, #b52bd0 100%);
  box-shadow: 0 26px 60px rgba(70, 8, 100, .5);
}

.activar-anim {
  background: linear-gradient(140deg, #0d7245 0%, #17a55f 55%, #2fc47c 100%);
  box-shadow: 0 26px 60px rgba(8, 80, 45, .5);
}

@keyframes ta-pop {
  from { opacity: 0; transform: scale(.72); }
  to   { opacity: 1; transform: scale(1); }
}

/* ---------- INACTIVAR: letras de "eliminar" ---------- */
.ta-letters {
  position: absolute;
  top: 30px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  gap: 3px;
}

.ta-letters span {
  color: #ffd86b;
  font-size: 21px;
  font-weight: 800;
  line-height: 1;
  animation: ta-suck .55s ease-in both;
  animation-delay: calc(var(--i) * .08s);
}

@keyframes ta-suck {
  0%   { transform: translateY(0) rotate(0) scale(1); opacity: 1; }
  60%  { opacity: 1; }
  100% { transform: translateY(66px) rotate(340deg) scale(.05); opacity: 0; }
}

.trash-anim.giro .ta-letters,
.trash-anim.listo .ta-letters { opacity: 0; }

/* Basurero */
.ta-can {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 46px;
  height: 46px;
  margin: -21px 0 0 -23px;
  color: #ffffff;
  filter: drop-shadow(0 6px 10px rgba(0, 0, 0, .35));
}

.trash-anim.accion .ta-can {
  animation: ta-jiggle .5s ease-in-out infinite;
}

@keyframes ta-jiggle {
  0%, 100% { transform: rotate(0); }
  25%      { transform: rotate(-7deg); }
  75%      { transform: rotate(7deg); }
}

.trash-anim.giro .ta-can {
  animation: ta-spin .75s cubic-bezier(.45, -0.35, .3, 1.4) forwards;
}

@keyframes ta-spin {
  0%   { transform: rotate(0) scale(1); }
  45%  { transform: rotate(230deg) scale(.78, 1.18); }
  72%  { transform: rotate(330deg) scale(1.18, .82); }
  100% { transform: rotate(360deg) scale(1); }
}

.trash-anim.listo .ta-can {
  opacity: .16;
  transition: opacity .3s ease;
}

/* ---------- ACTIVAR: letras de "activar" ---------- */
.aa-letters {
  position: absolute;
  bottom: 34px;
  left: 0;
  right: 0;
  display: flex;
  justify-content: center;
  gap: 3px;
}

.aa-letters span {
  color: #eafff2;
  font-size: 21px;
  font-weight: 800;
  line-height: 1;
  animation: aa-feed .55s ease-in both;
  animation-delay: calc(var(--i) * .08s);
}

@keyframes aa-feed {
  0%   { transform: translateY(0) rotate(0) scale(1); opacity: 1; }
  60%  { opacity: 1; }
  100% { transform: translateY(-70px) rotate(-320deg) scale(.05); opacity: 0; }
}

.activar-anim.giro .aa-letters,
.activar-anim.listo .aa-letters { opacity: 0; }

/* Anillos de energía */
.aa-rings {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
}

.aa-rings span {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 46px;
  height: 46px;
  margin: -23px 0 0 -23px;
  border: 2px solid rgba(255, 255, 255, .8);
  border-radius: 50%;
  opacity: 0;
}

.activar-anim.giro .aa-rings span,
.activar-anim.listo .aa-rings span {
  animation: aa-ring 1s ease-out infinite;
}

.activar-anim .aa-rings span:nth-child(2) { animation-delay: .33s; }
.activar-anim .aa-rings span:nth-child(3) { animation-delay: .66s; }

@keyframes aa-ring {
  0%   { opacity: .7; transform: scale(.5); }
  100% { opacity: 0;  transform: scale(2.6); }
}

/* Icono de usuario */
.aa-icon {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 46px;
  height: 46px;
  margin: -23px 0 0 -23px;
  color: #ffffff;
  filter: drop-shadow(0 6px 10px rgba(0, 0, 0, .3));
}

.activar-anim.accion .aa-icon {
  animation: aa-pulse .55s ease-in-out infinite;
}

@keyframes aa-pulse {
  0%, 100% { transform: scale(1); }
  50%      { transform: scale(1.14); }
}

.activar-anim.giro .aa-icon {
  animation: aa-spin .75s cubic-bezier(.45, -0.3, .3, 1.4) forwards;
}

@keyframes aa-spin {
  0%   { transform: rotate(0) scale(1); }
  45%  { transform: rotate(230deg) scale(1.2, .82); }
  72%  { transform: rotate(330deg) scale(.82, 1.2); }
  100% { transform: rotate(360deg) scale(1); }
}

.activar-anim.listo .aa-icon {
  opacity: .16;
  transition: opacity .3s ease;
}

/* ---------- Check final (compartido) ---------- */
.ta-check,
.aa-check {
  position: absolute;
  top: 50%;
  left: 50%;
  width: 40px;
  height: 40px;
  margin: -26px 0 0 -26px;
  padding: 6px;
  border-radius: 50%;
  background: #ffffff;
  color: #17a34a;
  opacity: 0;
  transform: scale(0);
}

.trash-anim.listo .ta-check,
.activar-anim.listo .aa-check {
  animation: ta-check .42s cubic-bezier(.2, 1.6, .4, 1) forwards;
}

@keyframes ta-check {
  to { opacity: 1; transform: scale(1); }
}

.ta-text,
.aa-text {
  position: absolute;
  left: 0;
  right: 0;
  bottom: 22px;
  margin: 0;
  text-align: center;
  color: #ffffff;
  font-size: 14px;
  font-weight: 700;
  letter-spacing: .3px;
}

.aa-text {
  top: 22px;
  bottom: auto;
}

@media (prefers-reduced-motion: reduce) {
  .trash-anim,
  .activar-anim,
  .ta-letters span,
  .aa-letters span,
  .trash-anim.accion .ta-can,
  .trash-anim.giro .ta-can,
  .activar-anim.accion .aa-icon,
  .activar-anim.giro .aa-icon,
  .aa-rings span,
  .trash-anim.listo .ta-check,
  .activar-anim.listo .aa-check {
    animation: none;
  }
  .ta-letters,
  .aa-letters { opacity: 0; }
  .trash-anim.listo .ta-check,
  .activar-anim.listo .aa-check { opacity: 1; transform: scale(1); }
}

</style>
