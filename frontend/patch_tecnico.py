import re
import sys

file_path = r"c:\Users\INTEL\Desktop\SIGTA - 5.0\Sigtap\frontend\src\views\AuxiliarServiciosGeneralesDashboardView.vue"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Reemplazar la sección de Ordenes de Trabajo
html_template = """      <!-- ==================== A. ÓRDENES DE TRABAJO (MASTER-DETAIL) ==================== -->
      <section v-else-if="vista==='ordenes'" class="gestion-tickets-layout">
        <div class="gestion-left">
          <div class="gestion-left-header">
            <h3>Órdenes de Trabajo</h3>
            <span class="badge">{{ porRecibir.length }} Pendientes</span>
          </div>
          <div class="gestion-lista">
            <article v-for="r in porRecibir" :key="r.id" :class="['ticket-item', ordenAbierta?.id === r.id ? 'activo' : '', 't-validar']" @click="recibirOrden(r)">
              <div class="top">
                <span>{{ r.codigo }}</span>
                <em class="e-validar">{{ r.prioridad_jefatura || r.estado_codigo }}</em>
              </div>
              <h4>{{ r.titulo }}</h4>
              <p>📍 {{ r.ubicacion || 's/d' }}</p>
            </article>
            <div v-if="!porRecibir.length" class="empty-list">Bandeja al día. No tiene órdenes pendientes.</div>
          </div>
        </div>

        <div class="gestion-right">
          <div v-if="!ordenAbierta" class="empty">
            <span>←</span>
            <h3>Seleccione una orden</h3>
            <p>Seleccione una orden de trabajo de la lista para registrar el diagnóstico.</p>
          </div>
          <div v-else class="gestion-detalle-wrapper">
            <div class="ticket-header-card">
              <div class="t-head">
                <h2>{{ ordenAbierta.titulo }}</h2>
                <span class="codigo-badge">{{ ordenAbierta.codigo }}</span>
              </div>
              <p class="t-meta"><b>Solicitante:</b> {{ ordenAbierta.solicitante_nombre }} • <b>Ubicación:</b> {{ ordenAbierta.ubicacion }}</p>
              <div class="desc-box">{{ ordenAbierta.descripcion }}</div>
              <a v-if="ordenAbierta.evidencia_archivo_url" class="adjunto mt-2 block" :href="ordenAbierta.evidencia_archivo_url" target="_blank">📎 Ver Evidencia Adjunta</a>
            </div>

            <div class="workflow-card">
              <div class="wf-header">Consola de Diagnóstico</div>
              <div class="wf-body">
                
                <!-- PASO 1: DIAGNÓSTICO -->
                <div :class="['wf-step', modoComponente ? 'completed' : 'active']">
                  <div class="step-num">1</div>
                  <div class="step-content">
                    <h4>Inspección técnica y diagnóstico <span v-if="modoComponente" class="step-badge">✓ Registrado</span></h4>
                    <p v-if="!modoComponente">Registre los resultados de la inspección inicial.</p>
                    <div v-if="!modoComponente">
                      <label class="campo">Diagnóstico
                        <textarea v-model="formDiagnostico.diagnostico" rows="3" placeholder="Falla detectada y componente afectado"></textarea>
                      </label>
                      <label class="campo">Plan de solución
                        <textarea v-model="formDiagnostico.plan_solucion" rows="2" placeholder="Acciones previstas para resolver el problema"></textarea>
                      </label>
                      
                      <fieldset class="compuerta" style="margin-bottom: 15px; border: 1px solid var(--sigta-borde); padding: 10px; border-radius: 6px;">
                        <legend style="font-size:12px; font-weight:bold; color:var(--sigta-texto-suave);">¿Requiere compra de componentes?</legend>
                        <label style="margin-right:15px; cursor:pointer;"><input v-model="formDiagnostico.requiere_compra" type="radio" :value="false"> No</label>
                        <label style="cursor:pointer;"><input v-model="formDiagnostico.requiere_compra" type="radio" :value="true"> Sí</label>
                      </fieldset>

                      <button class="primary step-btn" :disabled="procesando||!formDiagnostico.diagnostico.trim()||!formDiagnostico.plan_solucion.trim()" @click="guardarDiagnostico">
                        {{ formDiagnostico.requiere_compra ? 'Guardar y realizar requerimiento' : 'Guardar diagnóstico' }}
                      </button>
                    </div>
                  </div>
                </div>

                <!-- PASO 2: REQUERIMIENTO DE COMPRA -->
                <div v-if="formDiagnostico.requiere_compra" :class="['wf-step', !modoComponente ? 'locked' : 'active']">
                  <div class="step-num">2</div>
                  <div class="step-content">
                    <h4>Realizar requerimiento de compra</h4>
                    <p>Complete la solicitud del repuesto necesario.</p>
                    <div v-if="modoComponente">
                      <label class="campo">Componente requerido
                        <input v-model="formComponente.producto_requerido" placeholder="Ej.: Compresor 12000 BTU" class="full-select">
                      </label>
                      <label class="campo">Características del componente
                        <textarea v-model="formComponente.especificacion_producto" rows="2" placeholder="Marca, modelo, voltaje..."></textarea>
                      </label>
                      <label class="campo">Cantidad
                        <input v-model="formComponente.cantidad_requerida" type="number" min="1" class="full-select">
                      </label>
                      <label class="campo">Costo estimado (Bs.)
                        <input v-model="formComponente.costo_estimado" type="number" min="0" step="0.01" class="full-select">
                      </label>
                      <label class="campo">Cotización (opcional)
                        <input type="file" accept="application/pdf,image/*" @change="onCotizacion" class="full-select">
                      </label>
                      
                      <div class="step-actions mt-2">
                        <button class="reject" @click="retroceder">Retroceder</button>
                        <button class="primary flex-btn" :disabled="procesando||!formComponente.producto_requerido.trim()" @click="enviarRequerimiento">Enviar requerimiento</button>
                      </div>
                    </div>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>
      </section>"""

