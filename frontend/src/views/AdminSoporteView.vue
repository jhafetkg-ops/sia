<template>
  <div class="admin-layout">

    <AdminMenu />

    <main class="main">

      <!-- =================================================
           ENCABEZADO
      ================================================== -->

      <header class="page-header">

        <div>
          <h1>Soporte Técnico</h1>

          <p>
            Gestión y seguimiento de tickets de Soporte UTIC.
          </p>
        </div>

        <button
          class="secondary-main-button"
          type="button"
          @click="router.push('/admin/tickets')"
        >
          Consultar listado
        </button>

      
        <UsuarioHeader @actualizar="cargarTodo" />
      </header>


      <!-- =================================================
           MÉTRICAS
      ================================================== -->

      <section class="metrics">

        <article>
          <span>Total tickets</span>
          <strong>{{ tickets.length }}</strong>
          <small>Registrados en Soporte Técnico</small>
        </article>

        <article>
          <span>Nuevos</span>
          <strong>{{ contar('NUEVO') }}</strong>
          <small>Pendientes de validación UTIC</small>
        </article>

        <article>
          <span>En atención</span>
          <strong>{{ enProceso }}</strong>
          <small>Tickets en proceso técnico</small>
        </article>

        <article>
          <span>Cerrados</span>
          <strong>{{ contar('CERRADO') }}</strong>
          <small>Tickets finalizados</small>
        </article>

      </section>


      <!-- =================================================
           MENSAJES
      ================================================== -->

      <div
        v-if="mensaje"
        :class="[
          'message',
          mensajeError ? 'error' : 'success'
        ]"
      >
        {{ mensaje }}
      </div>


      <!-- =================================================
           FLUJO
      ================================================== -->

      <section class="process-info">

        <div>
          <span class="section-label">
            FLUJO DE SOPORTE
          </span>

          <strong>
            Seguimiento institucional
          </strong>

          <p>
            Las actividades siguen el flujo definido para
            Jefe de UTIC, Especialista y Solicitante.
          </p>
        </div>

        <div class="process-steps">
          <span>Recibir y validar</span>
          <span>Clasificar prioridad y SLA</span>
          <span>Designar especialista</span>
          <span>Diagnóstico</span>
          <span>Intervención</span>
          <span>Pruebas</span>
          <span>Verificación</span>
          <span>Conformidad</span>
        </div>

      </section>


      <!-- =================================================
           KANBAN
      ================================================== -->

      <!-- =================================================
           INFORMES DE ACTIVIDADES RECIBIDOS

           BPMN: al validar el informe final, la jefatura lo eleva
           y la Dirección lo recibe para su conocimiento.
      ================================================== -->
      <section v-if="informesRecibidos.length" class="informes-direccion">

        <div class="informes-head">
          <div>
            <h2>Informes de actividades recibidos</h2>
            <p>Expedientes cerrados cuyo informe final elevó la jefatura de UTIC.</p>
          </div>
          <span class="informes-total">{{ informesRecibidos.length }}</span>
        </div>

        <article
          v-for="t in informesRecibidos"
          :key="`informe-${t.id}`"
          class="informe-item"
        >
          <div class="informe-cabecera">
            <strong>{{ t.codigo }}</strong>
            <span>{{ t.titulo }}</span>
            <small>Elevado el {{ fechaInforme(t.informe_elevado_en) }}</small>
          </div>
          <p>{{ t.informe_final }}</p>
          <div class="informe-acuse">
            <span v-if="t.proceso_finalizado_en" class="acuse-listo">
              ✓ Informe recibido · proceso del ticket cerrado
            </span>
            <template v-else>
              <span class="acuse-estado">Pendiente de su acuse de recibo</span>
              <button
                class="primary-action"
                type="button"
                @click="acusarInforme(t)"
              >
                Acusar recibo
              </button>
            </template>
          </div>
        </article>

      </section>


      <section class="kanban-section">

        <div class="kanban-title-row">

          <div>
            <span class="section-label">
              TABLERO KANBAN
            </span>

            <h2>
              Estado de los tickets
            </h2>
          </div>

          <button
            class="refresh-button"
            type="button"
            :disabled="cargando"
            @click="cargarTodo"
          >
            {{ cargando ? 'Actualizando...' : 'Actualizar' }}
          </button>

        </div>

        <div
          v-if="cargando"
          class="loading"
        >
          Cargando tickets...
        </div>

        <div
          v-else
          class="kanban-wrapper"
        >

          <div class="kanban">

            <section
              v-for="columna in columnas"
              :key="columna.codigo"
              class="column"
            >

              <header class="column-header">

                <div>
                  <strong>
                    {{ columna.nombre }}
                  </strong>

                  <small>
                    {{ columna.descripcion }}
                  </small>
                </div>

                <span>
                  {{ ticketsPorColumna(columna).length }}
                </span>

              </header>

              <div class="column-body">

                <article
                  v-for="ticket in ticketsPorColumna(columna)"
                  :key="ticket.id"
                  class="ticket-card"
                  @click="abrirTicket(ticket)"
                >

                  <div class="ticket-top">

                    <strong>
                      {{ ticket.codigo }}
                    </strong>

                    <span
                      :class="[
                        'priority',
                        clasePrioridad(ticket.prioridad)
                      ]"
                    >
                      {{ textoPrioridad(ticket.prioridad) }}
                    </span>

                  </div>

                  <div
                    v-if="ticket.sla_horas"
                    :class="[
                      'sla-badge',
                      claseSla(ticket.sla_estado)
                    ]"
                  >
                    {{ textoSla(ticket) }}
                  </div>

                  <h3>
                    {{ ticket.titulo }}
                  </h3>

                  <span class="category">
                    {{
                      ticket.categoria_nombre
                      || 'Sin categoría'
                    }}
                  </span>

                  <div class="ticket-info">

                    <div>
                      <span>Área</span>
                      <strong>
                        {{
                          ticket.area_nombre
                          || 'No indicada'
                        }}
                      </strong>
                    </div>

                    <div>
                      <span>Ubicación</span>
                      <strong>
                        {{
                          ticket.ubicacion
                          || 'No indicada'
                        }}
                      </strong>
                    </div>

                    <div>
                      <span>Responsable</span>
                      <strong>
                        {{
                          ticket.tecnico_nombre
                          || 'Sin asignar'
                        }}
                      </strong>
                    </div>

                  </div>

                  <div class="ticket-footer">

                    <div>
                      <span>Solicitante</span>
                      <strong>
                        {{
                          ticket.solicitante_nombre
                          || 'Sin información'
                        }}
                      </strong>
                    </div>

                    <button
                      type="button"
                      @click.stop="abrirTicket(ticket)"
                    >
                      Gestionar
                    </button>

                  </div>

                </article>

                <div
                  v-if="
                    ticketsPorColumna(columna).length === 0
                  "
                  class="empty-column"
                >
                  Sin tickets
                </div>

              </div>

            </section>

          </div>

        </div>

      </section>

    </main>


    <!-- =====================================================
         MODAL TICKET
    ====================================================== -->

    <div
      v-if="ticketSeleccionado"
      class="overlay"
      @click.self="cerrarTicket"
    >

      <section class="ticket-modal">

        <!-- =================================================
             CABECERA
        ================================================== -->

        <header class="modal-header">

          <div>

            <span class="modal-code">
              {{ ticketSeleccionado.codigo }}
            </span>

            <h2>
              {{ ticketSeleccionado.titulo }}
            </h2>

            <p>
              Requerimiento de Soporte Técnico
            </p>

          </div>

          <button
            class="close-button"
            type="button"
            @click="cerrarTicket"
          >
            ×
          </button>

        </header>


        <!-- =================================================
             RESUMEN
        ================================================== -->

        <DocumentosExpediente v-if="ticketSeleccionado" base="/api/soporte/tickets" :id="ticketSeleccionado.id" />
        <section class="status-grid">

          <article>
            <span>Estado</span>

            <strong>
              {{
                ticketSeleccionado.estado_nombre
                || ticketSeleccionado.estado_codigo
                || 'Sin estado'
              }}
            </strong>
          </article>

          <article>
            <span>Prioridad</span>

            <strong>
              {{
                textoPrioridad(
                  ticketSeleccionado.prioridad
                )
              }}
            </strong>
          </article>

          <article>
            <span>SLA</span>

            <strong>
              {{
                ticketSeleccionado.sla_horas
                  ? ticketSeleccionado.sla_horas + ' horas'
                  : 'Sin asignar'
              }}
            </strong>
          </article>

          <article>
            <span>Responsable</span>

            <strong>
              {{
                ticketSeleccionado.tecnico_nombre
                || 'Sin asignar'
              }}
            </strong>
          </article>

        </section>


        <!-- =================================================
             DATOS GENERALES
        ================================================== -->

        <section class="modal-section">

          <div class="section-number">
            1
          </div>

          <div class="section-content">

            <h3>
              Información del requerimiento
            </h3>

            <div class="detail-grid">

              <div>
                <span>Solicitante</span>

                <strong>
                  {{
                    ticketSeleccionado.solicitante_nombre
                    || '-'
                  }}
                </strong>
              </div>

              <div>
                <span>Correo</span>

                <strong>
                  {{
                    ticketSeleccionado.solicitante_email
                    || '-'
                  }}
                </strong>
              </div>

              <div>
                <span>Área solicitante</span>

                <strong>
                  {{
                    ticketSeleccionado.area_nombre
                    || '-'
                  }}
                </strong>
              </div>

              <div>
                <span>Categoría</span>

                <strong>
                  {{
                    ticketSeleccionado.categoria_nombre
                    || '-'
                  }}
                </strong>
              </div>

              <div>
                <span>Ubicación</span>

                <strong>
                  {{
                    ticketSeleccionado.ubicacion
                    || '-'
                  }}
                </strong>
              </div>

              <div>
                <span>Equipo afectado</span>

                <strong>
                  {{
                    ticketSeleccionado.equipo_afectado
                    || '-'
                  }}
                </strong>
              </div>

            </div>

          </div>

        </section>


        <!-- =================================================
             DESCRIPCIÓN
        ================================================== -->

        <section class="modal-section">

          <div class="section-number">
            2
          </div>

          <div class="section-content">

            <h3>
              Descripción
            </h3>

            <div class="description-box">
              {{
                ticketSeleccionado.descripcion
                || 'Sin descripción.'
              }}
            </div>

          </div>

        </section>


        <!-- =================================================
             EVIDENCIA
        ================================================== -->

        <section class="modal-section">

          <div class="section-number">
            3
          </div>

          <div class="section-content">

            <h3>
              Evidencia cargada
            </h3>

            <div
              v-if="
                ticketSeleccionado.evidencia
                || ticketSeleccionado.evidencia_archivo_url
              "
              class="evidence-box"
            >

              <p
                v-if="ticketSeleccionado.evidencia"
              >
                {{ ticketSeleccionado.evidencia }}
              </p>

              <a
                v-if="
                  ticketSeleccionado.evidencia_archivo_url
                "
                :href="
                  ticketSeleccionado.evidencia_archivo_url
                "
                target="_blank"
                rel="noopener"
              >
                Ver archivo cargado
              </a>

            </div>

            <div
              v-else
              class="empty-evidence"
            >
              No se cargó evidencia.
            </div>

          </div>

        </section>


        <!-- =================================================
             SLA
        ================================================== -->

        <section
          v-if="ticketSeleccionado.sla_horas"
          class="modal-section"
        >

          <div class="section-number">
            4
          </div>

          <div class="section-content">

            <h3>
              Clasificación y SLA
            </h3>

            <div class="detail-grid">

              <div>
                <span>Prioridad</span>

                <strong>
                  {{
                    textoPrioridad(
                      ticketSeleccionado.prioridad
                    )
                  }}
                </strong>
              </div>

              <div>
                <span>SLA asignado</span>

                <strong>
                  {{
                    ticketSeleccionado.sla_horas
                  }} horas
                </strong>
              </div>

              <div>
                <span>Fecha límite</span>

                <strong>
                  {{
                    formatearFecha(
                      ticketSeleccionado.sla_fecha_limite
                    )
                  }}
                </strong>
              </div>

              <div>
                <span>Estado del SLA</span>

                <strong>
                  {{
                    textoEstadoSla(
                      ticketSeleccionado.sla_estado
                    )
                  }}
                </strong>
              </div>

              <div class="full-width">
                <span>Criterio técnico</span>

                <strong>
                  {{
                    ticketSeleccionado.criterio_tecnico
                    || 'Sin criterio registrado'
                  }}
                </strong>
              </div>

            </div>

          </div>

        </section>


        <!-- =================================================
             ATENCIÓN TÉCNICA
        ================================================== -->

        <section
          v-if="
            ticketSeleccionado.diagnostico
            || ticketSeleccionado.plan_solucion
            || ticketSeleccionado.solucion
            || ticketSeleccionado.resultado_pruebas
          "
          class="modal-section"
        >

          <div class="section-number">
            5
          </div>

          <div class="section-content">

            <h3>
              Atención técnica
            </h3>

            <div
              v-if="ticketSeleccionado.diagnostico"
              class="text-block"
            >
              <span>Diagnóstico</span>

              <p>
                {{ ticketSeleccionado.diagnostico }}
              </p>
            </div>

            <div
              v-if="ticketSeleccionado.plan_solucion"
              class="text-block"
            >
              <span>Plan de solución</span>

              <p>
                {{ ticketSeleccionado.plan_solucion }}
              </p>
            </div>

            <div
              v-if="ticketSeleccionado.solucion"
              class="text-block"
            >
              <span>Intervención realizada</span>

              <p>
                {{ ticketSeleccionado.solucion }}
              </p>
            </div>

            <div
              v-if="
                ticketSeleccionado.resultado_pruebas
              "
              class="text-block"
            >
              <span>Resultado de pruebas</span>

              <p>
                {{
                  ticketSeleccionado.resultado_pruebas
                }}
              </p>
            </div>

          </div>

        </section>


        <!-- =================================================
             ACCIONES DEL PROCESO
        ================================================== -->

        <section class="workflow-section">

          <span class="section-label">
            ACTIVIDAD DEL PROCESO
          </span>


          <!-- =================================================
               NUEVO
          ================================================== -->

          <div
            v-if="estadoActual === 'NUEVO'"
            class="action-card"
          >

            <div class="action-title">

              <div>
                <span class="step-number">
                  1
                </span>

                <div>
                  <h3>
                    Recibir Ticket y validar Ticket
                  </h3>

                  <p>
                    Verifique la información registrada antes
                    de iniciar la atención.
                  </p>
                </div>
              </div>

            </div>

            <div class="validation-list">
              <span>✓ Solicitante identificado</span>
              <span>✓ Área solicitante</span>
              <span>✓ Categoría</span>
              <span>✓ Ubicación</span>
              <span>✓ Equipo afectado</span>
            </div>

            <button
              class="primary-action"
              type="button"
              :disabled="procesando"
              @click="validarTicket"
            >
              {{
                procesando
                  ? 'Procesando...'
                  : 'Recibir y validar Ticket'
              }}
            </button>

          </div>


          <!-- =================================================
               EN ANÁLISIS: CLASIFICAR
          ================================================== -->

          <div
            v-else-if="
              estadoActual === 'EN_ANALISIS'
              && !ticketSeleccionado.prioridad
            "
            class="action-card"
          >

            <div class="action-title">

              <div>
                <span class="step-number">
                  2
                </span>

                <div>
                  <h3>
                    Clasificar prioridad y asignar SLA
                  </h3>

                  <p>
                    Determine el nivel de prioridad de acuerdo
                    con el impacto del requerimiento.
                  </p>
                </div>
              </div>

            </div>

            <div class="form-grid">

              <div class="field">

                <label>
                  Prioridad
                </label>

                <select
                  v-model="formClasificacion.prioridad"
                >
                  <option value="">
                    Seleccione prioridad
                  </option>

                  <option value="BAJA">
                    Baja
                  </option>

                  <option value="MEDIA">
                    Media
                  </option>

                  <option value="ALTA">
                    Alta
                  </option>

                  <option value="CRITICA">
                    Crítica
                  </option>
                </select>

              </div>

              <div class="sla-preview">

                <span>
                  SLA que se asignará
                </span>

                <strong>
                  {{ slaPreview }}
                </strong>

              </div>

              <div class="field full-width">

                <label>
                  Criterio técnico
                </label>

                <textarea
                  v-model="
                    formClasificacion.criterio_tecnico
                  "
                  placeholder="Explique el criterio utilizado para clasificar la prioridad..."
                ></textarea>

              </div>

            </div>

            <button
              class="primary-action"
              type="button"
              :disabled="
                procesando
                || !formClasificacion.prioridad
                || !formClasificacion.criterio_tecnico.trim()
              "
              @click="clasificarTicket"
            >
              {{
                procesando
                  ? 'Procesando...'
                  : 'Clasificar prioridad y asignar SLA'
              }}
            </button>

          </div>


          <!-- =================================================
               EN ANÁLISIS: DESIGNAR
          ================================================== -->

          <div
            v-else-if="
              estadoActual === 'EN_ANALISIS'
              && ticketSeleccionado.prioridad
              && !ticketSeleccionado.tecnico_asignado
            "
            class="action-card"
          >

            <div class="action-title">

              <div>
                <span class="step-number">
                  3
                </span>

                <div>
                  <h3>
                    Designar revisión al equipo de especialistas
                  </h3>

                  <p>
                    Seleccione al especialista responsable que
                    realizará la revisión técnica.
                  </p>
                </div>
              </div>

            </div>

            <div class="field">

              <label>
                Especialista responsable
              </label>

              <select
                v-model="formAsignacion.tecnico_id"
              >
                <option value="">
                  Seleccione un especialista
                </option>

                <option
                  v-for="usuario in especialistas"
                  :key="usuario.id"
                  :value="usuario.id"
                >
                  {{
                    usuario.nombre_completo
                    || usuario.email
                  }}
                </option>
              </select>

              <small
                v-if="especialistas.length === 0"
              >
                No hay usuarios activos con rol ESPECIALISTA.
                Debe asignar ese rol desde Gestión de Usuarios.
              </small>

            </div>

            <button
              class="primary-action"
              type="button"
              :disabled="
                procesando
                || !formAsignacion.tecnico_id
              "
              @click="designarEspecialista"
            >
              {{
                procesando
                  ? 'Procesando...'
                  : 'Designar especialista'
              }}
            </button>

          </div>


          <!-- =================================================
               ASIGNADO
          ================================================== -->

          <div
            v-else-if="estadoActual === 'ASIGNADO'"
            class="action-card"
          >

            <div class="action-title">

              <div>
                <span class="step-number">
                  4
                </span>

                <div>
                  <h3>
                    Realizar inspección técnica y diagnóstico
                  </h3>

                  <p>
                    Registre el diagnóstico obtenido y el plan
                    de solución propuesto.
                  </p>
                </div>
              </div>

            </div>

            <div class="field">

              <label>
                Diagnóstico
              </label>

              <textarea
                v-model="
                  formDiagnostico.diagnostico
                "
                placeholder="Describa el resultado de la inspección técnica..."
              ></textarea>

            </div>

            <div class="field">

              <label>
                Plan de solución
              </label>

              <textarea
                v-model="
                  formDiagnostico.plan_solucion
                "
                placeholder="Describa las acciones que se realizarán..."
              ></textarea>

            </div>

            <button
              class="primary-action"
              type="button"
              :disabled="
                procesando
                || !formDiagnostico.diagnostico.trim()
                || !formDiagnostico.plan_solucion.trim()
              "
              @click="registrarDiagnostico"
            >
              {{
                procesando
                  ? 'Procesando...'
                  : 'Registrar inspección y diagnóstico'
              }}
            </button>

          </div>


          <!-- =================================================
               EN EJECUCIÓN: INTERVENCIÓN
          ================================================== -->

          <div
            v-else-if="
              estadoActual === 'EN_EJECUCION'
              && !ticketSeleccionado.solucion
            "
            class="action-card"
          >

            <div class="action-title">

              <div>
                <span class="step-number">
                  5
                </span>

                <div>
                  <h3>
                    Realizar reparación o instalación y registrar
                  </h3>

                  <p>
                    Registre el trabajo técnico realizado
                    sobre el equipo o servicio.
                  </p>
                </div>
              </div>

            </div>

            <div class="field">

              <label>
                Intervención realizada
              </label>

              <textarea
                v-model="
                  formIntervencion.solucion
                "
                placeholder="Describa la reparación, instalación o configuración realizada..."
              ></textarea>

            </div>

            <button
              class="primary-action"
              type="button"
              :disabled="
                procesando
                || !formIntervencion.solucion.trim()
              "
              @click="registrarIntervencion"
            >
              {{
                procesando
                  ? 'Procesando...'
                  : 'Registrar intervención técnica'
              }}
            </button>

          </div>


          <!-- =================================================
               EN EJECUCIÓN: PRUEBAS
          ================================================== -->

          <div
            v-else-if="
              estadoActual === 'EN_EJECUCION'
              && ticketSeleccionado.solucion
              && !ticketSeleccionado.resultado_pruebas
            "
            class="action-card"
          >

            <div class="action-title">

              <div>
                <span class="step-number">
                  6
                </span>

                <div>
                  <h3>
                    Realizar pruebas técnicas
                  </h3>

                  <p>
                    Verifique técnicamente el resultado
                    de la intervención.
                  </p>
                </div>
              </div>

            </div>

            <div class="field">

              <label>
                Resultado de las pruebas
              </label>

              <textarea
                v-model="
                  formPruebas.resultado_pruebas
                "
                placeholder="Describa las pruebas realizadas y sus resultados..."
              ></textarea>

            </div>

            <div class="field">

              <label>
                Informe técnico a la jefatura
              </label>

              <textarea
                v-model="
                  formPruebas.informe_tecnico
                "
                placeholder="Descargo técnico del trabajo realizado..."
              ></textarea>

            </div>

            <button
              class="primary-action"
              type="button"
              :disabled="
                procesando
                || !formPruebas.resultado_pruebas.trim()
              "
              @click="registrarPruebas"
            >
              {{
                procesando
                  ? 'Procesando...'
                  : 'Registrar pruebas técnicas'
              }}
            </button>

          </div>


          <!-- =================================================
               VERIFICACIÓN
          ================================================== -->

          <div
            v-else-if="
              estadoActual === 'EN_VERIFICACION'
            "
            class="action-card"
          >

            <div class="action-title">

              <div>
                <span class="step-number">
                  7
                </span>

                <div>
                  <h3>
                    Verificar funcionamiento
                  </h3>

                  <p>
                    Registre el resultado de la verificación
                    del trabajo realizado.
                  </p>
                </div>
              </div>

            </div>

            <div class="verification-options">

              <label
                :class="{
                  selected:
                    formVerificacion.funciona_correctamente
                    === true
                }"
              >

                <input
                  v-model="
                    formVerificacion.funciona_correctamente
                  "
                  type="radio"
                  :value="true"
                />

                <strong>
                  Funcionamiento correcto
                </strong>

                <span>
                  El requerimiento pasa a conformidad.
                </span>

              </label>

              <label
                :class="{
                  selected:
                    formVerificacion.funciona_correctamente
                    === false
                }"
              >

                <input
                  v-model="
                    formVerificacion.funciona_correctamente
                  "
                  type="radio"
                  :value="false"
                />

                <strong>
                  Requiere nueva intervención
                </strong>

                <span>
                  El ticket vuelve a ejecución técnica.
                </span>

              </label>

            </div>

            <button
              class="primary-action"
              type="button"
              :disabled="
                procesando
                || formVerificacion.funciona_correctamente
                   === null
              "
              @click="verificarFuncionamiento"
            >
              {{
                procesando
                  ? 'Procesando...'
                  : 'Registrar verificación'
              }}
            </button>

          </div>


          <!-- =================================================
               PENDIENTE CONFORMIDAD
          ================================================== -->

          <div
            v-else-if="
              estadoActual === 'PENDIENTE_CONFORMIDAD'
            "
            class="waiting-card"
          >

            <div class="waiting-icon">
              ✓
            </div>

            <div>
              <h3>
                Pendiente de conformidad del solicitante
              </h3>

              <p>
                El funcionamiento ya fue verificado.
                El solicitante debe informar si está conforme
                con el servicio recibido.
              </p>
            </div>

          </div>


          <!-- =================================================
               CERRADO
          ================================================== -->

          <div
            v-else-if="estadoActual === 'CERRADO'"
            class="complete-card"
          >

            <div class="complete-icon">
              ✓
            </div>

            <div>

              <h3>
                Ticket cerrado
              </h3>

              <p>
                El solicitante informó conformidad y
                el proceso concluyó.
              </p>

              <span
                v-if="
                  ticketSeleccionado.sla_cumplido === true
                "
                class="sla-result success"
              >
                SLA cumplido
              </span>

              <span
                v-else-if="
                  ticketSeleccionado.sla_cumplido === false
                "
                class="sla-result danger"
              >
                SLA incumplido
              </span>

            </div>

          </div>


          <!-- =================================================
               ANULADO
          ================================================== -->

          <div
            v-else-if="estadoActual === 'ANULADO'"
            class="cancelled-card"
          >
            Este ticket fue anulado por el solicitante.
          </div>


          <div
            v-else
            class="waiting-card"
          >

            <div>
              <h3>
                Estado sin acción disponible
              </h3>

              <p>
                Estado actual:
                {{
                  ticketSeleccionado.estado_nombre
                  || ticketSeleccionado.estado_codigo
                }}
              </p>
            </div>

          </div>

        </section>


        <!-- =================================================
             PIE
        ================================================== -->

        <footer class="modal-footer">

          <button
            class="secondary-button"
            type="button"
            @click="cerrarTicket"
          >
            Cerrar
          </button>

        </footer>

      </section>

    </div>

  </div>
