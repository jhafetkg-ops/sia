<template>
  <div>
    <p>Dibuje su firma con mouse o pantalla táctil. Confirme únicamente para este documento.</p>
    <svg ref="superficie" class="sia-firma" viewBox="0 0 600 200" role="img" aria-label="Área para dibujar la firma" @pointerdown="iniciar" @pointermove="mover" @pointerup="terminar" @pointercancel="terminar">
      <polyline v-for="(trazo,i) in trazos" :key="i" :points="trazo.map(p => p.join(',')).join(' ')" fill="none" stroke="#123a6b" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" />
    </svg>
    <button class="sia-secondary" type="button" @click="limpiar">Limpiar / volver a firmar</button>
  </div>
</template>
<script setup>
import { ref } from 'vue'
const emit = defineEmits(['update:modelValue'])
const superficie = ref(null), trazos = ref([])
let activo = null
function punto(e) { const r = superficie.value.getBoundingClientRect(); return [Math.max(0,Math.min(600,(e.clientX-r.left)*600/r.width)),Math.max(0,Math.min(200,(e.clientY-r.top)*200/r.height))] }
function iniciar(e) { if (activo !== null || e.button !== 0) return; e.preventDefault(); activo=e.pointerId; superficie.value.setPointerCapture(activo); trazos.value.push([punto(e)]) }
function mover(e) { if(activo!==e.pointerId)return; const t=trazos.value.at(-1); if(t.length<2000)t.push(punto(e)); emit('update:modelValue',trazos.value.map(t=>t.map(p=>[...p]))) }
function terminar(e) { if(activo!==e.pointerId)return; activo=null; if(trazos.value.at(-1)?.length<2)trazos.value.pop(); emit('update:modelValue',trazos.value.map(t=>t.map(p=>[...p]))) }
function limpiar() { trazos.value=[]; activo=null; emit('update:modelValue',[]) }
</script>
<style scoped>.sia-firma { display:block; width:100%; height:auto; background:white; border:2px solid var(--sigta-azul); border-radius:8px; touch-action:none; margin:14px 0; }</style>
