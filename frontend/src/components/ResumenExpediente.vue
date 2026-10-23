<template>
  <section class="sia-summary">
    <header><div><small>{{ registro.codigo }}</small><h3>{{ requerimiento ? 'Datos del requerimiento' : registro.titulo }}</h3><strong v-if="requerimiento">{{ registro.titulo }}</strong></div><b>{{ registro.estado_nombre || registro.estado }}</b></header>
    <dl><div v-for="[nombre, valor] in datos" :key="nombre"><dt>{{ nombre }}</dt><dd>{{ valor || 'Sin registro' }}</dd></div></dl>
    <p>{{ registro.descripcion }}</p>
    <a v-if="registro.evidencia_archivo_url" :href="registro.evidencia_archivo_url" target="_blank" rel="noopener" class="sia-secondary">Ver evidencia ↗</a>
    <slot />
  </section>
</template>
<script setup>
import { computed } from 'vue'
const props = defineProps({ registro: Object, requerimiento: Boolean })
const datos = computed(() => {
  const r = props.registro
  if (props.requerimiento) return [['Solicitante', r.solicitante_nombre], ['Área solicitante', r.area_nombre || r.area], ['Fecha', r.creado_en ? new Date(r.creado_en).toLocaleString('es-BO') : ''], ['Tipo', r.tipo_nombre || r.tipo], ['Cantidad', r.cantidad], ['Monto estimado', r.monto_estimado ? `Bs. ${Number(r.monto_estimado).toFixed(2)}` : ''], ['Especificaciones', r.especificaciones], ['Justificación', r.justificacion]]
  return [['Solicitante', r.solicitante_nombre], ['Fecha', r.creado_en ? new Date(r.creado_en).toLocaleString('es-BO') : ''], ['Tipo', r.tipo_nombre || r.tipo], ['Prioridad', r.prioridad_jefatura || r.prioridad], ['Responsable', r.auxiliar_asignado_nombre || r.tecnico_nombre || r.responsable_actual], ['Ubicación', r.ubicacion]]
})
</script>