</template>


<script setup>
import DocumentosExpediente from '../components/DocumentosExpediente.vue'
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

import AdminMenu
  from '../components/AdminMenu.vue'


const router = useRouter()


// ==========================================================
// DATOS
// ==========================================================

const tickets = ref([])

const usuarios = ref([])

const ticketSeleccionado = ref(null)

const cargando = ref(true)

const procesando = ref(false)

const mensaje = ref('')

const mensajeError = ref(false)


// ==========================================================
// FORMULARIOS
// ==========================================================

const formClasificacion = reactive({
  prioridad: '',
  criterio_tecnico: '',
})

const formAsignacion = reactive({
  tecnico_id: '',
})

const formDiagnostico = reactive({
  diagnostico: '',
  plan_solucion: '',
})

const formIntervencion = reactive({
  solucion: '',
})

const formPruebas = reactive({
  resultado_pruebas: '',
  informe_tecnico: '',
})

const formVerificacion = reactive({
  funciona_correctamente: null,
})


// ==========================================================
// COLUMNAS
// ==========================================================

const informesRecibidos = computed(() =>
  tickets.value
    .filter(t => t.informe_elevado_en && t.informe_final)
    .sort((a, b) => new Date(b.informe_elevado_en) - new Date(a.informe_elevado_en))
)

