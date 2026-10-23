// La entrada monetaria admite dígitos y hasta dos decimales, sin exponentes.
const valores = new WeakMap()
export const monto = {
  mounted(el) {
    valores.set(el, el.value || '')
    el.addEventListener('input', () => {
      const valor = el.value.replace(',', '.')
      if (/^\d*(?:\.\d{0,2})?$/.test(valor)) valores.set(el, valor)
      el.value = valores.get(el)
    }, true)
  },
  updated(el) {
    if (/^\d*(?:\.\d{0,2})?$/.test(el.value)) valores.set(el, el.value)
  },
}
