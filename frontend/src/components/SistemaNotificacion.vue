<template>
  <transition name="notificacion">
    <aside v-if="visible" :class="['notificacion', `notificacion--${tipo}`]" role="status" aria-live="polite">
      <span class="notificacion__icono" aria-hidden="true">{{ iconos[tipo] }}</span>
      <div class="notificacion__contenido">
        <strong>{{ titulo }}</strong>
        <p>{{ descripcion }}</p>
      </div>
      <button type="button" aria-label="Cerrar notificación" @click="cerrar">×</button>
    </aside>
  </transition>
</template>

<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'

const props = defineProps({
  tipo: { type: String, default: 'info' },
  titulo: { type: String, required: true },
  descripcion: { type: String, required: true },
  duracion: { type: Number, default: 6000 },
})
const emit = defineEmits(['close'])
const visible = ref(true)
const iconos = { exito: '✓', info: 'i', advertencia: '!', error: '×' }
let temporizador

function cerrar() {
  visible.value = false
  emit('close')
}

onMounted(() => {
  if (props.duracion > 0) temporizador = window.setTimeout(cerrar, props.duracion)
})
onBeforeUnmount(() => window.clearTimeout(temporizador))
</script>

<style scoped>
.notificacion{display:flex;align-items:flex-start;gap:12px;margin:16px 26px 0;padding:14px;border:1px solid;border-radius:10px;box-shadow:0 8px 24px #17324a1a}.notificacion__icono{display:grid;place-items:center;flex:0 0 28px;height:28px;border-radius:50%;font-weight:900}.notificacion__contenido{flex:1}.notificacion strong{display:block;margin-bottom:3px}.notificacion p{margin:0;line-height:1.4}.notificacion button{border:0;background:transparent;color:inherit;font-size:22px;cursor:pointer}.notificacion--exito{background:var(--sigta-exito-fondo);border-color:var(--sigta-exito);color:var(--sigta-exito)}.notificacion--error{background:var(--sigta-error-fondo);border-color:var(--sigta-error);color:var(--sigta-error)}.notificacion--info{background:var(--sigta-azul-tenue);border-color:var(--sigta-azul);color:var(--sigta-azul)}.notificacion--advertencia{background:var(--sigta-mostaza-suave);border-color:var(--sigta-mostaza);color:var(--sigta-mostaza-oscuro)}.notificacion-enter-active,.notificacion-leave-active{transition:.2s}.notificacion-enter-from,.notificacion-leave-to{opacity:0;transform:translateY(-6px)}
</style>