async function acusarInforme(ticket) {
  try {
    const r = await fetch(`/api/soporte/tickets/${ticket.id}/recibir-informe/`, {
      method: 'POST',
      headers: {
        Authorization: `Token ${localStorage.getItem('sigta_token')}`,
        'Content-Type': 'application/json',
      },
      body: '{}',
    })
    const d = await r.json().catch(() => ({}))
    if (!r.ok) throw new Error(d.detalle || 'No fue posible registrar la recepción.')
    await cargarTickets()
    alert(d.mensaje || 'Informe recibido.')
  } catch (e) {
    alert(e.message)
  }
}

function fechaInforme(valor) {
  return valor
    ? new Date(valor).toLocaleDateString('es-BO', { day: '2-digit', month: 'long', year: 'numeric' })
    : ''
}

const columnas = [

  {
    codigo: 'NUEVO',
    nombre: 'Nuevo',
    descripcion: 'Pendiente de validación',
  },

  {
    codigo: 'EN_ANALISIS',
    nombre: 'En análisis',
    descripcion: 'Clasificación UTIC',
  },

  {
    codigo: 'ASIGNADO',
    nombre: 'Asignado',
    descripcion: 'Especialista designado',
  },

  {
    codigo: 'EN_EJECUCION',
    nombre: 'En ejecución',
    descripcion: 'Trabajo técnico',
  },

  {
    codigo: 'EN_VERIFICACION',
    nombre: 'En verificación',
    descripcion: 'Pruebas y validación',
  },

  {
    codigo: 'PENDIENTE_CONFORMIDAD',
    nombre: 'Pendiente conformidad',
    descripcion: 'Espera al solicitante',
  },

  {
    codigo: 'CERRADO',
    nombre: 'Cerrado',
    descripcion: 'Proceso finalizado',
  },
]


