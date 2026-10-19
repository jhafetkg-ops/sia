<template>
  <div class="workbench sigta-role-layout">
    <aside class="sidebar" :class="{ abierto: menuAbierto }">
      <div class="brand-row">
        <div class="brand"><span><img src="/img/emi.jpg" alt="EMI"></span><div><b>SIA</b><small>Gestión técnica</small></div></div>
        <button type="button" class="menu-toggle" :aria-expanded="menuAbierto" aria-label="Mostrar opciones del menú" @click="menuAbierto = !menuAbierto"><span></span><span></span><span></span></button>
      </div>
      <p class="nav-label">CENTRO DE TRABAJO</p>
      <button :class="{ active: modulo === 'resumen' }" @click="modulo = 'resumen'; menuAbierto = false"><i>⌂</i> Resumen</button>
      <button :class="{ active: modulo === 'soporte' }" @click="modulo = 'soporte'; menuAbierto = false"><i>ST</i> Soporte técnico <em>{{ conteos.soporte }}</em></button>
      <button :class="{ active: modulo === 'mantenimiento' }" @click="modulo = 'mantenimiento'; menuAbierto = false"><i>MT</i> Mantenimiento <em>{{ conteos.mantenimiento }}</em></button>
      <button :class="{ active: modulo === 'compras' }" @click="modulo = 'compras'; menuAbierto = false"><i>CP</i> Compras técnicas</button>
      <div class="sidebar-foot"><button class="logout" @click="mostrarLogout = true"><IconoSigta nombre="salir" :tamano="17" />Cerrar sesión</button></div>
    </aside>

    <LogoutModal :visible="mostrarLogout" @cancelar="mostrarLogout = false" @confirmar="confirmarCierreSesion" />

    <main>
      <header>
        <div><span class="crumb">SIA / {{ etiquetaRol }} / {{ tituloModulo }}</span><h1>{{ titulo }}</h1><p>{{ subtitulo }}</p></div>
        <div class="header-actions"><div class="today"><small>HOY</small><strong>{{ fechaActual }}</strong></div></div>
      
        <UsuarioHeader @actualizar="cargarDatos" />
      </header>

      <div v-if="error" class="alert">{{ error }}</div>

      <section v-if="modulo === 'resumen'">
        <div class="hero">
          <div><span class="eyebrow">{{ esJefe ? 'COORDINACIÓN GLOBAL' : 'CONSOLA DE CAMPO' }}</span><h2>{{ saludo }}, {{ primerNombre }}</h2><p>{{ esJefe ? 'Estos son los asuntos que requieren coordinación técnica hoy.' : 'Estas son las órdenes asignadas y próximas acciones de trabajo.' }}</p></div>
          <div class="hero-mark">{{ esJefe ? 'JU' : 'ET' }}</div>
        </div>
        <div class="stats">
          <article><span class="dot blue"></span><div><small>Soporte técnico</small><strong>{{ conteos.soporte }}</strong><p>{{ esJefe ? 'tickets para supervisar' : 'órdenes disponibles' }}</p></div></article>
          <article><span class="dot amber"></span><div><small>Mantenimiento</small><strong>{{ conteos.mantenimiento }}</strong><p>{{ esJefe ? 'casos para coordinar' : 'trabajos registrados' }}</p></div></article>
          <article><span class="dot red"></span><div><small>Prioridad inmediata</small><strong>{{ urgentes }}</strong><p>casos altos o críticos</p></div></article>
          <article><span class="dot green"></span><div><small>{{ esJefe ? 'Cobertura' : 'Mi avance' }}</small><strong>{{ cargando ? '…' : '100%' }}</strong><p>información sincronizada</p></div></article>
        </div>
        <div class="columns">
          <section class="panel"><div class="panel-head"><div><span class="eyebrow">BANDEJA PRIORITARIA</span><h3>Próximas acciones</h3></div><button @click="modulo='soporte'">Ver bandeja →</button></div>
            <div class="action-list">
              <article v-for="accion in acciones" :key="accion.titulo"><span :class="['action-icon', accion.color]">{{ accion.icono }}</span><div><strong>{{ accion.titulo }}</strong><p>{{ accion.texto }}</p></div><span class="tag">{{ accion.estado }}</span></article>
            </div>
          </section>
          <aside class="panel quick"><div class="panel-head"><div><span class="eyebrow">ACCESOS RÁPIDOS</span><h3>Operación</h3></div></div>
            <button v-for="item in accesos" :key="item.titulo" @click="modulo=item.modulo"><span>{{ item.icono }}</span><div><strong>{{ item.titulo }}</strong><small>{{ item.texto }}</small></div><b>›</b></button>
          </aside>
        </div>
      </section>

      <section v-else class="module-view">
        <div class="module-toolbar">
          <div class="filters"><button v-for="f in filtros" :key="f" :class="{ active: filtro === f }" @click="filtro=f">{{ f }}</button></div>
          <label>⌕ <input v-model="busqueda" placeholder="Buscar por código, asunto o solicitante"></label>
        </div>
        <div v-if="cargando" class="empty">Actualizando bandeja…</div>
        <div v-else-if="registrosFiltrados.length" class="ticket-grid">
          <article v-for="item in registrosFiltrados" :key="item.id" class="ticket">
            <div class="ticket-top"><span class="code">{{ codigo(item) }}</span><span :class="['priority', prioridad(item).toLowerCase()]">{{ prioridad(item) }}</span></div>
            <h3>{{ asunto(item) }}</h3><p>{{ descripcion(item) }}</p>
            <div class="meta"><span>Solicitante<br><b>{{ solicitante(item) }}</b></span><span>Estado<br><b>{{ estado(item) }}</b></span></div>
            <div class="ticket-actions">
              <button class="secondary">Ver expediente</button>
              <button class="primary">{{ accionPrincipal }}</button>
            </div>
          </article>
        </div>
        <div v-else class="empty"><span>✓</span><h3>Bandeja al día</h3><p>No hay registros para mostrar en este módulo.</p></div>
      </section>
    </main>
  </div>
