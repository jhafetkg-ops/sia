<template>
  <fieldset class="decision-viabilidad">
    <legend>¿La compra es viable?</legend>
    <div>
      <label :class="{ seleccionada: modelValue === 'si' }"><input type="radio" :name="nombre" value="si" :checked="modelValue === 'si'" :disabled="ocupado" @change="$emit('update:modelValue', 'si')"> Sí, es viable</label>
      <label :class="{ seleccionada: modelValue === 'no' }"><input type="radio" :name="nombre" value="no" :checked="modelValue === 'no'" :disabled="ocupado" @change="$emit('update:modelValue', 'no')"> No, no es viable</label>
    </div>
    <p v-if="validada && modelValue === 'si'">Viabilidad registrada. Puede adjuntar el POA y el proveído de jefatura.</p>
    <p v-else-if="modelValue === 'si'">Confirme la viabilidad para habilitar el POA y el proveído de jefatura.</p>
    <p v-else-if="modelValue === 'no'">Al continuar deberá indicar el motivo de no viabilidad.</p>
    <p v-else>Revise la cotización y seleccione una opción para continuar.</p>
  </fieldset>
</template>

<script setup>
import { useId } from 'vue'
defineProps({ modelValue: String, validada: Boolean, ocupado: Boolean })
defineEmits(['update:modelValue'])
const nombre = useId()
</script>

<style scoped>
.decision-viabilidad{margin:18px 0;padding:16px;border:1px solid #c7d7e8;border-radius:10px;background:#fff;color:#17365b}
.decision-viabilidad legend{padding:0 7px;font-weight:800;font-size:16px}
.decision-viabilidad>div{display:flex;flex-wrap:wrap;gap:12px}
.decision-viabilidad label{display:flex;align-items:center;gap:10px;padding:13px 18px;border:1px solid #c7d7e8;border-radius:8px;font-weight:700;cursor:pointer}
.decision-viabilidad label.seleccionada{background:#edf4fc;border-color:#163c69}
.decision-viabilidad input{width:18px;height:18px;accent-color:#163c69;margin:0}
.decision-viabilidad p{margin:12px 0 0;color:#526a82;font-size:13px;line-height:1.5}
</style>
