import { ref } from 'vue'

/*
 * Estado reutilizable para la tarjeta gelatinosa de "guardado".
 * Cada vista crea su propia instancia:
 *
 *   const { mostrar, texto, tipo, animar, animarError, ocultar } = usarGuardado()
 *   ...
 *   await animar('Rol actualizado')           // exito
 *   await animarError('Falta el archivo X')   // error
 *
 * Ambas esperan a que la persona haga clic en "Aceptar" (o la X, o
 * afuera de la tarjeta) antes de resolver — no se cierran solas, para
 * que el mensaje no desaparezca antes de que alguien alcance a leerlo.
 *
 * y en el template:
 *
 *   <TarjetaGuardado :visible="mostrar" :texto="texto" :tipo="tipo" @cerrar="ocultar" />
 */
export function usarGuardado() {
  const mostrar = ref(false)
  const texto = ref('Cambios guardados')
  const tipo = ref('exito')
  let resolverCierre = null

  function animar(mensaje, tipoMensaje = 'exito') {
    texto.value = mensaje || 'Cambios guardados'
    tipo.value = tipoMensaje
    mostrar.value = true
    return new Promise(resolve => { resolverCierre = resolve })
  }

  function animarError(mensaje) {
    return animar(mensaje || 'No fue posible completar la acción.', 'error')
  }

  function ocultar() {
    mostrar.value = false
    if (resolverCierre) {
      resolverCierre()
      resolverCierre = null
    }
  }

  return { mostrar, texto, tipo, animar, animarError, ocultar }
}