</template>

<script setup>
import UsuarioHeader from '../components/UsuarioHeader.vue'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import LogoutModal from '../components/LogoutModal.vue'
import IconoSigta from '../components/IconoSigta.vue'

const router = useRouter()
const usuario = ref(JSON.parse(localStorage.getItem('sigta_usuario') || '{}'))
const roles = computed(() => (usuario.value.roles || []).map(r => String(r.codigo || '').toUpperCase()))
const esJefe = computed(() => roles.value.includes('JEFE_UTIC'))
const modulo = ref('resumen'); const filtro = ref('Todos'); const busqueda = ref(''); const menuAbierto = ref(false)
const soporte = ref([]); const mantenimiento = ref([]); const cargando = ref(false); const error = ref('')
const filtros = ['Todos', 'Nuevos', 'En proceso', 'Críticos']
const nombre = computed(() => usuario.value.nombre || usuario.value.nombre_completo || etiquetaRol.value)
const primerNombre = computed(() => nombre.value.split(' ')[0])
const iniciales = computed(() => nombre.value.split(' ').slice(0,2).map(x => x[0]).join('').toUpperCase())
const etiquetaRol = computed(() => esJefe.value ? 'Jefe de UTIC' : 'Especialista técnico')
const tituloModulo = computed(() => ({resumen:'Resumen',soporte:'Soporte técnico',mantenimiento:'Mantenimiento',compras:'Compras técnicas'})[modulo.value])
const titulo = computed(() => modulo.value === 'resumen' ? `Panel de ${etiquetaRol.value}` : tituloModulo.value)
const subtitulo = computed(() => modulo.value === 'resumen' ? (esJefe.value ? 'Asignación, seguimiento y control técnico institucional.' : 'Recepción, diagnóstico y ejecución de órdenes técnicas.') : `Gestione la bandeja de ${tituloModulo.value.toLowerCase()} desde un solo lugar.`)
const fechaActual = new Intl.DateTimeFormat('es-BO',{day:'2-digit',month:'short',year:'numeric'}).format(new Date())
const conteos = computed(() => ({soporte:soporte.value.length,mantenimiento:mantenimiento.value.length}))
const todos = computed(() => modulo.value === 'soporte' ? soporte.value : modulo.value === 'mantenimiento' ? mantenimiento.value : [])
const urgentes = computed(() => [...soporte.value,...mantenimiento.value].filter(x => /alta|cr.tica/i.test(String(x.prioridad || ''))).length)
const saludo = computed(() => new Date().getHours() < 12 ? 'Buenos días' : new Date().getHours() < 19 ? 'Buenas tardes' : 'Buenas noches')
const acciones = computed(() => esJefe.value ? [
  {icono:'✓',color:'blue',titulo:'Validar nuevos requerimientos',texto:'Revise procedencia técnica, prioridad y SLA.',estado:`${conteos.value.soporte} tickets`},
  {icono:'↗',color:'amber',titulo:'Asignar especialista',texto:'Distribuya órdenes según especialidad y carga.',estado:'Coordinar'},
  {icono:'▣',color:'green',titulo:'Revisar informes finales',texto:'Valide registros, firmas y fotogramas.',estado:'Control'}
] : [
  {icono:'↓',color:'blue',titulo:'Registrar recepción',texto:'Confirme el inicio de atención de sus órdenes.',estado:'Pendiente'},
  {icono:'⌕',color:'amber',titulo:'Inspección y diagnóstico',texto:'Documente daños y materiales necesarios.',estado:'Campo'},
  {icono:'▣',color:'green',titulo:'Informe y fotograma',texto:'Adjunte evidencias antes y después.',estado:'Cierre'}
])
const accesos = computed(() => [
  {icono:'ST',titulo:esJefe.value?'Validar tickets':'Mis órdenes TI',texto:esJefe.value?'Priorizar y asignar':'Diagnosticar y reparar',modulo:'soporte'},
  {icono:'MT',titulo:esJefe.value?'Asignar mantenimiento':'Trabajos de campo',texto:esJefe.value?'Coordinar especialistas':'Inspección y ejecución',modulo:'mantenimiento'},
  {icono:'CP',titulo:esJefe.value?'Derivar a Caja Chica':'Solicitar insumos',texto:'Gestionar falta de materiales',modulo:'compras'}
])
const accionPrincipal = computed(() => esJefe.value ? (modulo.value === 'mantenimiento' ? 'Validar y asignar' : 'Validar ticket') : 'Registrar atención')

