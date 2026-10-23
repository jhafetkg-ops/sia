<template>
  <Teleport to="body">
  <transition name="lm">
    <div
      v-if="visible"
      class="lm-overlay"
      role="dialog"
      aria-modal="true"
      :aria-label="fase === 'despedida' ? 'Cerrando sesión' : 'Confirmar cierre de sesión'"
      @click.self="onCancelar"
    >
      <div class="lm-card" :class="fase">

        <!-- FIGURA -->
        <div class="lm-figura" :class="fase">
          <img
            v-if="modoFigura === 'frames'"
            :src="frames[frameActual]"
            alt=""
            aria-hidden="true"
          />
          <img
            v-else-if="modoFigura === 'unico'"
            :src="rutaSoldadoUnico"
            alt=""
            aria-hidden="true"
          />
          <span v-else class="lm-figura-fallback" aria-hidden="true">
            <IconoSigta nombre="salir" :tamano="46" />
          </span>
        </div>

        <!-- ESTADO 2: CONFIRMACIÓN -->
        <template v-if="fase === 'confirmacion'">
          <h2>¿Cerrar sesión?</h2>
          <p>Estás a punto de salir de SIA. ¿Deseas continuar?</p>

          <div class="lm-acciones">
            <button type="button" class="lm-btn lm-cancelar" @click="onCancelar">
              Cancelar
            </button>
            <button type="button" class="lm-btn lm-confirmar" @click="onConfirmar">
              Cerrar sesión
            </button>
          </div>
        </template>

        <!-- ESTADO 3: DESPEDIDA -->
        <template v-else>
          <h2>¡Hasta pronto!</h2>
          <p>Cerrando sesión de forma segura…</p>
          <div class="lm-puntos" aria-hidden="true">
            <span></span><span></span><span></span>
          </div>
        </template>

      </div>
    </div>
  </transition>
  </Teleport>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import IconoSigta from './IconoSigta.vue'

const props = defineProps({
  visible: { type: Boolean, default: false },
})

const emit = defineEmits(['cancelar', 'confirmar'])

const DURACION_DESPEDIDA = 1750

/* Se sirven desde /public (enlace en runtime para no romper el build
   si aún no se agregaron los archivos). Cadena de respaldo:
   6 frames del saludo  ->  1 PNG único  ->  ícono. */
const frames = Array.from({ length: 6 }, (_, i) => `/img/animacion${i + 1}.png`)
const rutaSoldadoUnico = '/img/soldado-saludo.png'

/* Secuencia del saludo: descanso(1) -> sube(2) -> saludo firme(3-4)
   -> baja(5) -> descanso(6). Tiempos en ms desde el inicio. */
const SECUENCIA = [
  { idx: 1, at: 160 },
  { idx: 2, at: 310 },
  { idx: 3, at: 1080 },
  { idx: 4, at: 1210 },
  { idx: 5, at: 1340 },
]

const modoFigura = ref('frames')   // 'frames' | 'unico' | 'icono'
const frameActual = ref(0)
const fase = ref('confirmacion')

let temporizador = null
let temporizadoresFrame = []

/* Precarga: decide qué recurso está disponible antes de mostrar nada. */
onMounted(() => {
  probarImagen(frames[0])
    .then(() => { modoFigura.value = 'frames'; frames.forEach(precargar) })
    .catch(() => probarImagen(rutaSoldadoUnico)
      .then(() => { modoFigura.value = 'unico' })
      .catch(() => { modoFigura.value = 'icono' }))
})

function probarImagen(src) {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => resolve(src)
    img.onerror = () => reject(src)
    img.src = src
  })
}

function precargar(src) {
  const img = new Image()
  img.src = src
}

function alPresionarTecla(evento) {
  if (evento.key === 'Escape') onCancelar()
}

watch(
  () => props.visible,
  (abierto) => {
    if (abierto) {
      fase.value = 'confirmacion'
      frameActual.value = 0
      window.addEventListener('keydown', alPresionarTecla)
    } else {
      window.removeEventListener('keydown', alPresionarTecla)
      limpiarTemporizadores()
    }
  }
)

onBeforeUnmount(() => {
  window.removeEventListener('keydown', alPresionarTecla)
  limpiarTemporizadores()
})

function limpiarTemporizadores() {
  if (temporizador) { clearTimeout(temporizador); temporizador = null }
  temporizadoresFrame.forEach(clearTimeout)
  temporizadoresFrame = []
}

function onCancelar() {
  if (fase.value === 'despedida') return
  emit('cancelar')
}

function onConfirmar() {
  if (fase.value === 'despedida') return
  fase.value = 'despedida'
  if (modoFigura.value === 'frames') reproducirSaludo()
  temporizador = setTimeout(() => {
    temporizador = null
    emit('confirmar')
  }, DURACION_DESPEDIDA)
}

/* Reproduce el saludo según la secuencia (sube, mantiene, baja). */
function reproducirSaludo() {
  frameActual.value = 0
  temporizadoresFrame = SECUENCIA.map(({ idx, at }) =>
    setTimeout(() => { frameActual.value = idx }, at)
  )
}
</script>

