<template>
  <ModalSia titulo="Validar requisitos de la solicitud" :ocupado="ocupado" @cerrar="$emit('cerrar')">
    <p><b>{{ registro.codigo }}</b> · {{ registro.titulo }}</p>
    <p>Revise los datos del solicitante antes de continuar.</p>
    <label v-for="r in requisitos" :key="r.campo" class="sia-check"><input v-model="revisados" type="checkbox" :value="r.campo" :disabled="!r.presente || ocupado"> {{ r.nombre }} <span>{{ r.presente ? 'Registrado' : 'Faltante' }}</span></label>
    <a v-if="registro.evidencia_archivo_url" :href="registro.evidencia_archivo_url" target="_blank" rel="noopener" class="sia-secondary">Ver evidencia ↗</a>
    <label class="sia-field">Motivo de rechazo<textarea v-model="motivo" rows="3" :disabled="ocupado" /></label>
    <p v-if="error" role="alert">{{ error }}</p>
    <template #acciones>
      <button class="sia-secondary" :disabled="ocupado" @click="$emit('cerrar')">Cancelar</button>
      <button class="sia-secondary" :disabled="ocupado || !motivo.trim()" @click="$emit('rechazar', motivo.trim())">Rechazar con motivo</button>
      <button class="sia-primary" :disabled="ocupado || revisados.length !== requisitos.length" @click="$emit('validar')">Validar y clasificar</button>
    </template>
  </ModalSia>
</template>
<script setup>
import { computed, ref } from 'vue'
import ModalSia from './ModalSia.vue'
const props = defineProps({ registro: Object, ocupado: Boolean, error: String })
defineEmits(['cerrar', 'validar', 'rechazar'])
const revisados = ref([])
const requisitos = computed(() => [
  { campo: 'titulo', nombre: 'Título' }, { campo: 'descripcion', nombre: 'Descripción' },
  { campo: 'ubicacion', nombre: 'Ubicación' }, { campo: 'evidencia', nombre: 'Evidencia' },
].map(r => ({ ...r, presente: r.campo === 'evidencia' ? !!(props.registro.evidencia_archivo_url || props.registro.evidencia_archivo || props.registro.evidencia?.trim()) : !!props.registro[r.campo]?.trim() && !(r.campo === 'ubicacion' && ['no especificado','sin especificar'].includes(props.registro.ubicacion.trim().toLowerCase())) })))
const faltantes = requisitos.value.filter(r => !r.presente).map(r => r.nombre.toLowerCase())
const motivo = ref(faltantes.length ? `Solicitud rechazada por falta de ${faltantes.join(', ')}.` : '')
</script>