content = re.sub(
    r'<!-- ==================== A\. ÓRDENES DE TRABAJO ==================== -->.*?<!-- ==================== EN ESPERA DE COMPRA ==================== -->',
    html_template + '\n\n      <!-- ==================== EN ESPERA DE COMPRA ==================== -->',
    content,
    flags=re.DOTALL
)

# 2. Agregar lógica de script
script_replacement = """
function retroceder() {
  modoComponente.value = false
}

async function guardarDiagnostico() {
  if (formDiagnostico.requiere_compra) {
    modoComponente.value = true
    return
  }
  
  procesando.value = true
  try {
    await postAccion(ordenAbierta.value, 'registrar-diagnostico', {
      diagnostico: formDiagnostico.diagnostico.trim(),
      plan_solucion: formDiagnostico.plan_solucion.trim(),
    })
    cerrarOrden()
    vista.value = 'trabajo'
  } catch (e) { alert(e.message) }
  finally { procesando.value = false }
}

async function enviarRequerimiento() {
  procesando.value = true
  try {
    const token = localStorage.getItem('sigta_token');
    
    // 1. Guardar diagnóstico primero (sin usar postAccion para evitar refrescar la UI aún)
    const respDiag = await fetch(`/api/mantenimiento/requerimientos/${ordenAbierta.value.id}/registrar-diagnostico/`, {
      method: 'POST',
      headers: { Authorization: `Token ${token}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({
        diagnostico: formDiagnostico.diagnostico.trim(),
        plan_solucion: formDiagnostico.plan_solucion.trim(),
      })
    })
    
    if (!respDiag.ok) {
      const d = await respDiag.json().catch(() => ({}))
      throw new Error(d.detalle || 'Error al guardar el diagnóstico.')
    }

    // 2. Solicitar requerimiento
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
  finally { procesando.value = false }
}
"""

content = re.sub(r'async function guardarDiagnostico\(\) \{.*?\}(?=\s+function onCotizacion)', script_replacement.strip(), content, flags=re.DOTALL)
content = re.sub(r'async function enviarRequerimiento\(\) \{.*?\}(?=\s+/\* ----------)', '', content, flags=re.DOTALL)