const valor = (o,...ks) => { for(const k of ks) if(o?.[k] !== undefined && o[k] !== null) return o[k]; return '' }
const codigo = o => valor(o,'codigo','numero_ticket') || `#${o.id}`
const asunto = o => valor(o,'asunto','titulo','tipo_mantenimiento','descripcion_corta') || 'Requerimiento técnico'
const descripcion = o => String(valor(o,'descripcion','detalle','observaciones') || 'Sin descripción adicional.').slice(0,130)
const solicitante = o => valor(o,'solicitante_nombre','nombre_solicitante','solicitante_email') || 'Usuario institucional'
const estado = o => valor(o,'estado_nombre','estado')?.nombre || valor(o,'estado_nombre','estado') || 'Nuevo'
const prioridad = o => valor(o,'prioridad_nombre','prioridad') || 'Media'
const registrosFiltrados = computed(() => todos.value.filter(o => {
  const texto = `${codigo(o)} ${asunto(o)} ${descripcion(o)} ${solicitante(o)} ${estado(o)}`.toLowerCase()
  const coincide = texto.includes(busqueda.value.toLowerCase())
  if(filtro.value === 'Críticos') return coincide && /alta|cr.tica/i.test(prioridad(o))
  if(filtro.value === 'Nuevos') return coincide && /nuevo|pendiente|registrado/i.test(estado(o))
  if(filtro.value === 'En proceso') return coincide && /proceso|asignado|atenci.n/i.test(estado(o))
  return coincide
}))

async function cargar(url, destino){
  const token=localStorage.getItem('sigta_token'); const r=await fetch(url,{headers:{Authorization:`Token ${token}`}})
  if(!r.ok) throw new Error('No fue posible consultar la bandeja técnica.')
  const data=await r.json(); destino.value=Array.isArray(data)?data:(data.results||[])
}
async function cargarDatos(){
  cargando.value=true; error.value=''
  const resultados=await Promise.allSettled([cargar('/api/soporte/tickets/',soporte),cargar('/api/mantenimiento/requerimientos/',mantenimiento)])
  if(resultados.every(r=>r.status==='rejected')) error.value='No se pudo actualizar la información. Compruebe que el servidor esté disponible.'
  cargando.value=false
}
const mostrarLogout = ref(false)
function cerrarSesion(){ localStorage.removeItem('sigta_token'); localStorage.removeItem('sigta_usuario'); router.push('/login') }
function confirmarCierreSesion(){ mostrarLogout.value = false; cerrarSesion() }
onMounted(cargarDatos)
</script>

