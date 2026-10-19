<template>
  <svg
    class="icono-sigta"
    :width="tamano"
    :height="tamano"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.7"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
  >
    <g v-html="trazo"></g>
  </svg>
</template>

<script setup>
import { computed } from 'vue'

/* =========================================================
   ICONOS DEL SISTEMA

   Un solo juego de iconos de trazo, en el color que herede
   del menú. Sustituyen a los emoji de colores, que rompían
   la paleta institucional y daban aspecto improvisado.
========================================================= */

const props = defineProps({
  nombre: { type: String, required: true },
  tamano: { type: [Number, String], default: 19 },
})

const TRAZOS = {
  panel: '<rect x="3" y="3" width="7" height="9" rx="1.5"/><rect x="14" y="3" width="7" height="5" rx="1.5"/><rect x="14" y="12" width="7" height="9" rx="1.5"/><rect x="3" y="16" width="7" height="5" rx="1.5"/>',
  inicio: '<path d="M3 10.5 12 3l9 7.5"/><path d="M5.5 9.5V20h13V9.5"/><path d="M9.5 20v-6h5v6"/>',
  solicitudes: '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8.5 8h7M8.5 12h7M8.5 16h4"/>',
  perfil: '<circle cx="12" cy="8" r="3.5"/><path d="M4.5 20c1.2-3.6 4-5.5 7.5-5.5s6.3 1.9 7.5 5.5"/>',
  configuracion: '<circle cx="12" cy="12" r="3"/><path d="M12 2v2.5M12 19.5V22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M2 12h2.5M19.5 12H22M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8"/>',
  usuarios: '<circle cx="9" cy="8" r="3.2"/><path d="M2.5 20c1-3.2 3.5-5 6.5-5s5.5 1.8 6.5 5"/><path d="M16.5 5.2a3.2 3.2 0 0 1 0 5.6M18 15.2c2 .7 3.3 2.3 3.9 4.8"/>',
  roles: '<rect x="4.5" y="10" width="15" height="10" rx="2"/><path d="M8 10V7a4 4 0 0 1 8 0v3"/><circle cx="12" cy="15" r="1.4"/>',
  auditoria: '<path d="M6 3h9l4 4v14a1 1 0 0 1-1 1H6a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1z"/><path d="M14.5 3v4.5H19"/><path d="M8.5 12.5h7M8.5 16.5h5"/>',
  compras: '<path d="M3 4h2.2l2.3 11.2a1.5 1.5 0 0 0 1.5 1.2h8.2a1.5 1.5 0 0 0 1.5-1.2L20.5 8H6"/><circle cx="9.5" cy="20" r="1.3"/><circle cx="17" cy="20" r="1.3"/>',
  almacen: '<path d="M3 9.5 12 4l9 5.5V20a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1z"/><path d="M8.5 21v-6.5h7V21"/>',
  soporte: '<rect x="2.5" y="4.5" width="19" height="12" rx="2"/><path d="M8.5 20.5h7M12 16.5v4"/>',
  mantenimiento: '<path d="M14.7 6.3a4.5 4.5 0 0 0 6 6l-2.6 2.6-6-6z"/><path d="M12.1 8.9 5 16a2.1 2.1 0 0 0 3 3l7.1-7.1"/>',
  tickets: '<path d="M3 8.5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2V10a2 2 0 0 0 0 4v1.5a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V14a2 2 0 0 0 0-4z"/><path d="M14 6.5v11"/>',
  portal: '<circle cx="12" cy="12" r="9"/><path d="M3.2 9.5h17.6M3.2 14.5h17.6"/><path d="M12 3c2.5 2.4 3.8 5.5 3.8 9s-1.3 6.6-3.8 9c-2.5-2.4-3.8-5.5-3.8-9S9.5 5.4 12 3z"/>',
  correo: '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3.5 6.5 12 13l8.5-6.5"/>',
  salir: '<path d="M9.5 20H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h3.5"/><path d="M15 8.5 19 12l-4 3.5"/><path d="M19 12H9.5"/>',
  notificaciones: '<path d="M6.5 10a5.5 5.5 0 0 1 11 0c0 4 1.5 5.5 1.5 5.5H5S6.5 14 6.5 10z"/><path d="M10 19a2.2 2.2 0 0 0 4 0"/>',
  buscar: '<circle cx="10.8" cy="10.8" r="6.2"/><path d="m16 16 4 4"/>',
  filtro: '<path d="M4 5h16l-6.5 7.4V19l-3 1v-7.6z"/>',
  editar: '<path d="M4 20h4.2L19.5 8.7a2.2 2.2 0 0 0-3.1-3.1L5.1 16.9z"/><path d="m14.8 7.2 2 2"/>',
  llave: '<circle cx="7.8" cy="15.8" r="3.2"/><path d="M10.1 13.5 20 3.6"/><path d="M15.5 8.1 18 10.6"/><path d="M13.2 10.4 15 12.2"/>',
  basura: '<path d="M4 7h16"/><path d="M9 7V4h6v3"/><path d="M6.5 7 7.4 20h9.2l.9-13"/><path d="M10 11v5M14 11v5"/>',
  mas: '<path d="M12 5v14M5 12h14"/>',
  reloj: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3.2 2"/>',
  usuario_check: '<circle cx="10" cy="8" r="3.4"/><path d="M3.5 20c1.1-3.4 3.6-5.2 6.5-5.2 1.6 0 3 .5 4.1 1.4"/><path d="m15.5 18.2 2 2 4-4.2"/>',
  usuario_x: '<circle cx="10" cy="8" r="3.4"/><path d="M3.5 20c1.1-3.4 3.6-5.2 6.5-5.2 1.5 0 2.8.4 3.9 1.2"/><path d="m16.2 16.2 4 4M20.2 16.2l-4 4"/>',
  historial: '<path d="M3.5 12a8.5 8.5 0 1 0 2.6-6.1"/><path d="M3 4v4.5h4.5"/><path d="M12 7.5V12l3 1.8"/>',
  actividades: '<rect x="5" y="3.5" width="14" height="17" rx="2"/><path d="M9 3.5h6v2.5H9z"/><path d="M9 11l2 2 4-4"/><path d="M9 16.5h6"/>',
  validar: '<circle cx="12" cy="12" r="9"/><path d="M8 12.3l2.7 2.7L16.5 9"/>',
  conformidad: '<path d="M12 3.2l1.8 1.4 2.3-.5.9 2.1 2.1.9-.5 2.3 1.4 1.8-1.4 1.8.5 2.3-2.1.9-.9 2.1-2.3-.5L12 20.8l-1.8-1.4-2.3.5-.9-2.1-2.1-.9.5-2.3L3.8 12l1.4-1.8-.5-2.3 2.1-.9.9-2.1 2.3.5z"/><path d="M9 12.2l2 2 4-4.2"/>',
  reporte: '<rect x="3.5" y="3.5" width="17" height="17" rx="2"/><path d="M8 15.5V11M12 15.5V8M16 15.5v-4.5"/>',
  edificio: '<path d="M3 21h18"/><path d="M5 21V6l7-3 7 3v15"/><path d="M9.5 9h.01M14.5 9h.01M9.5 13h.01M14.5 13h.01"/><path d="M10 21v-4h4v4"/>',
  escudo: '<path d="M12 3l7 3v5c0 4.5-2.9 8.3-7 9.6C7.9 19.3 5 15.5 5 11V6z"/>',
  corona: '<path d="M4 8l3.5 3L12 5l4.5 6L20 8l-1.6 10H5.6z"/><path d="M5.6 20h12.8"/>',
  globo: '<circle cx="12" cy="12" r="9"/><path d="M3.5 9h17M3.5 15h17"/><path d="M12 3c2.6 2.4 4 5.6 4 9s-1.4 6.6-4 9c-2.6-2.4-4-5.6-4-9s1.4-6.6 4-9z"/>',
  alerta: '<path d="M12 3.8 21.2 20H2.8z"/><path d="M12 10v4.5"/><path d="M12 17.6h.01"/>',
  error: '<circle cx="12" cy="12" r="9"/><path d="M9 9l6 6M15 9l-6 6"/>',
  evento: '<rect x="3.5" y="4.5" width="17" height="16" rx="2"/><path d="M3.5 9.5h17"/><path d="M8 3v3M16 3v3"/><path d="M8 13.5h4"/>',
  etiqueta: '<path d="M12.6 3.5H20v7.4L11.4 19.5a1.5 1.5 0 0 1-2.1 0L4 14.2a1.5 1.5 0 0 1 0-2.1z"/><circle cx="16.2" cy="7.3" r="1.3"/>',
}

const trazo = computed(() => TRAZOS[props.nombre] || TRAZOS.panel)
</script>

<style scoped>
.icono-sigta {
  flex-shrink: 0;
  display: block;
}
</style>
