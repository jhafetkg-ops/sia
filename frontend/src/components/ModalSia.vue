<template>
  <Teleport to="body">
    <div class="sia-modal-backdrop" @keydown.esc="cerrar">
      <section ref="panel" class="sia-modal" :class="{ 'sia-modal-amplio': amplio }" role="dialog" aria-modal="true" :aria-labelledby="id" tabindex="-1" @keydown.tab="enfocar">
        <header class="sia-modal-head"><h2 :id="id">{{ titulo }}</h2><button type="button" aria-label="Cerrar" :disabled="ocupado" @click="cerrar">×</button></header>
        <div class="sia-modal-body"><slot /></div>
        <footer v-if="$slots.acciones" class="sia-modal-actions"><slot name="acciones" /></footer>
      </section>
    </div>
  </Teleport>
</template>
<script setup>
import { onMounted, onUnmounted, ref, useId } from 'vue'
const props = defineProps({ titulo: String, ocupado: Boolean, amplio: Boolean })
const emit = defineEmits(['cerrar'])
const panel = ref(null), id = useId()
let anterior, overflow
function cerrar() { if (!props.ocupado) emit('cerrar') }
function enfocar(event) {
  const nodos = [...panel.value.querySelectorAll('button:not(:disabled), input:not(:disabled), textarea:not(:disabled), select:not(:disabled), a[href], [tabindex="0"]')]
  if (!nodos.length) { event.preventDefault(); return }
  const primero = nodos[0], ultimo = nodos.at(-1)
  if (event.shiftKey && [primero, panel.value].includes(document.activeElement)) { event.preventDefault(); ultimo.focus() }
  else if (!event.shiftKey && [ultimo, panel.value].includes(document.activeElement)) { event.preventDefault(); primero.focus() }
}
onMounted(() => { anterior = document.activeElement; overflow = document.body.style.overflow; document.body.style.overflow = 'hidden'; panel.value.focus() })
onUnmounted(() => { document.body.style.overflow = overflow; anterior?.focus() })
</script>
<style scoped>
.sia-modal-amplio { width:min(1080px,100%); overflow:hidden; display:flex; flex-direction:column; }
.sia-modal-amplio .sia-modal-head { flex-shrink:0; }
.sia-modal-amplio .sia-modal-body { overflow-y:auto; min-height:0; }
</style>
