<template>
  <section class="it-informes"><h3>Informes del requerimiento</h3><p v-if="cargando" role="status">Consultando informes…</p><p v-if="error" role="alert">{{ error }}</p><div v-for="d in informes" :key="d.id" class="it-informe"><IconoSigta nombre="reporte" :tamano="24"/><div><strong>{{ d.tipo }}</strong><small>{{ d.nombre_firmante }} · {{ new Date(d.creado_en).toLocaleDateString('es-BO') }}</small></div><button class="sia-primary" @click="$emit('ver', `/api/mantenimiento/requerimientos/${id}/documentos/${d.id}/pdf/`, d.tipo)">Ver informe</button></div><p v-if="!cargando && !error && !informes.length">Todavía no hay informes generados para este requerimiento.</p></section>
</template>
<script setup>
import { ref, watch } from 'vue'
import IconoSigta from './IconoSigta.vue'
const props=defineProps({id:[Number,String]})
defineEmits(['ver'])
const informes=ref([]),cargando=ref(false),error=ref('')
let consulta=0
watch(()=>props.id,async id=>{const actual=++consulta;informes.value=[];cargando.value=true;error.value='';try{const r=await fetch(`/api/mantenimiento/requerimientos/${id}/documentos/`,{headers:{Authorization:`Token ${localStorage.getItem('sigta_token')}`}});if(!r.ok)throw new Error('No se pudieron consultar los informes.');const datos=await r.json();if(actual===consulta)informes.value=datos.filter(d=>/informe/i.test(d.tipo))}catch(e){if(actual===consulta)error.value=e.message}finally{if(actual===consulta)cargando.value=false}},{immediate:true})
</script>
<style scoped>
.it-informes{padding:22px;border:1px solid #d7e3f2;border-radius:12px;background:#fff}.it-informes h3{margin:0 0 18px;font-size:17px;color:var(--sigta-azul)}.it-informes p{font-size:13px;color:#607795}.it-informe{display:flex;align-items:center;gap:14px;padding:16px;background:#f4f8fd;border:1px solid #dce6f2;border-radius:9px;margin-top:12px;color:var(--sigta-azul)}.it-informe>div{flex:1;min-width:0}.it-informe strong,.it-informe small{display:block}.it-informe strong{font-size:14px}.it-informe small{font-size:12px;color:#607795;margin-top:6px}@media(max-width:650px){.it-informe{flex-wrap:wrap}}
</style>