// ==========================================================
// TOKEN
// ==========================================================

function token() {
  return localStorage.getItem(
    'sigta_token'
  )
}


function headersJson() {

  return {
    Authorization:
      `Token ${token()}`,

    Accept:
      'application/json',

    'Content-Type':
      'application/json',
  }
}


// ==========================================================
// INICIO
// ==========================================================

onMounted(
  async () => {

    if (!token()) {

      router.push(
        '/login'
      )

      return
    }

    await cargarTodo()
  }
)


// ==========================================================
// CARGAR TODO
// ==========================================================

async function cargarTodo() {

  cargando.value = true

  try {

    await Promise.all([
      cargarTickets(),
      cargarUsuarios(),
    ])

  } finally {

    cargando.value = false
  }
}


// ==========================================================
// NORMALIZAR LISTA
// ==========================================================

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


// ==========================================================
// CARGAR TICKETS
// ==========================================================

async function cargarTickets() {

  try {

    const respuesta =
      await fetch(
        '/api/soporte/tickets/',
        {
          headers: {
            Authorization:
              `Token ${token()}`,

            Accept:
              'application/json',
          }
        }
      )


    if (
      respuesta.status === 401
      || respuesta.status === 403
    ) {

      cerrarSesion()
      return
    }


    if (!respuesta.ok) {

      throw new Error(
        'No fue posible cargar los tickets.'
      )
    }


    tickets.value =
      normalizarLista(
        await respuesta.json()
      )


  } catch (error) {

    console.error(
      error
    )


    mostrarMensaje(
      'No fue posible cargar los tickets de soporte.',
      true
    )
  }
}


