export function solicitarFirma(titulo, expediente) {
  return new Promise(resolve => window.dispatchEvent(new CustomEvent('sia-firma', { detail: { titulo, expediente, resolve } })))
}