# 3. Inject CSS
css_injection = """
/* ====== NUEVOS ESTILOS: GESTIÓN DE TICKETS (MASTER-DETAIL) ====== */
.gestion-tickets-layout { display: flex; gap: 20px; height: calc(100vh - 160px); overflow: hidden; align-items: stretch; }
.gestion-left { width: 35%; display: flex; flex-direction: column; background: var(--sigta-blanco); border: 1px solid var(--sigta-borde); border-radius: 12px; overflow: hidden; }
.gestion-left-header { padding: 15px 20px; border-bottom: 1px solid var(--sigta-borde-suave); display: flex; justify-content: space-between; align-items: center; background: #f8fafc; }
.gestion-left-header h3 { margin: 0; font-size: 14px; color: var(--sigta-texto); }
.badge { background: #e0e7ff; color: var(--sigta-azul); font-size: 11px; padding: 4px 8px; border-radius: 20px; font-weight: bold; }
.gestion-lista { flex: 1; overflow-y: auto; padding: 10px; display: flex; flex-direction: column; gap: 8px; }
.ticket-item { padding: 14px; border: 1px solid var(--sigta-borde-suave); border-radius: 8px; cursor: pointer; transition: all 0.2s; background: var(--sigta-blanco); }
.ticket-item:hover { border-color: var(--sigta-borde); box-shadow: 0 2px 5px rgba(0,0,0,0.03); }
.ticket-item.activo { border-color: var(--sigta-azul); background: #f8fafc; }
.ticket-item.t-validar { border-left: 4px solid var(--sigta-error); }
.ticket-item.t-clasificar { border-left: 4px solid var(--sigta-mostaza); }
.ticket-item.t-designar { border-left: 4px solid var(--sigta-azul); }
.ticket-item h4 { margin: 8px 0 4px; font-size: 14px; color: var(--sigta-texto); }
.ticket-item p { margin: 0; font-size: 11px; color: var(--sigta-texto-suave); }
.e-validar { background: #fee2e2; color: #b91c1c; }
.e-clasificar { background: #fef3c7; color: #b45309; }
.e-designar { background: #e0e7ff; color: #4338ca; }
.empty-list { text-align: center; padding: 30px; font-size: 12px; color: var(--sigta-texto-suave); }

.gestion-right { flex: 1; display: flex; flex-direction: column; overflow: hidden; }
.gestion-detalle-wrapper { display: flex; flex-direction: column; gap: 15px; height: 100%; }
.ticket-header-card { background: var(--sigta-blanco); border: 1px solid var(--sigta-borde); border-radius: 12px; padding: 20px; flex-shrink: 0; }
.t-head { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 8px; }
.t-head h2 { margin: 0; font-size: 18px; color: var(--sigta-texto); }
.codigo-badge { font-weight: bold; color: var(--sigta-azul); font-size: 14px; }
.t-meta { margin: 0 0 12px; font-size: 12px; color: var(--sigta-texto-suave); }
.desc-box { background: #f8fafc; padding: 12px; border-radius: 8px; font-size: 13px; line-height: 1.5; color: var(--sigta-texto); border: 1px solid var(--sigta-borde-suave); }

.workflow-card { flex: 1; background: var(--sigta-blanco); border: 1px solid var(--sigta-borde); border-radius: 12px; display: flex; flex-direction: column; overflow: hidden; }
.wf-header { padding: 15px 20px; border-bottom: 1px solid var(--sigta-borde-suave); font-weight: bold; color: var(--sigta-texto); background: #f8fafc; }
.wf-body { flex: 1; overflow-y: auto; padding: 25px; display: flex; flex-direction: column; position: relative; }
.wf-body::before { content: ''; position: absolute; left: 45px; top: 35px; bottom: 35px; width: 2px; background: var(--sigta-borde-suave); z-index: 1; }

.wf-step { display: flex; margin-bottom: 30px; position: relative; z-index: 2; }
.wf-step:last-child { margin-bottom: 0; }
.step-num { width: 42px; height: 42px; border-radius: 50%; background: var(--sigta-borde); color: var(--sigta-texto-suave); display: flex; align-items: center; justify-content: center; font-weight: bold; flex-shrink: 0; border: 4px solid var(--sigta-blanco); transition: all 0.3s; }
.step-content { margin-left: 20px; flex: 1; background: var(--sigta-blanco); border: 1px solid var(--sigta-borde); border-radius: 10px; padding: 15px 20px; transition: all 0.3s; }
.step-content h4 { margin: 0 0 5px; font-size: 15px; display: flex; justify-content: space-between; align-items: center; }
.step-content p { margin: 0 0 15px; font-size: 12px; color: var(--sigta-texto-suave); }
.step-badge { font-size: 10px; text-transform: uppercase; background: #f0fdf4; color: #166534; padding: 3px 8px; border-radius: 10px; }

.wf-step.active .step-num { background: var(--sigta-azul); color: var(--sigta-blanco); box-shadow: 0 0 0 4px rgba(0, 42, 92, 0.1); }
.wf-step.active .step-content { border-color: var(--sigta-azul); box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
.wf-step.locked { opacity: 0.5; pointer-events: none; }
.wf-step.locked .step-content { background: #f8fafc; }
.wf-step.completed .step-num { background: var(--sigta-azul-medio); color: var(--sigta-blanco); }
.wf-step.completed .step-content { border-color: var(--sigta-borde-suave); background: #f8fafc; }

.step-actions { display: flex; gap: 10px; }
.flex-btn { flex: 1; text-align: center; justify-content: center; padding: 10px; border-radius: 6px; font-weight: bold; cursor: pointer; border: none; }
.reject { background: var(--sigta-blanco); border: 1px solid var(--sigta-error); color: var(--sigta-error); padding: 10px 20px; border-radius: 6px; font-weight: bold; cursor: pointer; }
.p-options { display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px; margin-bottom: 15px; }
.p-options label { border: 1px solid var(--sigta-borde); border-radius: 6px; padding: 8px; text-align: center; font-size: 12px; font-weight: bold; cursor: pointer; color: var(--sigta-texto-suave); }
.p-options label:has(input:checked) { background: #e0e7ff; border-color: var(--sigta-azul); color: var(--sigta-azul); }
.p-options input { display: none; }
textarea { width: 100%; border: 1px solid var(--sigta-borde); border-radius: 6px; padding: 10px; font-family: inherit; font-size: 13px; resize: vertical; margin-bottom: 15px; }
.full-select { width: 100%; border: 1px solid var(--sigta-borde); border-radius: 6px; padding: 10px; font-family: inherit; font-size: 13px; color: var(--sigta-texto); background: #fff; margin-bottom: 15px; }
.step-btn { width: 100%; padding: 12px; border-radius: 6px; font-weight: bold; cursor: pointer; border: none; background: var(--sigta-azul); color: var(--sigta-blanco); font-size: 14px; text-align: center; margin-top:10px; }
"""

# Insert CSS before @media(max-width
content = content.replace('@media(max-width:1050px)', css_injection + '\n@media(max-width:1050px)')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Actualizado exitosamente.")