<style scoped>
*{box-sizing:border-box}.workbench{min-height:100vh;background:var(--sigta-azul-tenue);color:var(--sigta-azul-oscuro);font-family: var(--sigta-fuente)}.sidebar{position:fixed;inset:0 auto 0 0;width:270px;background:var(--sigta-azul);color:var(--sigta-blanco);padding:22px 16px;display:flex;flex-direction:column}.brand{display:flex;align-items:center;gap:12px;padding:0 10px 21px;border-bottom:1px solid #ffffff25}.brand>span{background:var(--sigta-mostaza);color:var(--sigta-azul);font-weight:900;border-radius:10px;padding:15px 10px}.brand b{display:block;font-size:24px}.brand small{opacity:.72}.profile{display:flex;gap:11px;align-items:center;padding:22px 10px}.avatar{width:42px;height:42px;border-radius:50%;background:var(--sigta-mostaza);color:var(--sigta-azul);display:grid;place-items:center;font-weight:800}.profile strong,.profile span{display:block}.profile strong{font-size:14px}.profile span{font-size:12px;color:var(--sigta-azul-texto-claro);margin-top:4px}.nav-label,.eyebrow{font-size:10px;font-weight:800;letter-spacing:1.5px}.nav-label{color:var(--sigta-texto-suave);margin:15px 12px 9px}.sidebar button{border:0;background:transparent;color:var(--sigta-azul-tenue);width:100%;padding:12px;border-radius:8px;text-align:left;display:flex;align-items:center;gap:12px;cursor:pointer;margin:2px 0}.sidebar button:hover,.sidebar button.active{background:#ffffff18;color:var(--sigta-blanco)}.sidebar button.active{box-shadow:inset 3px 0 var(--sigta-mostaza)}.sidebar button i{font-style:normal;font-size:11px;font-weight:800;width:27px}.sidebar button em{margin-left:auto;background:#ffffff1f;border-radius:12px;padding:2px 8px;font-style:normal}.sidebar-foot{margin-top:auto;border-top:1px solid #ffffff20;padding-top:12px}.sidebar-foot .logout{justify-content:center;gap:14px!important;border:1px solid var(--sigta-mostaza)!important;border-radius:8px!important;background:transparent!important;color:#fff!important;box-shadow:inset 0 0 0 1px rgba(255,199,44,.35)!important;transition:transform .3s cubic-bezier(.34,1.55,.5,1),background .2s ease,color .2s ease,box-shadow .2s ease!important}.sidebar-foot .logout .icono-sigta{color:var(--sigta-mostaza);transition:color .2s ease}.sidebar-foot .logout:hover{background:#FFB300!important;color:var(--sigta-azul)!important;transform:scale(1.09)!important;box-shadow:0 14px 32px rgba(255,159,0,.55)!important}.sidebar-foot .logout:hover .icono-sigta{color:var(--sigta-azul)}main{margin-left:270px;padding:30px 38px 50px;max-width:1700px}header{display:flex;justify-content:space-between;align-items:center;margin-bottom:28px}h1{font-size:29px;margin:6px 0}header p{margin:0;color:var(--sigta-texto-suave)}.crumb{font-size:11px;color:var(--sigta-texto-suave)}.header-actions{display:flex;align-items:center;gap:16px}.icon-btn{border:1px solid var(--sigta-azul-texto-claro);background:var(--sigta-blanco);width:40px;height:40px;border-radius:9px;font-size:20px;cursor:pointer}.today{border-left:1px solid var(--sigta-azul-texto-claro);padding-left:16px}.today small,.today strong{display:block}.today small{color:var(--sigta-texto-suave);font-size:9px}.hero{background:linear-gradient(120deg,var(--sigta-azul),var(--sigta-texto-suave));color:var(--sigta-blanco);border-radius:14px;padding:27px 30px;display:flex;justify-content:space-between;align-items:center;box-shadow:0 8px 24px #123f7320}.hero .eyebrow{color:var(--sigta-mostaza)}.hero h2{font-size:24px;margin:7px 0}.hero p{margin:0;color:var(--sigta-azul-texto-claro)}.hero-mark{width:68px;height:68px;border:1px solid #ffffff40;border-radius:16px;display:grid;place-items:center;font-weight:900;font-size:21px;background:#ffffff10}.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:15px;margin:18px 0}.stats article{background:var(--sigta-blanco);border:1px solid var(--sigta-azul-texto-claro);border-radius:11px;padding:20px;display:flex;gap:14px}.stats small{color:var(--sigta-texto-suave)}.stats strong{font-size:27px;display:block;margin:3px 0}.stats p{font-size:11px;color:var(--sigta-texto-suave);margin:0}.dot{width:9px;height:9px;border-radius:50%;margin-top:5px}.blue{background:var(--sigta-azul)}.amber{background:var(--sigta-mostaza)}.red{background:var(--sigta-error)}.green{background:var(--sigta-azul-medio)}.columns{display:grid;grid-template-columns:2fr 1fr;gap:18px}.panel{background:var(--sigta-blanco);border:1px solid var(--sigta-azul-texto-claro);border-radius:11px;padding:22px}.panel-head{display:flex;justify-content:space-between;align-items:center;margin-bottom:15px}.panel-head h3{margin:4px 0;font-size:18px}.panel-head>button{border:0;background:none;color:var(--sigta-texto-suave);font-weight:700;cursor:pointer}.action-list article{display:flex;align-items:center;gap:13px;padding:15px 0;border-top:1px solid var(--sigta-azul-tenue)}.action-icon{width:36px;height:36px;border-radius:9px;color:var(--sigta-blanco);display:grid;place-items:center}.action-list strong,.action-list p{display:block;margin:0}.action-list p{font-size:12px;color:var(--sigta-texto-suave);margin-top:3px}.tag{margin-left:auto;background:var(--sigta-azul-tenue);color:var(--sigta-texto-suave);font-size:10px;padding:5px 8px;border-radius:12px}.quick>button{width:100%;border:1px solid var(--sigta-azul-texto-claro);background:var(--sigta-blanco);border-radius:9px;padding:12px;margin:7px 0;display:flex;text-align:left;align-items:center;gap:11px;cursor:pointer}.quick>button>span{background:var(--sigta-azul-tenue);color:var(--sigta-texto-suave);padding:10px 8px;border-radius:7px;font-weight:800;font-size:11px}.quick small,.quick strong{display:block}.quick small{color:var(--sigta-texto-suave);margin-top:3px}.quick b{margin-left:auto}.module-toolbar{display:flex;justify-content:space-between;gap:20px;margin-bottom:18px}.filters{display:flex;background:var(--sigta-azul-tenue);padding:4px;border-radius:9px}.filters button{border:0;background:none;padding:9px 14px;border-radius:7px;cursor:pointer;color:var(--sigta-texto-suave)}.filters button.active{background:var(--sigta-blanco);color:var(--sigta-azul);box-shadow:0 2px 7px #183d6220}.module-toolbar label{background:var(--sigta-blanco);border:1px solid var(--sigta-azul-texto-claro);border-radius:9px;padding:9px 13px;width:340px}.module-toolbar input{border:0;outline:0;width:90%;margin-left:7px}.ticket-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}.ticket{background:var(--sigta-blanco);border:1px solid var(--sigta-azul-texto-claro);border-radius:11px;padding:19px}.ticket-top{display:flex;justify-content:space-between}.code{color:var(--sigta-texto-suave);font-weight:800;font-size:12px}.priority{font-size:10px;background:var(--sigta-azul-tenue);padding:4px 8px;border-radius:10px}.priority.alta,.priority.crítica{background:var(--sigta-error-fondo);color:var(--sigta-error)}.ticket h3{font-size:17px;margin:15px 0 7px}.ticket>p{font-size:12px;color:var(--sigta-texto-suave);min-height:45px}.meta{border-top:1px solid var(--sigta-azul-tenue);border-bottom:1px solid var(--sigta-azul-tenue);display:grid;grid-template-columns:1fr 1fr;padding:12px 0;margin:14px 0;color:var(--sigta-texto-suave);font-size:10px}.meta b{color:var(--sigta-azul);font-size:11px}.ticket-actions{display:flex;gap:8px}.ticket-actions button{flex:1;border-radius:7px;padding:9px;border:1px solid var(--sigta-azul-texto-claro);cursor:pointer;font-weight:700}.primary{background:var(--sigta-texto-suave);color:var(--sigta-blanco);border-color:var(--sigta-texto-suave)!important}.secondary{background:var(--sigta-blanco);color:var(--sigta-texto-suave)}.empty{text-align:center;background:var(--sigta-blanco);border:1px dashed var(--sigta-azul-texto-claro);padding:70px;border-radius:12px;color:var(--sigta-texto-suave)}.empty span{font-size:35px;color:var(--sigta-exito)}.alert{background:var(--sigta-mostaza-suave);color:var(--sigta-mostaza-oscuro);padding:12px;border-radius:8px;margin-bottom:15px}@media(max-width:1050px){.stats{grid-template-columns:1fr 1fr}.columns{grid-template-columns:1fr}.ticket-grid{grid-template-columns:1fr 1fr}}@media(max-width:720px){.sidebar{position:static;width:100%}.workbench{display:block}main{margin:0;padding:20px}.stats,.ticket-grid{grid-template-columns:1fr}.module-toolbar,header{align-items:flex-start;flex-direction:column}.module-toolbar label{width:100%}}
</style>
