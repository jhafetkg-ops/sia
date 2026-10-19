<template>
  <section class="tes-tabla-card">
    <div class="tes-tabla-head"><h2>{{ historial ? 'Desembolsos registrados' : 'Desembolsos pendientes' }}</h2><span>{{ registros.length }} {{ historial ? 'registros' : 'por desembolsar' }}</span></div>
    <label class="tes-buscar">Buscar expediente<input v-model="busqueda" type="search" placeholder="Buscar por código, requerimiento, solicitante o responsable…"></label>
    <p v-if="cargando" class="tes-vacio" role="status">Consultando expedientes…</p>
    <div v-else class="tes-scroll">
      <table><thead><tr><th>Código</th><th>Requerimiento</th><th>{{ historial ? 'Recibe los fondos' : 'Solicitante / área' }}</th><th>Monto (Bs.)</th><th>{{ historial ? 'Método' : 'Estado' }}</th><th>Acción</th></tr></thead>
        <tbody><tr v-for="e in filtrados" :key="e.id"><td><strong>{{ e.codigo }}</strong></td><td>{{ e.titulo }}</td><td>{{ historial ? e.responsable_adquisicion || 'Sin registro' : e.solicitante_nombre }}<small>{{ e.area_nombre }}</small></td><td class="monto">{{ Number(historial ? e.monto_desembolsado : e.monto_estimado || 0).toLocaleString('es-BO', { minimumFractionDigits: 2 }) }}</td><td><span class="estado">{{ historial ? e.tipo_desembolso || 'Sin registro' : 'Autorizado' }}</span></td><td><button type="button" @click="$emit('ver', e)">Ver</button></td></tr>
          <tr v-if="!filtrados.length"><td colspan="6" class="tes-vacio">{{ busqueda ? 'No se encontraron expedientes con esa búsqueda.' : historial ? 'Todavía no hay desembolsos registrados.' : 'No hay expedientes pendientes de desembolso.' }}</td></tr>
        </tbody>
      </table>
    </div>
  </section>
</template>
<script setup>
import { computed, ref } from 'vue'
const props = defineProps({ registros: { type: Array, default: () => [] }, cargando: Boolean, historial: Boolean })
defineEmits(['ver'])
const busqueda = ref('')
const filtrados = computed(() => {
  const texto = busqueda.value.trim().toLocaleLowerCase('es')
  return props.registros.filter(e => !texto || [e.codigo, e.titulo, e.solicitante_nombre, e.responsable_adquisicion, e.area_nombre].some(v => String(v || '').toLocaleLowerCase('es').includes(texto)))
})
</script>
<style scoped>
.tes-tabla-card{padding:24px;background:#fff;border:1px solid var(--sigta-borde);border-radius:12px;margin-top:22px;color:var(--sigta-texto)}.tes-tabla-head{display:flex;align-items:center;justify-content:space-between;gap:14px;margin-bottom:20px}.tes-tabla-head h2{margin:0;font-size:18px;color:var(--sigta-azul)}.tes-tabla-head span{background:#fff5d4;color:#765a00;padding:8px 12px;border-radius:18px;font-size:12px;font-weight:700;white-space:nowrap}.tes-buscar{display:block;font-weight:700;font-size:12px;margin-bottom:22px}.tes-buscar input{display:block;box-sizing:border-box;width:100%;padding:15px;margin-top:8px;border:1px solid var(--sigta-borde);border-radius:8px;font:inherit;font-weight:400;background:#f8fafd}.tes-buscar input:focus-visible{outline:2px solid var(--sigta-azul);outline-offset:2px}.tes-scroll{overflow:auto}table{width:100%;border-collapse:collapse;text-align:left;font-size:13px}th{padding:14px;background:#f3f7fc;color:var(--sigta-texto-suave);text-transform:uppercase;font-size:11px;letter-spacing:.4px}td{padding:17px 14px;border-bottom:1px solid #e6edf5;vertical-align:middle}td strong{color:var(--sigta-azul);white-space:nowrap}td small{display:block;color:var(--sigta-texto-suave);margin-top:5px}tbody tr:hover{background:#fafcff}.monto{white-space:nowrap;font-variant-numeric:tabular-nums}.estado{display:inline-block;background:#edf4fc;color:var(--sigta-azul);border-radius:15px;padding:6px 10px;font-size:11px;white-space:nowrap}button{border:0;background:var(--sigta-azul);color:white;border-radius:7px;padding:9px 20px;font:inherit;font-weight:700;cursor:pointer}.tes-vacio{padding:30px;text-align:center;color:var(--sigta-texto-suave)}@media(max-width:720px){.tes-tabla-card{padding:16px}.tes-tabla-head{align-items:flex-start}.tes-tabla-head h2{font-size:16px}}
</style>