// ==========================================================
// CARGAR USUARIOS
// ==========================================================

async function cargarUsuarios() {

  try {

    const respuesta =
      await fetch(
        '/api/usuarios/usuarios/',
        {
          headers: {
            Authorization:
              `Token ${token()}`,

            Accept:
              'application/json',
          }
        }
      )


    if (!respuesta.ok) {

      console.error(
        'No fue posible cargar usuarios:',
        respuesta.status
      )

      return
    }


    usuarios.value =
      normalizarLista(
        await respuesta.json()
      )


  } catch (error) {

    console.error(
      'No fue posible cargar usuarios:',
      error
    )
  }
}


// ==========================================================
// ESPECIALISTAS
// ==========================================================
//
// IMPORTANTE:
//
// usuarios/serializers.py devuelve:
//
// roles: [
//   {
//     rol_id,
//     rol_codigo,
//     rol_nombre,
//     area_id,
//     area_codigo,
//     area_nombre
//   }
// ]
//
// Por eso buscamos rol_codigo.
//
// ==========================================================

const especialistas =
  computed(() => {

    return usuarios.value.filter(
      usuario => {

        // Usuario inactivo
        if (
          usuario.is_active === false
        ) {
          return false
        }


        // Debe tener roles
        if (
          !Array.isArray(
            usuario.roles
          )
        ) {
          return false
        }


        return usuario.roles.some(
          asignacion => {

            const codigo =
              String(
                asignacion?.rol_codigo
                || ''
              )
                .trim()
                .toUpperCase()


            return [
              'ESPECIALISTA',
              'AGENTE'
            ].includes(
              codigo
            )
          }
        )
      }
    )
  })


// ==========================================================
// ESTADO
// ==========================================================

function estadoTicket(
  ticket
) {

  return String(
    ticket?.estado_codigo
    || ''
  )
    .trim()
    .toUpperCase()
    .replace(
      /\s+/g,
      '_'
    )
}


const estadoActual =
  computed(() => {

    return estadoTicket(
      ticketSeleccionado.value
    )
  })


// ==========================================================
// KANBAN
// ==========================================================

function ticketsPorColumna(
  columna
) {

  return tickets.value.filter(
    ticket =>
      estadoTicket(ticket)
      ===
      columna.codigo
  )
}


function contar(
  codigo
) {

  return tickets.value.filter(
    ticket =>
      estadoTicket(ticket)
      ===
      codigo
  ).length
}


const enProceso =
  computed(() => {

    const estados = [
      'EN_ANALISIS',
      'ASIGNADO',
      'EN_EJECUCION',
      'EN_VERIFICACION',
      'PENDIENTE_CONFORMIDAD',
    ]


    return tickets.value.filter(
      ticket =>
        estados.includes(
          estadoTicket(ticket)
        )
    ).length
  })


// ==========================================================
// ABRIR TICKET
// ==========================================================

function abrirTicket(
  ticket
) {

  ticketSeleccionado.value = {
    ...ticket
  }

  reiniciarFormularios()
}


function cerrarTicket() {

  ticketSeleccionado.value = null
}


// ==========================================================
// REINICIAR FORMULARIOS
// ==========================================================

function reiniciarFormularios() {

  Object.assign(
    formClasificacion,
    {
      prioridad: '',
      criterio_tecnico: '',
    }
  )


  Object.assign(
    formAsignacion,
    {
      tecnico_id: '',
    }
  )


  Object.assign(
    formDiagnostico,
    {
      diagnostico: '',
      plan_solucion: '',
    }
  )


  Object.assign(
    formIntervencion,
    {
      solucion: '',
    }
  )


  Object.assign(
    formPruebas,
    {
      resultado_pruebas: '',
    }
  )


  formVerificacion
    .funciona_correctamente = null
}


// ==========================================================
// SLA PREVIEW
// ==========================================================

const slaPreview =
  computed(() => {

    const valores = {
      CRITICA: '4 horas',
      ALTA: '8 horas',
      MEDIA: '24 horas',
      BAJA: '48 horas',
    }


    return (
      valores[
        formClasificacion.prioridad
      ]
      ||
      'Seleccione una prioridad'
    )
  })


// ==========================================================
// EJECUTAR ACCIÓN
// ==========================================================

