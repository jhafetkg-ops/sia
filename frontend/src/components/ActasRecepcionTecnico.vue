<template>
  <section class="actas-receptor">
    <h3>Acta de entrega del producto</h3>
    <p v-if="cargando" role="status">Consultando actas...</p>
    <p v-if="error" role="alert">{{ error }}</p>
    <button v-if="error" class="sia-secondary" @click="cargar">Volver a consultar</button>
    <p v-if="!cargando && !actas.length && !error">El acta se elabora al entregar el producto en almacén.</p>
    <article v-for="acta in actas" :key="acta.id">
      <div><strong>{{ acta.confirmado_en ? 'Entrega con acta firmada' : 'Acta para firma en la entrega' }}</strong><p>Entrega: {{ acta.datos.entrega }}<br>Recibe: {{ acta.datos.recibe }}</p></div>
      <div class="actas-receptor-acciones"><button class="sia-secondary" @click="abrir(acta.original_url, 'Acta original')">Ver acta original</button><button v-if="acta.firmado_url" class="sia-primary" @click="abrir(acta.firmado_url, 'Acta firmada')">Ver acta firmada</button></div>
    </article>
    <ModalSia v-if="visor" :titulo="visor.nombre" amplio @cerrar="cerrar"><p v-if="visor.cargando" role="status">Abriendo acta...</p><template v-if="visor.url"><iframe :src="visor.url" :title="visor.nombre" /><a :href="visor.url" download="acta-entrega.pdf" class="sia-secondary">Descargar acta PDF</a></template></ModalSia>
  </section>
</template>
<script setup>
import { onUnmounted, ref, watch } from 'vue'
import ModalSia from './ModalSia.vue'
const props = defineProps({ compraId: { type: [String, Number], required: true } })
const actas = ref([]), cargando = ref(false), error = ref(''), visor = ref(null)
let consulta = 0, consultaVisor = 0
const headers = () => ({ Authorization: `Token ${localStorage.getItem('sigta_token')}` })
async function cargar() {
  const actual = ++consulta
  cargando.value = true; error.value = ''; actas.value = []
  try {
    const r = await fetch(`/api/compras/solicitudes/${props.compraId}/actas-almacen/`, { headers: headers() })
    if (!r.ok) throw new Error('No fue posible consultar las actas de entrega.')
    const datos = await r.json()
    if (actual === consulta) actas.value = datos
  } catch (e) { if (actual === consulta) error.value = e.message } finally { if (actual === consulta) cargando.value = false }
}
function cerrar() { consultaVisor++; if (visor.value?.url) URL.revokeObjectURL(visor.value.url); visor.value = null }
async function abrir(url, nombre) {
  cerrar(); const actual = consultaVisor
  visor.value = { nombre, cargando: true }; error.value = ''
  try {
    const r = await fetch(url, { headers: headers(), cache: 'no-store' })
    if (!r.ok) throw new Error('No fue posible abrir el acta.')
    const blob = await r.blob()
    if (actual === consultaVisor) visor.value = { nombre, cargando: false, url: URL.createObjectURL(blob) }
  } catch (e) { if (actual === consultaVisor) { cerrar(); error.value = e.message } }
}
watch(() => props.compraId, () => { cerrar(); cargar() }, { immediate: true })
onUnmounted(() => { consulta++; cerrar() })
</script>
<style scoped>
.actas-receptor{padding:18px;border:1px solid #dbe5f0;border-radius:10px;background:#f7faff;margin:16px 0}.actas-receptor h3{margin:0 0 12px;font-size:16px;color:var(--sigta-azul)}.actas-receptor p{font-size:13px;line-height:1.6;color:#526a82}.actas-receptor article{padding:14px;border:1px solid #dbe5f0;border-radius:8px;background:white;margin-top:10px}.actas-receptor-acciones{display:flex;flex-wrap:wrap;gap:8px}iframe{width:100%;height:65vh;border:0;margin-bottom:12px}
</style>
