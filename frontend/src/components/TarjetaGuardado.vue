<template>
  <transition name="tg-fade">
    <div v-if="visible" class="tg-overlay" @click.self="$emit('cerrar')">
      <div class="tg-card">
        <div :class="['tg-check', { 'tg-check--error': tipo === 'error' }]" aria-hidden="true">
          <IconoSigta :nombre="tipo === 'error' ? 'error' : 'validar'" :tamano="42" />
        </div>
        <p>{{ texto }}</p>
        <button type="button" class="tg-aceptar" @click="$emit('cerrar')">Aceptar</button>
      </div>
    </div>
  </transition>
</template>

<script setup>
import IconoSigta from './IconoSigta.vue'

defineProps({
  visible: { type: Boolean, default: false },
  texto: { type: String, default: 'Cambios guardados' },
  tipo: { type: String, default: 'exito' },
})

defineEmits(['cerrar'])
</script>

<style scoped>
.tg-overlay {
  position: fixed;
  inset: 0;
  z-index: 1400;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(7, 35, 60, .55);
}

.tg-card {
  position: relative;
  width: 300px;
  min-height: 210px;
  padding: 30px 14px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 18px;
  border-radius: 12px;
  background: var(--sigta-azul);
  box-shadow: 0 26px 60px rgba(18, 58, 107, .2);
  transform-origin: center;
  animation: tg-in .72s cubic-bezier(.25, .9, .3, 1) both;
}

@keyframes tg-in {
  0%   { transform: scale(0, 0); }
  22%  { transform: scale(1.22, .78); }
  40%  { transform: scale(.84, 1.16); }
  56%  { transform: scale(1.09, .91); }
  72%  { transform: scale(.95, 1.05); }
  86%  { transform: scale(1.03, .97); }
  100% { transform: scale(1, 1); }
}

.tg-check {
  width: 74px;
  height: 74px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: #e3f7ec;
  color: #17a34a;
  animation: tg-check .55s cubic-bezier(.2, 1.7, .35, 1) .2s both;
}

.tg-check--error {
  background: #fde3e3;
  color: #dc2626;
}

@keyframes tg-check {
  0%   { transform: scale(0); }
  55%  { transform: scale(1.18); }
  100% { transform: scale(1); }
}

.tg-card p {
  margin: 0;
  padding: 0 16px;
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  letter-spacing: .3px;
  text-align: center;
}

.tg-aceptar {
  padding: 10px 34px;
  border: none;
  border-radius: 999px;
  background: #fff;
  color: var(--sigta-azul);
  font-size: 14px;
  font-weight: 800;
  cursor: pointer;
  transition: transform .15s, box-shadow .15s;
}

.tg-aceptar:hover {
  transform: translateY(-1px);
  box-shadow: 0 6px 16px rgba(0, 0, 0, .2);
}

.tg-fade-enter-active { transition: opacity .2s ease; }
.tg-fade-leave-active { transition: opacity .25s ease; }
.tg-fade-enter-from,
.tg-fade-leave-to { opacity: 0; }

@media (prefers-reduced-motion: reduce) {
  .tg-card,
  .tg-check {
    animation: none;
  }
}
</style>