async function ejecutarAccion(
  endpoint,
  body = {}
) {

  if (
    !ticketSeleccionado.value
  ) {
    return null
  }


  procesando.value = true


  try {

    const respuesta =
      await fetch(
        `/api/soporte/tickets/${ticketSeleccionado.value.id}/${endpoint}/`,
        {
          method:
            'POST',

          headers:
            headersJson(),

          body:
            JSON.stringify(
              body
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
      datos.mensaje
      ||
      'Acción realizada correctamente.'
    )


    await cargarTickets()


    const actualizado =
      tickets.value.find(
        ticket =>
          Number(ticket.id)
          ===
          Number(
            ticketSeleccionado
              .value
              .id
          )
      )


    if (
      actualizado
    ) {

      ticketSeleccionado.value = {
        ...actualizado
      }
    }


    return datos


  } catch (error) {

    console.error(
      error
    )


    mostrarMensaje(
      error.message
      ||
      'No fue posible realizar la acción.',
      true
    )


    return null


  } finally {

    procesando.value = false
  }
}


// ==========================================================
// 1. VALIDAR
// ==========================================================

async function validarTicket() {

  await ejecutarAccion(
    'validar-ticket'
  )
}


// ==========================================================
// 2. CLASIFICAR
// ==========================================================

async function clasificarTicket() {

  await ejecutarAccion(
    'clasificar-prioridad',
    {
      prioridad:
        formClasificacion.prioridad,

      criterio_tecnico:
        formClasificacion
          .criterio_tecnico
          .trim(),
    }
  )
}


// ==========================================================
// 3. DESIGNAR
// ==========================================================

async function designarEspecialista() {

  await ejecutarAccion(
    'designar-revision',
    {
      tecnico_id:
        Number(
          formAsignacion.tecnico_id
        ),

      especialistas_apoyo: [],
    }
  )
}


// ==========================================================
// 4. DIAGNÓSTICO
// ==========================================================

async function registrarDiagnostico() {

  await ejecutarAccion(
    'registrar-diagnostico',
    {
      diagnostico:
        formDiagnostico
          .diagnostico
          .trim(),

      plan_solucion:
        formDiagnostico
          .plan_solucion
          .trim(),
    }
  )
}


// ==========================================================
// 5. INTERVENCIÓN
// ==========================================================

async function registrarIntervencion() {

  await ejecutarAccion(
    'registrar-intervencion',
    {
      solucion:
        formIntervencion
          .solucion
          .trim(),
    }
  )
}


// ==========================================================
// 6. PRUEBAS
// ==========================================================

async function registrarPruebas() {

  await ejecutarAccion(
    'pruebas-tecnicas',
    {
      resultado_pruebas:
        formPruebas
          .resultado_pruebas
          .trim(),

      informe_tecnico:
        formPruebas
          .informe_tecnico
          .trim(),
    }
  )
}


// ==========================================================
// 7. VERIFICACIÓN
// ==========================================================

async function verificarFuncionamiento() {

  await ejecutarAccion(
    'verificar-funcionamiento',
    {
      funciona_correctamente:
        formVerificacion
          .funciona_correctamente,
    }
  )
}


// ==========================================================
// PRIORIDAD
// ==========================================================

function textoPrioridad(
  prioridad
) {

  const valor =
    String(
      prioridad
      || ''
    )
      .trim()
      .toUpperCase()


  const nombres = {
    BAJA: 'Baja',
    MEDIA: 'Media',
    ALTA: 'Alta',
    CRITICA: 'Crítica',
  }


  return (
    nombres[valor]
    ||
    'Sin clasificar'
  )
}


function clasePrioridad(
  prioridad
) {

  const valor =
    String(
      prioridad
      || ''
    )
      .trim()
      .toUpperCase()


  const clases = {
    BAJA: 'low',
    MEDIA: 'medium',
    ALTA: 'high',
    CRITICA: 'critical',
  }


  return (
    clases[valor]
    ||
    'unclassified'
  )
}


// ==========================================================
// SLA
// ==========================================================

function textoEstadoSla(
  estado
) {

  const estados = {
    SIN_SLA: 'Sin SLA',
    EN_TIEMPO: 'En tiempo',
    EN_RIESGO: 'En riesgo',
    VENCIDO: 'Vencido',
    CUMPLIDO: 'Cumplido',
    INCUMPLIDO: 'Incumplido',
  }


  return (
    estados[estado]
    ||
    estado
    ||
    'Sin SLA'
  )
}


function claseSla(
  estado
) {

  const clases = {
    EN_TIEMPO: 'sla-ok',
    EN_RIESGO: 'sla-risk',
    VENCIDO: 'sla-danger',
    CUMPLIDO: 'sla-ok',
    INCUMPLIDO: 'sla-danger',
  }


  return (
    clases[estado]
    ||
    'sla-neutral'
  )
}


function textoSla(
  ticket
) {

  if (
    !ticket.sla_horas
  ) {

    return 'Sin SLA'
  }


  return (
    `SLA ${ticket.sla_horas} h · `
    +
    textoEstadoSla(
      ticket.sla_estado
    )
  )
}


// ==========================================================
// FECHA
// ==========================================================

function formatearFecha(
  fecha
) {

  if (!fecha) {
    return '-'
  }


  try {

    return new Intl.DateTimeFormat(
      'es-BO',
      {
        dateStyle: 'short',
        timeStyle: 'short',
      }
    ).format(
      new Date(fecha)
    )

  } catch {

    return fecha
  }
}


// ==========================================================
// ERROR
// ==========================================================

function obtenerError(
  datos
) {

  if (
    datos?.detalle
  ) {
    return datos.detalle
  }


  if (
    datos?.detail
  ) {
    return datos.detail
  }


  const entrada =
    Object.entries(
      datos
      || {}
    )[0]


  if (
    !entrada
  ) {

    return (
      'Revise la información ingresada.'
    )
  }


  const [
    campo,
    valor
  ] = entrada


  return (
    `${campo}: ${
      Array.isArray(valor)
        ? valor.join(', ')
        : String(valor)
    }`
  )
}


// ==========================================================
// MENSAJE
// ==========================================================

function mostrarMensaje(
  texto,
  error = false
) {

  mensaje.value = texto

  mensajeError.value = error


  setTimeout(
    () => {

      mensaje.value = ''

    },
    5000
  )
}


// ==========================================================
// SESIÓN
// ==========================================================

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

.breadcrumb {
  display: block;
  margin-bottom: 6px;
  color: var(--sigta-texto-suave);
  font-size: 9px;
}

.page-header h1 {
  margin: 0;
  color: var(--sigta-texto);
  font-size: 27px;
}

.page-header p {
  margin: 5px 0 0;
  color: var(--sigta-texto-suave);
  font-size: 11px;
}

.secondary-main-button {
  min-height: 39px;
  padding: 0 15px;
  border: 1px solid var(--sigta-azul);
  border-radius: 7px;
  background: white;
  color: var(--sigta-azul);
  font-size: 9px;
  font-weight: 800;
  cursor: pointer;
}


/* =========================================================
   MÉTRICAS
========================================================= */

.metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 13px;
  margin-bottom: 17px;
}

.metrics article {
  min-height: 105px;
  padding: 17px;
  background: white;
  border-top: 4px solid var(--sigta-mostaza);
  border-radius: 9px;
  box-shadow: 0 3px 12px rgba(0,0,0,.05);
}

.metrics span,
.metrics small {
  display: block;
  color: var(--sigta-texto-suave);
}

.metrics span {
  font-size: 8px;
  font-weight: 800;
  text-transform: uppercase;
}

.metrics strong {
  display: block;
  margin: 7px 0 4px;
  color: var(--sigta-azul);
  font-size: 26px;
}

.metrics small {
  font-size: 8px;
}


/* =========================================================
   MENSAJE
========================================================= */

.message {
  margin-bottom: 15px;
  padding: 11px 13px;
  border-radius: 7px;
  font-size: 9px;
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
   PROCESO
========================================================= */

.process-info {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  margin-bottom: 17px;
  padding: 15px 17px;
  background: white;
  border-left: 4px solid var(--sigta-mostaza);
  border-radius: 8px;
}

.section-label {
  display: block;
  margin-bottom: 4px;
  color: var(--sigta-azul);
  font-size: 7px;
  font-weight: 900;
  letter-spacing: .8px;
}

.process-info strong {
  color: var(--sigta-texto);
  font-size: 11px;
}

.process-info p {
  margin: 4px 0 0;
  color: var(--sigta-texto-suave);
  font-size: 8px;
}

.process-steps {
  display: flex;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 5px;
}

.process-steps span {
  padding: 5px 7px;
  border-radius: 5px;
  background: var(--sigta-azul-tenue);
  color: var(--sigta-texto-suave);
  font-size: 7px;
}


/* =========================================================
   KANBAN
========================================================= */

.kanban-section {
  min-width: 0;
  padding: 17px;
  background: white;
  border-radius: 9px;
  box-shadow: 0 4px 14px rgba(0,0,0,.05);
}

.kanban-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 13px;
}

.kanban-title-row h2 {
  margin: 0;
  color: var(--sigta-texto);
  font-size: 16px;
}

.refresh-button {
  min-height: 33px;
  padding: 0 11px;
  border: 1px solid var(--sigta-borde);
  border-radius: 6px;
  background: white;
  color: var(--sigta-texto-suave);
  font-size: 8px;
  font-weight: 700;
  cursor: pointer;
}

.refresh-button:disabled {
  opacity: .6;
  cursor: not-allowed;
}

.kanban-wrapper {
  width: 100%;
  max-width: 100%;
  overflow-x: auto;
  overflow-y: hidden;
  padding-bottom: 12px;
}

.kanban-wrapper::-webkit-scrollbar {
  height: 11px;
}

.kanban-wrapper::-webkit-scrollbar-track {
  background: var(--sigta-azul-texto-claro);
  border-radius: 10px;
}

.kanban-wrapper::-webkit-scrollbar-thumb {
  background: var(--sigta-texto-suave);
  border-radius: 10px;
}

.kanban {
  width: max-content;
  min-width: max-content;
  display: flex;
  gap: 10px;
}

.column {
  width: var(--sigta-sidebar);
  min-width: var(--sigta-sidebar);
  flex-shrink: 0;
}

.column-header {
  min-height: 57px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 9px 10px;
  background: var(--sigta-azul-texto-claro);
  border-radius: 7px 7px 0 0;
}

.column-header strong {
  display: block;
  color: var(--sigta-azul);
  font-size: 10px;
}

.column-header small {
  display: block;
  margin-top: 3px;
  color: var(--sigta-texto-suave);
  font-size: 7px;
}

.column-header > span {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--sigta-azul);
  color: white;
  font-size: 8px;
  font-weight: 900;
}