<style scoped>
.lm-overlay {
  position: fixed;
  inset: 0;
  z-index: 1500;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  background: rgba(7, 35, 60, .58);
  backdrop-filter: blur(3px);
  -webkit-backdrop-filter: blur(3px);
}

.lm-card {
  width: 100%;
  max-width: 400px;
  padding: 26px 26px 24px;
  text-align: center;
  background: var(--sigta-blanco, #fff);
  border: 1px solid var(--sigta-borde, #d7e3ef);
  border-top: 4px solid var(--sigta-mostaza, #ffc72c);
  border-radius: 14px;
  box-shadow: 0 20px 50px rgba(11, 40, 79, .28);
}

.lm-card h2 {
  margin: 16px 0 6px;
  color: var(--sigta-azul, #123a6b);
  font-size: 21px;
  font-weight: 800;
}

.lm-card p {
  margin: 0;
  color: var(--sigta-texto-suave, #5b7189);
  font-size: 14.5px;
  line-height: 1.5;
}

/* ---------- Figura ---------- */
.lm-figura {
  width: 156px;
  height: 140px;
  margin: 2px auto 0;
  display: flex;
  align-items: flex-end;
  justify-content: center;
}

.lm-figura img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
  object-position: bottom center;
  filter: drop-shadow(0 6px 10px rgba(11, 40, 79, .14));
}

.lm-figura-fallback {
  width: 92px;
  height: 92px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--sigta-azul-tenue, #f0f6fc);
  border: 1px solid var(--sigta-borde-suave, #eaf1f8);
  color: var(--sigta-azul, #123a6b);
}

/* El contenedor solo hace la entrada, un leve porte firme y la
   retirada. El gesto del brazo lo llevan los 6 frames (sin deformar). */
.lm-figura.despedida {
  animation: lm-saludo 1.75s cubic-bezier(.4, 0, .2, 1) forwards;
}

@keyframes lm-saludo {
  0%   { opacity: 0; transform: translateY(14px) scale(.92); }
  9%   { opacity: 1; transform: translateY(0) scale(1); }
  20%  { transform: translateY(-3px) scale(1.02); }
  86%  { opacity: 1; transform: translateY(-2px) scale(1.02); }
  100% { opacity: 0; transform: translateY(34px) scale(.88); }
}

/* ---------- Acciones ---------- */
.lm-acciones {
  display: flex;
  gap: 10px;
  margin-top: 22px;
}

.lm-btn {
  flex: 1;
  min-height: 42px;
  padding: 0 14px;
  border-radius: 8px;
  font-family: inherit;
  font-size: 14.5px;
  font-weight: 700;
  cursor: pointer;
  transition: background .18s ease, box-shadow .18s ease, transform .12s ease;
}

.lm-cancelar {
  border: 1px solid var(--sigta-borde, #d7e3ef);
  background: var(--sigta-blanco, #fff);
  color: var(--sigta-texto-suave, #5b7189);
}

.lm-cancelar:hover {
  background: var(--sigta-azul-tenue, #f0f6fc);
}

.lm-confirmar {
  border: 1px solid var(--sigta-azul, #123a6b);
  background: var(--sigta-azul, #123a6b);
  color: #fff;
}

.lm-confirmar:hover {
  background: var(--sigta-azul-oscuro, #0c2a4f);
  box-shadow: 0 8px 18px rgba(11, 40, 79, .25);
}

.lm-btn:active {
  transform: scale(.98);
}

/* ---------- Puntos ---------- */
.lm-puntos {
  display: flex;
  gap: 7px;
  justify-content: center;
  margin-top: 18px;
}

.lm-puntos span {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--sigta-mostaza, #ffc72c);
  animation: lm-punto 1.1s ease-in-out infinite;
}

.lm-puntos span:nth-child(2) { animation-delay: .16s; }
.lm-puntos span:nth-child(3) { animation-delay: .32s; }

@keyframes lm-punto {
  0%, 75%, 100% { opacity: .3; transform: translateY(0); }
  35%           { opacity: 1; transform: translateY(-5px); }
}

/* ---------- Entrada / salida ---------- */
.lm-enter-active,
.lm-leave-active {
  transition: opacity .28s ease;
}

.lm-enter-from,
.lm-leave-to {
  opacity: 0;
}

.lm-enter-active .lm-card {
  animation: lm-card-in .32s cubic-bezier(.2, .8, .3, 1) both;
}

@keyframes lm-card-in {
  from { opacity: 0; transform: translateY(20px) scale(.96); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}

@media (max-width: 480px) {
  .lm-card { max-width: 100%; padding: 22px 18px 20px; }
  .lm-figura { width: 96px; height: 96px; }
}

@media (prefers-reduced-motion: reduce) {
  .lm-enter-active .lm-card,
  .lm-figura.despedida {
    animation: none;
  }
  .lm-puntos span {
    animation-duration: 1.6s;
  }
}
</style>
