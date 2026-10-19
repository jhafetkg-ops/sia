import sys

vue_content = r'''<template>
  <div class="sigta-role-layout">
    <DafMenu />

    <main class="main-content">
      <header class="top-bar" style="margin-bottom: 15px;">
        <div class="breadcrumb">
          <span>Direcci&oacute;n Administrativa Financiera</span>
          <span class="separator">/</span>
          <strong>Emitir Certificaci&oacute;n</strong>
        </div>
        <div class="user-profile">
          <div class="avatar">{{ avatarInicial }}</div>
          <div class="info">
            <b>{{ usuario.first_name || usuario.username }}</b>
            <span>{{ usuario.rol_nombre || 'DAF' }}</span>
          </div>
        </div>
      </header>

      <div class="gestion-tickets-layout">
        
        <div class="gestion-left">
          <div class="gestion-left-header">
            <h3>Pendientes de Certificaci&oacute;n</h3>
            <span class="badge">{{ porCertificar.length }} por emitir</span>
          </div>
          <div class="gestion-lista">
            <article 
              v-for="r in porCertificar" 
              :key="r.id" 
              :class="['ticket-item', itemActivo?.id === r.id ? 'activo' : '', 't-validar']" 
              @click="abrir(r)"
            >
              <div class="top">
                <span>{{ r.codigo }}</span>
                <em class="e-validar">Requiere Certificaci&oacute;n</em>
              </div>
              <h4>{{ r.titulo }}</h4>
              <p>Monto Estimado: Bs. {{ r.monto_estimado || 's/d' }}</p>
            </article>
            <div v-if="!porCertificar.length" class="empty-list">
              Bandeja al d&iacute;a. No hay expedientes pendientes de certificaci&oacute;n.
            </div>
          </div>
        </div>

        <div class="gestion-right">
          <div v-if="!itemActivo" class="empty" style="margin-top: 40px;">
            <span style="font-size:30px">&marker;</span>
            <h3>Seleccione un expediente</h3>
            <p>Seleccione una solicitud de compra de la lista para emitir su certificaci&oacute;n presupuestaria.</p>
          </div>
          <div v-else class="gestion-detalle-wrapper">
            
            <div class="ticket-header-card" style="flex-shrink: 0;">
              <div class="t-head">
                <h2 style="font-size: 18px;">{{ itemActivo.titulo }}</h2>
                <span class="codigo-badge">{{ itemActivo.codigo }}</span>
              </div>
              <p class="t-meta">
                <span>👤 <b>Solicitante:</b> {{ itemActivo.solicitante_nombre || 's/d' }}</span>
                <span>📌 <b>&Aacute;rea:</b> {{ itemActivo.area || 's/d' }}</span>
              </p>
              
              <div class="t-content" style="grid-template-columns: 1fr; gap: 10px;">
                <div class="desc-box">
                  <p><b>Descripci&oacute;n:</b> {{ itemActivo.descripcion }}</p>
                  <p><b>Monto estimado:</b> Bs. {{ itemActivo.monto_estimado || 's/d' }}</p>
                </div>
                
                <div class="evidence-box">
                  <div class="evidence-info">
                    <strong>Documentos adjuntos</strong>
                    <div class="doc-links">
                      <a v-if="itemActivo.informe" :href="itemActivo.informe" target="_blank" class="evidence-btn">Informe &#x2197;</a>
                      <a v-if="itemActivo.poa" :href="itemActivo.poa" target="_blank" class="evidence-btn">POA &#x2197;</a>
                      <a v-if="itemActivo.proforma" :href="itemActivo.proforma" target="_blank" class="evidence-btn">Proforma &#x2197;</a>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div class="workflow-card" style="flex-shrink: 0; margin-bottom: 20px;">
              <div class="wf-header">Emitir Certificaci&oacute;n Presupuestaria</div>
              <div class="wf-body" style="overflow-y: visible;">
                
                <!-- PASO 1 -->
                <div :class="['wf-step', formCert.partida_confirmada ? 'completed' : 'active']">
                  <div class="step-num">1</div>
                  <div class="step-content">
                    <h4>Partida Presupuestaria <span v-if="formCert.partida_confirmada" class="step-badge">&check; {{ formCert.partida.codigo }} - {{ formCert.partida.descripcion }}</span></h4>
                    <p>Busque y seleccione la partida presupuestaria oficial.</p>
                    
                    <div v-if="!formCert.partida_confirmada" class="step-actions" style="flex-direction: column; align-items: stretch;">
                      <input type="text" v-model="searchPartida" placeholder="Buscar por código o descripción..." class="text-input" />
                      
                      <div class="search-results" v-if="searchPartida.trim().length > 0">
                        <div 
                          v-for="p in partidasFiltradas" 
                          :key="p.codigo" 
                          class="search-item" 
                          @click="seleccionarPartida(p)"
                        >
                          <b>{{ p.codigo }}</b> - {{ p.descripcion }}
                        </div>
                        <div v-if="partidasFiltradas.length === 0" class="search-item empty">
                          No se encontraron coincidencias
                        </div>
                      </div>
                    </div>
                    <div v-else class="step-actions">
                      <button class="reject" @click="formCert.partida_confirmada = false">Cambiar Partida</button>
                    </div>
                  </div>
                </div>

                <!-- PASO 2 -->
                <div :class="['wf-step', !formCert.partida_confirmada ? 'locked' : 'active']">
                  <div class="step-num">2</div>
                  <div class="step-content">
                    <h4>Par&aacute;metros de la Certificaci&oacute;n</h4>
                    <p>Complete y verifique los datos para la generaci&oacute;n del documento.</p>
                    
                    <div v-if="formCert.partida_confirmada" class="cert-form">
                      
                      <fieldset>
                        <legend>SECCI&Oacute;N 1: DATOS DE CABECERA Y SISTEMA</legend>
                        <div class="form-grid">
                          <div class="campo">
                            <label>ID Certificaci&oacute;n</label>
                            <input type="text" v-model="formCert.id_certificacion" disabled class="text-input disabled" />
                          </div>
                          <div class="campo">
                            <label>Fecha de Emisi&oacute;n</label>
                            <input type="date" v-model="formCert.fecha_emision" disabled class="text-input disabled" />
                          </div>
                          <div class="campo">
                            <label>Gesti&oacute;n</label>
                            <input type="text" v-model="formCert.gestion" disabled class="text-input disabled" />
                          </div>
                          <div class="campo">
                            <label>Repartici&oacute;n Emisora</label>
                            <input type="text" v-model="formCert.reparticion_emisora" disabled class="text-input disabled" />
                          </div>
                          <div class="campo">
                            <label>Tipo de Cambio</label>
                            <input type="number" step="0.01" v-model="formCert.tipo_cambio" class="text-input" />
                          </div>
                          <div class="campo">
                            <label>Fuente de Financiamiento</label>
                            <select v-model="formCert.fuente_financiamiento" class="text-input">
                              <option value="1 - TGN">1 - TGN</option>
                              <option value="2 - Recursos Propios">2 - Recursos Propios</option>
                              <option value="3 - Donaciones">3 - Donaciones</option>
                            </select>
                          </div>
                        </div>
                      </fieldset>

                      <fieldset>
                        <legend>SECCI&Oacute;N 2: DATOS DEL REQUERIMIENTO</legend>
                        <div class="form-grid">
                          <div class="campo">
                            <label>Unidad Solicitante / Interesado</label>
                            <input type="text" v-model="formCert.unidad_solicitante" disabled class="text-input disabled" />
                          </div>
                          <div class="campo">
                            <label>Doc. Referencia</label>
                            <input type="text" v-model="formCert.doc_referencia" disabled class="text-input disabled" />
                          </div>
                          <div class="campo full-width">
                            <label>Informe T&eacute;cnico / Cite</label>
                            <input type="text" v-model="formCert.informe_tecnico" disabled class="text-input disabled" />
                          </div>
                          <div class="campo full-width">
                            <label>Glosa / Descripci&oacute;n del Gasto</label>
                            <textarea v-model="formCert.glosa" class="text-input" rows="3"></textarea>
                          </div>
                        </div>
                      </fieldset>

                      <fieldset>
                        <legend>SECCI&Oacute;N 3: IMPUTACI&Oacute;N Y ASIGNACI&Oacute;N PRESUPUESTARIA</legend>
                        <div class="form-grid">
                          <div class="campo full-width">
                            <label>Partida Presupuestaria</label>
                            <input type="text" :value="formCert.partida.codigo + ' - ' + formCert.partida.descripcion" disabled class="text-input disabled" />
                          </div>
                          <div class="campo">
                            <label>Repartici&oacute;n Program&aacute;tica</label>
                            <input type="text" v-model="formCert.reparticion_programatica" class="text-input" />
                          </div>
                          <div class="campo">
                            <label>CATPROG (Categor&iacute;a Program&aacute;tica)</label>
                            <input type="text" v-model="formCert.catprog" class="text-input" />
                          </div>
                        </div>
                      </fieldset>

                      <fieldset>
                        <legend>SECCI&Oacute;N 4: VALORIZACI&Oacute;N Y TOTALES</legend>
                        <div class="form-grid">
                          <div class="campo">
                            <label>Monto Certificado (Bs.)</label>
                            <input type="number" step="0.01" v-model="formCert.monto_certificado" class="text-input" />
                          </div>
                          <div class="campo full-width">
                            <label>Monto en Literal</label>
                            <input type="text" :value="montoALiteral(formCert.monto_certificado)" disabled class="text-input disabled" />
                          </div>
                        </div>
                      </fieldset>

                      <div class="step-actions" style="margin-top: 20px;">
                        <button 
                          class="primary flex-btn" 
                          style="width: 100%; padding: 14px; font-size: 16px; background: #15803d !important; border-color: #15803d !important;" 
                          :disabled="procesando || !formCert.monto_certificado || formCert.monto_certificado <= 0" 
                          @click="emitirCertificacion"
                        >
                          Generar y Emitir Certificaci&oacute;n Presupuestaria
                        </button>
                      </div>

                    </div>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import DafMenu from '../components/DafMenu.vue'
import { jsPDF } from 'jspdf'

const router = useRouter()
const usuario = ref(JSON.parse(localStorage.getItem('sigta_usuario') || '{}'))
const token = () => localStorage.getItem('sigta_token')

const avatarInicial = computed(() => {
  const n = usuario.value.first_name || usuario.value.username || 'U'
  return n.charAt(0).toUpperCase()
})

const items = ref([])
const cargando = ref(true)
const procesando = ref(false)
const itemActivo = ref(null)

const porCertificar = computed(() => items.value.filter(r => !r.certificacion_presupuestaria && r.estado !== 'RECHAZADO' && r.estado !== 'CERRADO_SIN_COMPRA'))

// PARTIDAS
const searchPartida = ref('')
const listaPartidas = [
  { "codigo": "24110", "descripcion": "Mantenimiento y Reparación de Edificios y Estructuras" },
  { "codigo": "24120", "descripcion": "Mantenimiento y Reparación de Vehículos, Maquinaria y Equipos" },
  { "codigo": "24130", "descripcion": "Mantenimiento y Reparación de Muebles y Enseres" },
  { "codigo": "24200", "descripcion": "Mantenimiento y Reparación de Vías y Obras Públicas" },
  { "codigo": "24300", "descripcion": "Servicios de Instalación, Montaje y Acondicionamiento" },
  { "codigo": "32100", "descripcion": "Papel de Escritorio y Cartulina" },
  { "codigo": "32200", "descripcion": "Productos de Artes Gráficas, Impresos y Cartón" },
  { "codigo": "34110", "descripcion": "Combustibles, Lubricantes y Derivados para Vehículos y Equipos" },
  { "codigo": "34200", "descripcion": "Productos Químicos, Farmacéuticos y Reactivos de Laboratorio" },
  { "codigo": "34300", "descripcion": "Llantas y Neumáticos" },
  { "codigo": "34400", "descripcion": "Productos de Cuero y Caucho" },
  { "codigo": "34500", "descripcion": "Productos de Minerales No Metálicos y Plásticos" },
  { "codigo": "34600", "descripcion": "Productos Metálicos (Perfiles, Soportes, Estructuras)" },
  { "codigo": "34800", "descripcion": "Herramientas Menores y Accesorios Mecánicos" },
  { "codigo": "39100", "descripcion": "Material Eléctrico, Cables, Iluminación y Electrónica" },
  { "codigo": "39200", "descripcion": "Material de Aseo, Limpieza y Utensilios de Higiene" },
  { "codigo": "39400", "descripcion": "Insumos, Repuestos y Accesorios Informáticos (RAM, Discos, Cables Red)" },
  { "codigo": "39500", "descripcion": "Útiles de Escritorio, Oficina y Material Didáctico" },
  { "codigo": "39700", "descripcion": "Utensilios de Cocina, Comedor y Laboratorio" },
  { "codigo": "39800", "descripcion": "Otros Repuestos y Accesorios General" },
  { "codigo": "43110", "descripcion": "Equipo de Oficina y Muebles" },
  { "codigo": "43120", "descripcion": "Equipos Computacionales, Servidores y Periféricos" },
  { "codigo": "43200", "descripcion": "Maquinaria y Equipos para Laboratorios y Talleres" },
  { "codigo": "43700", "descripcion": "Otra Maquinaria, Equipos e Instrumentos Especializados" }
]

const partidasFiltradas = computed(() => {
  const t = searchPartida.value.toLowerCase()
  return listaPartidas.filter(p => p.codigo.includes(t) || p.descripcion.toLowerCase().includes(t))
})

const formCert = reactive({
  partida: null,
  partida_confirmada: false,

  id_certificacion: '',
  fecha_emision: '',
  gestion: '2026',
  reparticion_emisora: 'DIRECCION ADMIN. FINANCIERO',
  tipo_cambio: 6.96,
  fuente_financiamiento: '2 - Recursos Propios',

  unidad_solicitante: '',
  doc_referencia: '',
  informe_tecnico: '',
  glosa: '',

  reparticion_programatica: '30020000',
  catprog: '00000001',

  monto_certificado: 0
})

function seleccionarPartida(p) {
  formCert.partida = p
  formCert.partida_confirmada = true
  searchPartida.value = ''
}

function montoALiteral(monto) {
  if (!monto || isNaN(monto)) return 'CERO 00/100 BOLIVIANOS'
  
  const unidades = ['', 'UNO', 'DOS', 'TRES', 'CUATRO', 'CINCO', 'SEIS', 'SIETE', 'OCHO', 'NUEVE']
  const decenas = ['', 'DIEZ', 'VEINTE', 'TREINTA', 'CUARENTA', 'CINCUENTA', 'SESENTA', 'SETENTA', 'OCHENTA', 'NOVENTA']
  const especiales = {11: 'ONCE', 12: 'DOCE', 13: 'TRECE', 14: 'CATORCE', 15: 'QUINCE', 16: 'DIECISEIS', 17: 'DIECISIETE', 18: 'DIECIOCHO', 19: 'DIECINUEVE'}
  
  function aTexto(num) {
    if (num === 0) return 'CERO'
    if (num < 10) return unidades[num]
    if (num < 20) return especiales[num] || 'DIEZ Y ' + unidades[num % 10]
    if (num === 10) return 'DIEZ'
    if (num === 20) return 'VEINTE'
    if (num < 30) return 'VEINTI' + unidades[num % 10]
    if (num < 100) return decenas[Math.floor(num/10)] + (num%10 === 0 ? '' : ' Y ' + unidades[num%10])
    if (num === 100) return 'CIEN'
    if (num < 200) return 'CIENTO ' + aTexto(num%100)
    if (num < 1000) {
      const centenas = ['', 'CIENTO', 'DOSCIENTOS', 'TRESCIENTOS', 'CUATROCIENTOS', 'QUINIENTOS', 'SEISCIENTOS', 'SETECIENTOS', 'OCHOCIENTOS', 'NOVECIENTOS']
      return centenas[Math.floor(num/100)] + (num%100 === 0 ? '' : ' ' + aTexto(num%100))
    }
    if (num === 1000) return 'MIL'
    if (num < 2000) return 'MIL ' + aTexto(num%1000)
    if (num < 1000000) return aTexto(Math.floor(num/1000)) + ' MIL' + (num%1000 === 0 ? '' : ' ' + aTexto(num%1000))
    return num.toString()
  }
  
  const partes = parseFloat(monto).toFixed(2).split('.')
  const enteros = parseInt(partes[0], 10)
  const centavos = partes[1] || '00'
  
  let textoEnteros = aTexto(enteros).replace(/ UNO$/, ' UN').replace(/^UNO MIL/, 'UN MIL')
  return `${textoEnteros} ${centavos}/100 BOLIVIANOS`
}

async function cargar() {
  cargando.value = true
  try {
    const r = await fetch('/api/compras/solicitudes/', {
      headers: { Authorization: `Token ${token()}` }
    })
    const d = await r.json()
    if (!r.ok) throw new Error('Error al cargar')
    items.value = Array.isArray(d) ? d : []
  } catch (e) {
    console.error(e)
  } finally {
    cargando.value = false
  }
}

function abrir(item) {
  itemActivo.value = item
  formCert.partida = null
  formCert.partida_confirmada = false
  searchPartida.value = ''
  
  formCert.id_certificacion = `C-${Math.floor(Math.random()*100000000).toString().padStart(8, '0')}`
  formCert.fecha_emision = new Date().toISOString().split('T')[0]
  formCert.gestion = '2026'
  formCert.reparticion_emisora = 'DIRECCION ADMIN. FINANCIERO'
  formCert.tipo_cambio = 6.96
  formCert.fuente_financiamiento = '2 - Recursos Propios'
  
  formCert.unidad_solicitante = item.area || '13200 MANTENIMIENTO / UTIC'
  formCert.doc_referencia = item.codigo
  formCert.informe_tecnico = `INF-TEC-${item.codigo}`
  formCert.glosa = item.descripcion || ''
  
  formCert.reparticion_programatica = '30020000'
  formCert.catprog = '00000001'
  
  formCert.monto_certificado = item.monto_estimado || 0
}

async function emitirCertificacion() {
  if (!formCert.partida_confirmada || !formCert.monto_certificado) return
  
  procesando.value = true
  try {
    const doc = new jsPDF()
    doc.setFontSize(20)
    doc.text('CERTIFICADO DE PREVISIÓN PRESUPUESTARIA', 105, 30, { align: 'center' })
    doc.setFontSize(11)
    
    let y = 50
    doc.text(`Nro. Certificación: ${formCert.id_certificacion}`, 20, y); doc.text(`Fecha: ${formCert.fecha_emision}`, 140, y); y += 8;
    doc.text(`Repartición Emisora: ${formCert.reparticion_emisora}`, 20, y); doc.text(`Gestión: ${formCert.gestion}`, 140, y); y += 8;
    doc.text(`Unidad Solicitante: ${formCert.unidad_solicitante}`, 20, y); y += 8;
    doc.text(`Doc. Referencia: ${formCert.doc_referencia}`, 20, y); doc.text(`Informe Téc: ${formCert.informe_tecnico}`, 100, y); y += 8;
    doc.text(`Fuente: ${formCert.fuente_financiamiento}`, 20, y); doc.text(`TC: ${formCert.tipo_cambio}`, 140, y); y += 15;
    
    doc.setFontSize(10)
    doc.text('PARTIDA PRESUPUESTARIA A AFECTAR:', 20, y); y += 6;
    doc.setFontSize(11)
    doc.text(`${formCert.partida.codigo} - ${formCert.partida.descripcion}`, 20, y); y += 8;
    doc.text(`Prog: ${formCert.reparticion_programatica} | CatProg: ${formCert.catprog}`, 20, y); y += 15;
    
    doc.setFontSize(10)
    doc.text('GLOSA / DESCRIPCIÓN:', 20, y); y += 6;
    doc.setFontSize(11)
    doc.text(formCert.glosa || 'Sin descripción', 20, y, { maxWidth: 170 }); y += 25;
    
    doc.setFontSize(12)
    doc.text(`MONTO CERTIFICADO: Bs. ${parseFloat(formCert.monto_certificado).toFixed(2)}`, 20, y); y += 8;
    doc.text(`LITERAL: ${montoALiteral(formCert.monto_certificado)}`, 20, y, { maxWidth: 170 });
    
    const pdfBlob = doc.output('blob')
    const fd = new FormData()
    fd.append('certificacion_presupuestaria', pdfBlob, `${formCert.id_certificacion}.pdf`)

    const r = await fetch(`/api/compras/solicitudes/${itemActivo.value.id}/certificar-daf/`, {
      method: 'POST',
      headers: { Authorization: `Token ${token()}` },
      body: fd
    })
    
    const d = await r.json().catch(()=>({}))
    if (!r.ok) throw new Error(d.detalle || Object.values(d)[0] || 'Error al emitir.')

    if(window.sigtaConfirm) {
      await window.sigtaConfirm('Certificación generada y emitida con éxito! El expediente fue derivado.')
    } else {
      alert('Certificación generada y emitida con éxito! El expediente fue derivado.')
    }
    
    itemActivo.value = null
    await cargar()
  } catch (e) {
    alert(e.message)
  } finally {
    procesando.value = false
  }
}

onMounted(() => {
  if (!token()) router.push('/login')
  else cargar()
})
</script>

<style scoped>
@import '../assets/role-theme.css';

/* Layout overrides para hacer scrolleable el detalle */
.gestion-right {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.gestion-detalle-wrapper {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow-y: auto;
  padding-right: 8px;
  gap: 15px;
}
/* Scrollbar para la vista de detalle */
.gestion-detalle-wrapper::-webkit-scrollbar { width: 6px; }
.gestion-detalle-wrapper::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }

.doc-links {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  margin-top: 10px;
}
.evidence-btn {
  background: var(--sigta-azul);
  color: var(--sigta-blanco);
  text-decoration: none;
  font-size: 12px;
  font-weight: bold;
  padding: 8px 16px;
  border-radius: 6px;
  transition: opacity 0.2s;
  white-space: nowrap;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}
.evidence-btn:hover {
  opacity: 0.9;
}

/* Buscador de partidas */
.search-results {
  width: 100%;
  border: 1px solid var(--sigta-borde);
  border-radius: 6px;
  margin-top: 4px;
  max-height: 200px;
  overflow-y: auto;
  background: #fff;
  box-shadow: 0 4px 12px rgba(0,0,0,0.1);
}
.search-item {
  padding: 10px 14px;
  font-size: 13px;
  cursor: pointer;
  border-bottom: 1px solid var(--sigta-borde-suave);
}
.search-item:last-child {
  border-bottom: none;
}
.search-item:hover {
  background: #f8fafc;
  color: var(--sigta-azul);
}
.search-item.empty {
  color: var(--sigta-texto-suave);
  text-align: center;
  cursor: default;
}
.search-item.empty:hover {
  background: #fff;
  color: var(--sigta-texto-suave);
}

/* Formulario Certificación */
.cert-form fieldset {
  border: 1px solid var(--sigta-borde-suave);
  border-radius: 8px;
  padding: 15px 20px;
  margin-bottom: 20px;
  background: #fcfcfc;
}
.cert-form legend {
  font-size: 11px;
  font-weight: 900;
  color: var(--sigta-azul);
  padding: 0 8px;
  letter-spacing: 0.5px;
}
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 15px;
}
.form-grid .full-width {
  grid-column: 1 / -1;
}
.cert-form .campo {
  margin: 0;
}
.cert-form label {
  display: block;
  font-size: 11px;
  color: var(--sigta-texto-suave);
  margin-bottom: 4px;
}
.text-input.disabled {
  background: #f1f5f9;
  color: #64748b;
  cursor: not-allowed;
}
</style>
'''

with open(r'c:\Users\INTEL\Desktop\SIGTA - 5.0\Sigtap\frontend\src\views\DafEmitirView.vue', 'w', encoding='utf-8') as f:
    f.write(vue_content)
