<template>
  <ModalSia v-if="pendiente" :titulo="pendiente.titulo" @cerrar="terminar(null)">
    <p><b>Expediente:</b> {{ pendiente.expediente }}</p>
    <p>Esta firma manuscrita se asociará al documento con su usuario, rol y fecha.</p>
    <FirmaManuscrita :key="pendiente.expediente" v-model="firma" />
    <template #acciones><button class="sia-secondary" @click="terminar(null)">Cancelar</button><button class="sia-primary" :disabled="!firma.length" @click="terminar(firma)">Confirmar firma</button></template>
  </ModalSia>
</template>
<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import ModalSia from './ModalSia.vue'
import FirmaManuscrita from './FirmaManuscrita.vue'
const pendiente=ref(null), firma=ref([])
function abrir(e) { if(pendiente.value){e.detail.resolve(null);return} firma.value=[];pendiente.value=e.detail }
function terminar(valor) { pendiente.value?.resolve(valor); pendiente.value=null; firma.value=[] }
onMounted(()=>window.addEventListener('sia-firma',abrir))
onUnmounted(()=>{window.removeEventListener('sia-firma',abrir); terminar(null)})
</script>