.column-body {
  min-height: 470px;
  padding: 8px;
  background: var(--sigta-azul-tenue);
  border-radius: 0 0 7px 7px;
}


/* =========================================================
   TICKET
========================================================= */

.ticket-card {
  margin-bottom: 8px;
  padding: 10px;
  background: white;
  border-left: 3px solid var(--sigta-texto-suave);
  border-radius: 7px;
  box-shadow: 0 2px 7px rgba(0,0,0,.06);
  cursor: pointer;
}

.ticket-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 5px;
  color: var(--sigta-azul);
  font-size: 8px;
}

.ticket-card h3 {
  margin: 7px 0;
  color: var(--sigta-azul);
  font-size: 10px;
  line-height: 1.4;
}

.category {
  display: inline-block;
  margin-bottom: 8px;
  padding: 4px 6px;
  border-radius: 4px;
  background: var(--sigta-azul-tenue);
  color: var(--sigta-texto-suave);
  font-size: 7px;
}

.ticket-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.ticket-info span {
  display: block;
  color: var(--sigta-texto-suave);
  font-size: 6px;
}

.ticket-info strong {
  color: var(--sigta-texto-suave);
  font-size: 7px;
}

.ticket-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 7px;
  margin-top: 9px;
  padding-top: 8px;
  border-top: 1px solid var(--sigta-azul-tenue);
}

.ticket-footer span,
.ticket-footer strong {
  display: block;
}

.ticket-footer span {
  color: var(--sigta-texto-suave);
  font-size: 6px;
}

.ticket-footer strong {
  max-width: 120px;
  overflow: hidden;
  color: var(--sigta-texto-suave);
  font-size: 7px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.ticket-footer button {
  border: none;
  border-radius: 5px;
  padding: 5px 7px;
  background: var(--sigta-azul-tenue);
  color: var(--sigta-azul);
  font-size: 7px;
  cursor: pointer;
}


/* =========================================================
   PRIORIDAD
========================================================= */

.priority {
  padding: 3px 5px;
  border-radius: 4px;
  font-size: 6px;
  font-weight: 800;
}

.priority.unclassified {
  background: var(--sigta-azul-tenue);
  color: var(--sigta-texto-suave);
}

.priority.low {
  background: var(--sigta-exito-fondo);
  color: var(--sigta-exito);
}

.priority.medium {
  background: var(--sigta-mostaza-suave);
  color: var(--sigta-mostaza-oscuro);
}

.priority.high {
  background: var(--sigta-mostaza-suave);
  color: var(--sigta-mostaza);
}

.priority.critical {
  background: var(--sigta-error-fondo);
  color: var(--sigta-error);
}


/* =========================================================
   SLA
========================================================= */

.sla-badge {
  display: inline-block;
  margin-top: 7px;
  padding: 4px 6px;
  border-radius: 4px;
  font-size: 6px;
  font-weight: 800;
}

.sla-neutral {
  background: var(--sigta-azul-tenue);
  color: var(--sigta-texto-suave);
}

.sla-ok {
  background: var(--sigta-exito-fondo);
  color: var(--sigta-exito);
}

.sla-risk {
  background: var(--sigta-mostaza-suave);
  color: var(--sigta-mostaza-oscuro);
}

.sla-danger {
  background: var(--sigta-error-fondo);
  color: var(--sigta-error);
}


/* =========================================================
   MODAL
========================================================= */

.overlay {
  position: fixed;
  inset: 0;
  z-index: 1200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 18px;
  background: rgba(5,31,53,.68);
}

.ticket-modal {
  width: 900px;
  max-width: 100%;
  max-height: 94vh;
  overflow-y: auto;
  border-top: 4px solid var(--sigta-mostaza);
  border-radius: 11px;
  background: white;
  box-shadow: 0 20px 60px rgba(0,0,0,.28);
}

.modal-header {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  padding: 20px 22px;
  border-bottom: 1px solid var(--sigta-borde);
}

.modal-code {
  color: var(--sigta-azul);
  font-size: 8px;
  font-weight: 900;
}

.modal-header h2 {
  margin: 5px 0 0;
  color: var(--sigta-texto);
  font-size: 19px;
}

.modal-header p {
  margin: 4px 0 0;
  color: var(--sigta-texto-suave);
  font-size: 8px;
}

.close-button {
  border: none;
  background: transparent;
  color: var(--sigta-texto-suave);
  font-size: 25px;
  cursor: pointer;
}


/* =========================================================
   STATUS
========================================================= */

.status-grid {
  display: grid;
  grid-template-columns: repeat(4,1fr);
  gap: 8px;
  padding: 13px 22px;
  background: var(--sigta-azul-tenue);
}

.status-grid article {
  padding: 8px;
  border-radius: 6px;
  background: white;
}

.status-grid span,
.status-grid strong {
  display: block;
}

.status-grid span {
  color: var(--sigta-texto-suave);
  font-size: 7px;
}

.status-grid strong {
  margin-top: 4px;
  color: var(--sigta-azul);
  font-size: 9px;
}


/* =========================================================
   SECCIONES
========================================================= */

.modal-section {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 17px 22px;
  border-bottom: 1px solid var(--sigta-azul-tenue);
}

.section-number,
.step-number {
  width: 25px;
  height: 25px;
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--sigta-azul);
  color: white;
  font-size: 8px;
  font-weight: 900;
}

.section-content {
  flex: 1;
  min-width: 0;
}

.section-content h3 {
  margin: 3px 0 11px;
  color: var(--sigta-texto);
  font-size: 11px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2,1fr);
  gap: 9px;
}

.detail-grid > div {
  padding: 9px;
  border-radius: 6px;
  background: var(--sigta-azul-tenue);
}

.detail-grid .full-width {
  grid-column: 1 / -1;
}

.detail-grid span,
.detail-grid strong {
  display: block;
}

.detail-grid span {
  color: var(--sigta-texto-suave);
  font-size: 7px;
}

.detail-grid strong {
  margin-top: 4px;
  color: var(--sigta-texto-suave);
  font-size: 9px;
}

.description-box,
.text-block {
  padding: 10px;
  border-radius: 6px;
  background: var(--sigta-azul-tenue);
  color: var(--sigta-texto-suave);
  font-size: 9px;
  line-height: 1.55;
}

.text-block {
  margin-bottom: 8px;
}

.text-block span {
  color: var(--sigta-texto-suave);
  font-size: 7px;
}

.text-block p {
  margin: 4px 0 0;
}


/* =========================================================
   EVIDENCIA
========================================================= */

.evidence-box {
  padding: 11px;
  border: 1px dashed var(--sigta-texto-suave);
  border-radius: 7px;
  background: var(--sigta-azul-tenue);
}

.evidence-box p {
  margin: 0 0 8px;
  color: var(--sigta-texto-suave);
  font-size: 8px;
}

.evidence-box a {
  color: var(--sigta-azul);
  font-size: 8px;
  font-weight: 800;
  text-decoration: none;
}

.empty-evidence {
  padding: 10px;
  border-radius: 6px;
  background: var(--sigta-azul-tenue);
  color: var(--sigta-texto-suave);
  font-size: 8px;
}


/* =========================================================
   WORKFLOW
========================================================= */

.workflow-section {
  padding: 19px 22px;
  background: var(--sigta-azul-tenue);
}

.action-card {
  margin-top: 8px;
  padding: 15px;
  border: 1px solid var(--sigta-azul-texto-claro);
  border-radius: 8px;
  background: white;
}

