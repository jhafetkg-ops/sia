<template>
  <section class="request-records">
    <p v-if="cargando" role="status">Consultando documentos...</p>
    <button v-if="error" class="sia-secondary" :disabled="cargando" @click="cargar">Volver a consultar</button>
    <p v-if="error" role="alert">{{ error }}</p>
    <p v-if="consultado && !documentos.length">No hay documentos generados para este expediente.</p>
    <p v-for="d in documentos" :key="d.id"><button class="sia-secondary" @click="seleccionado=d">{{ d.tipo }} · {{ new Date(d.creado_en).toLocaleString('es-BO') }}</button></p>
    <ModalSia v-if="seleccionado" :titulo="seleccionado.tipo" @cerrar="seleccionado=null">
      <article ref="documento" class="sia-documento">
        <header><h2>{{ institucion }}</h2><p>SIA · {{ seleccionado.tipo }}</p></header>
        <p>Documento {{ seleccionado.id }} · {{ seleccionado.codigo_expediente }}</p>
        <dl><template v-for="(valor,nombre) in seleccionado.contenido" :key="nombre"><dt>{{ nombre }}</dt><dd>{{ valor }}</dd></template></dl>
        <svg v-if="seleccionado.firma.length" viewBox="0 0 600 200" aria-label="Firma manuscrita registrada"><polyline v-for="(trazo,i) in seleccionado.firma" :key="i" :points="trazo.map(p=>p.join(',')).join(' ')" fill="none" stroke="#123a6b" stroke-width="2.5" /></svg>
        <p>{{ seleccionado.firma.length ? 'Firmado por' : 'Emitido por' }}: {{ seleccionado.nombre_firmante }} · {{ seleccionado.roles_firmante.join(', ') }}</p>
        <p>{{ new Date(seleccionado.creado_en).toLocaleString('es-BO') }}</p>
      </article>
      <template #acciones><button class="sia-secondary" @click="seleccionado=null">Cerrar</button><button class="sia-secondary" @click="imprimir">Imprimir</button><button class="sia-primary" :disabled="cargando" @click="descargarPdf">{{ seleccionado.firma.length ? 'Descargar PDF firmado' : 'Descargar PDF' }}</button></template>
    </ModalSia>
  </section>
</template>
<script setup>
import { ref, watch } from 'vue'
import ModalSia from './ModalSia.vue'
const props=defineProps({ base: String, id: [Number,String], institucion: {type:String,default:import.meta.env.VITE_INSTITUCION || 'SIA'} })
const documentos=ref([]), seleccionado=ref(null), cargando=ref(false), consultado=ref(false), error=ref(''), documento=ref(null)
watch(()=>[props.base,props.id],()=>{documentos.value=[];seleccionado.value=null;consultado.value=false;error.value='';cargar()},{immediate:true})
async function cargar(){cargando.value=true;error.value='';try{const r=await fetch(`${props.base}/${props.id}/documentos/`,{headers:{Authorization:`Token ${localStorage.getItem('sigta_token')}`}});if(!r.ok)throw new Error('No fue posible consultar los documentos.');documentos.value=await r.json();consultado.value=true}catch(e){error.value=e.message}finally{cargando.value=false}}
async function descargarPdf(){cargando.value=true;error.value='';try{const r=await fetch(`${props.base}/${props.id}/documentos/${seleccionado.value.id}/pdf/`,{headers:{Authorization:`Token ${localStorage.getItem('sigta_token')}`}});if(!r.ok)throw new Error('No se pudo descargar el PDF.');const url=URL.createObjectURL(await r.blob());const a=document.createElement('a');a.href=url;a.download=`documento-sia-${seleccionado.value.id}.pdf`;a.click();setTimeout(()=>URL.revokeObjectURL(url),60000)}catch(e){error.value=e.message}finally{cargando.value=false}}
function imprimir(){const w=window.open('','_blank');if(!w){error.value='Permita abrir la ventana de impresión.';return}w.opener=null;w.document.write('<!doctype html><html><head><meta charset="utf-8"><title>Documento SIA</title><style>body{font:14px Arial;color:#123a6b;margin:40px}header{border-bottom:4px solid #c79a1e}dt{font-weight:bold;margin-top:14px}dd{margin:4px 0;white-space:pre-wrap}svg{width:300px}article{max-width:750px;margin:auto}</style></head><body></body></html>');w.document.body.appendChild(documento.value.cloneNode(true));w.document.close();w.focus();w.print()}
</script>
<style scoped>
.request-records > p { margin: 10px 0; color: var(--sigta-texto-suave); font-size: 13px; }
.request-records > p > button { width: 100%; padding: 12px 14px; border: 1px solid #dce5ef; border-radius: 9px; background: white; color: var(--sigta-azul); text-align: left; cursor: pointer; }
.request-records > p > button:hover { border-color: var(--sigta-azul); }
.request-records > p > button:focus-visible { outline: 2px solid var(--sigta-azul); outline-offset: 3px; }
.sia-documento header {border-bottom:4px solid var(--sigta-mostaza);}.sia-documento dt {font-weight:700;margin-top:14px;}.sia-documento dd {margin:4px 0;white-space:pre-wrap;}.sia-documento svg {width:min(300px,100%);}</style>
