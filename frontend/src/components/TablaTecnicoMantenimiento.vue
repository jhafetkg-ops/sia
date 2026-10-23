<template>
  <section class="tm-tabla">
    <label>Buscar requerimientos<input v-model="busqueda" type="search" placeholder="Código, título, solicitante o ubicación"></label>
    <div class="tm-titulo"><h2>{{ titulo }}</h2><span>{{ filtrados.length }} registros</span></div>
    <div class="tm-scroll"><table><thead><tr><th>Código</th><th>Requerimiento</th><th>Solicitante</th><th>Estado</th><th>Acciones</th></tr></thead><tbody>
      <tr v-for="r in filtrados" :key="r.id"><td><strong>{{ r.codigo }}</strong></td><td>{{ r.titulo }}<small>{{ r.producto_requerido || r.ubicacion || r.equipo_afectado || 'Sin ubicación registrada' }}</small></td><td>{{ r.solicitante_nombre || 'Sin registro' }}</td><td><span class="tm-estado">{{ r.estado_nombre || r.estado_codigo || 'Sin registro' }}</span></td><td><div class="tm-acciones"><slot name="acciones" :registro="r"><button @click="$emit('ver',r)">Ver detalles</button></slot></div></td></tr>
      <tr v-if="!filtrados.length"><td colspan="5" class="tm-vacio">{{ busqueda ? 'No se encontraron coincidencias.' : 'No hay requerimientos en esta bandeja.' }}</td></tr>
    </tbody></table></div>
  </section>
</template>
<script setup>
import { computed, ref } from 'vue'
const props=defineProps({ registros:{type:Array,default:()=>[]}, titulo:String })
defineEmits(['ver'])
const busqueda=ref('')
const filtrados=computed(()=>props.registros.filter(r=>[r.codigo,r.titulo,r.solicitante_nombre,r.ubicacion,r.producto_requerido].some(v=>String(v||'').toLowerCase().includes(busqueda.value.trim().toLowerCase()))))
</script>
<style scoped>
.tm-tabla{padding:24px;background:white;border:1px solid #d7e3f2;border-radius:12px;margin-top:16px;color:var(--sigta-texto)}label{display:block;font-size:13px;font-weight:700}input{display:block;width:100%;box-sizing:border-box;padding:14px;margin-top:8px;border:1px solid #d7e3f2;border-radius:8px;background:#f8fafd;font:inherit;font-weight:400}.tm-titulo{display:flex;justify-content:space-between;align-items:center;gap:12px;margin:24px 0 18px}.tm-titulo h2{font-size:18px;margin:0;color:var(--sigta-azul)}.tm-titulo>span{font-size:12px;color:#607795}.tm-scroll{overflow-x:auto}table{width:100%;border-collapse:collapse;text-align:left;font-size:13px}th{padding:14px;background:#f1f6fc;font-size:11px;text-transform:uppercase;color:#607795}td{padding:17px 14px;border-bottom:1px solid #e5ecf5;vertical-align:middle}td strong{white-space:nowrap;color:var(--sigta-azul)}td:nth-child(2){min-width:180px;overflow-wrap:anywhere}small{display:block;margin-top:6px;font-size:12px;color:#607795}.tm-estado{display:inline-block;padding:7px 10px;border-radius:7px;font-size:11px;font-weight:700;line-height:1.5;background:#eaf1fa;color:var(--sigta-azul)}.tm-acciones{display:flex;gap:8px;flex-wrap:wrap}.tm-acciones :deep(button){padding:9px 13px;border:1px solid var(--sigta-azul);border-radius:7px;background:var(--sigta-azul);color:white;font:inherit;font-weight:700;cursor:pointer;white-space:nowrap}.tm-acciones :deep(button.secundario){background:white;color:var(--sigta-azul)}.tm-vacio{padding:32px;text-align:center;color:#607795}@media(max-width:650px){.tm-tabla{padding:16px}}
</style>