.action-title > div {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}

.action-title h3 {
  margin: 2px 0 3px;
  color: var(--sigta-texto);
  font-size: 11px;
}

.action-title p {
  margin: 0;
  color: var(--sigta-texto-suave);
  font-size: 8px;
  line-height: 1.45;
}

.validation-list {
  display: grid;
  grid-template-columns: repeat(2,1fr);
  gap: 6px;
  margin: 13px 0;
  padding: 11px;
  border-radius: 6px;
  background: var(--sigta-azul-tenue);
}

.validation-list span {
  color: var(--sigta-texto-suave);
  font-size: 8px;
}


/* =========================================================
   FORMULARIOS
========================================================= */

.form-grid {
  display: grid;
  grid-template-columns: 1fr 220px;
  gap: 10px;
  margin-top: 13px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 5px;
  margin-top: 12px;
}

.field label {
  color: var(--sigta-azul);
  font-size: 8px;
  font-weight: 800;
}

.field input,
.field select,
.field textarea {
  width: 100%;
  padding: 9px 10px;
  border: 1px solid var(--sigta-borde);
  border-radius: 6px;
  background: white;
  color: var(--sigta-azul);
  font-family: inherit;
  font-size: 9px;
  outline: none;
}

.field textarea {
  min-height: 85px;
  resize: vertical;
}

.field small {
  color: var(--sigta-texto-suave);
  font-size: 7px;
}

.full-width {
  grid-column: 1 / -1;
}

.sla-preview {
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 11px;
  border-radius: 7px;
  background: var(--sigta-azul-tenue);
}

.sla-preview span {
  color: var(--sigta-texto-suave);
  font-size: 7px;
}

.sla-preview strong {
  margin-top: 5px;
  color: var(--sigta-azul);
  font-size: 13px;
}


/* =========================================================
   BOTÓN ACCIÓN
========================================================= */

.primary-action {
  min-height: 38px;
  margin-top: 14px;
  padding: 0 14px;
  border: none;
  border-radius: 6px;
  background: var(--sigta-azul);
  color: white;
  font-size: 8px;
  font-weight: 800;
  cursor: pointer;
}

.primary-action:disabled {
  opacity: .5;
  cursor: not-allowed;
}


/* =========================================================
   VERIFICACIÓN
========================================================= */

.verification-options {
  display: grid;
  grid-template-columns: repeat(2,1fr);
  gap: 9px;
  margin-top: 13px;
}

.verification-options label {
  padding: 12px;
  border: 1px solid var(--sigta-borde);
  border-radius: 7px;
  cursor: pointer;
}

.verification-options label.selected {
  border-color: var(--sigta-azul);
  background: var(--sigta-azul-tenue);
}

.verification-options strong,
.verification-options span {
  display: block;
  margin-left: 22px;
}

.verification-options strong {
  margin-top: -17px;
  color: var(--sigta-azul);
  font-size: 9px;
}

.verification-options span {
  margin-top: 4px;
  color: var(--sigta-texto-suave);
  font-size: 7px;
}


/* =========================================================
   ESPERA / COMPLETADO
========================================================= */

.waiting-card,
.complete-card {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-top: 10px;
  padding: 14px;
  border-radius: 8px;
}

.waiting-card {
  background: var(--sigta-mostaza-suave);
  border: 1px solid var(--sigta-mostaza-clara);
}

.complete-card {
  background: var(--sigta-exito-fondo);
  border: 1px solid var(--sigta-exito);
}

.waiting-icon,
.complete-icon {
  width: 33px;
  height: 33px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-weight: 900;
}

.waiting-icon {
  background: var(--sigta-mostaza);
  color: var(--sigta-texto);
}

.complete-icon {
  background: var(--sigta-exito);
  color: white;
}

.waiting-card h3,
.complete-card h3 {
  margin: 0;
  color: var(--sigta-azul);
  font-size: 10px;
}

.waiting-card p,
.complete-card p {
  margin: 4px 0 0;
  color: var(--sigta-texto-suave);
  font-size: 8px;
}

.sla-result {
  display: inline-block;
  margin-top: 7px;
  padding: 4px 7px;
  border-radius: 13px;
  font-size: 7px;
  font-weight: 800;
}

.sla-result.success {
  background: var(--sigta-exito-fondo);
  color: var(--sigta-exito);
}

.sla-result.danger {
  background: var(--sigta-error-fondo);
  color: var(--sigta-error);
}

.cancelled-card {
  margin-top: 10px;
  padding: 13px;
  border-radius: 7px;
  background: var(--sigta-error-fondo);
  color: var(--sigta-error);
  font-size: 8px;
}


/* =========================================================
   FOOTER
========================================================= */

.modal-footer {
  display: flex;
  justify-content: flex-end;
  padding: 14px 22px;
  border-top: 1px solid var(--sigta-azul-tenue);
}

.secondary-button {
  min-height: 35px;
  padding: 0 13px;
  border: 1px solid var(--sigta-borde);
  border-radius: 6px;
  background: white;
  color: var(--sigta-texto-suave);
  font-size: 8px;
  font-weight: 700;
  cursor: pointer;
}

.loading,
.empty-column {
  padding: 28px 8px;
  color: var(--sigta-texto-suave);
  text-align: center;
  font-size: 8px;
}


/* =========================================================
   RESPONSIVE
========================================================= */

@media (max-width: 1000px) {

  .metrics {
    grid-template-columns: repeat(2,1fr);
  }

  .process-info {
    align-items: flex-start;
    flex-direction: column;
  }

  .process-steps {
    justify-content: flex-start;
  }

  .status-grid {
    grid-template-columns: repeat(2,1fr);
  }
}


@media (max-width: 760px) {

  .admin-layout {
    display: block;
  }

  .main {
    padding: 16px;
  }

  .page-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .metrics,
  .status-grid,
  .detail-grid,
  .form-grid,
  .verification-options,
  .validation-list {
    grid-template-columns: 1fr;
  }

  .detail-grid .full-width,
  .full-width {
    grid-column: auto;
  }
}


.informes-direccion {
  margin-bottom: 22px;
  padding: 20px 24px;
  background: var(--sigta-superficie);
  border: 1px solid var(--sigta-borde);
  border-left: 4px solid var(--sigta-mostaza);
  border-radius: var(--sigta-radio);
}

.informes-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 14px;
}

.informes-head h2 {
  margin: 0 0 4px;
}

.informes-head p {
  margin: 0;
  color: var(--sigta-texto-suave);
  font-size: 12px;
}

.informes-total {
  min-width: 34px;
  padding: 5px 11px;
  border-radius: 14px;
  background: var(--sigta-mostaza);
  color: var(--sigta-texto);
  font-weight: 800;
  text-align: center;
}

.informe-item {
  padding: 13px 0;
  border-top: 1px solid var(--sigta-borde-suave);
}

.informe-cabecera {
  display: flex;
  align-items: baseline;
  gap: 10px;
  flex-wrap: wrap;
}

.informe-cabecera strong {
  color: var(--sigta-azul);
}

.informe-cabecera small {
  margin-left: auto;
  color: var(--sigta-texto-suave);
}

.informe-item p {
  margin: 7px 0 0;
  color: var(--sigta-texto-suave);
  font-size: 13px;
  line-height: 1.6;
}

.informe-acuse {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
  margin-top: 10px;
}

.acuse-estado {
  font-size: 12px;
  color: var(--sigta-texto-suave);
}

.acuse-listo {
  font-size: 12px;
  font-weight: 700;
  color: var(--sigta-exito);
}

.informe-acuse .primary-action {
  padding: 7px 14px;
  font-size: 12px;
}
</style>
