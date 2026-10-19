export function esVistaVerificaciones(route) {
  return route.query.vista === 'verificaciones'
}

export function opcionSolicitudesActiva(route, verificaciones = false) {
  return route.path.endsWith('/mis-solicitudes') && esVistaVerificaciones(route) === verificaciones
}

export function coincideProceso(item, proceso) {
  if (!proceso) return true
  const origen = item.proceso || item.origen_modulo || item.jefatura || ''
  return (origen === 'UTIC' ? 'SOPORTE' : origen) === proceso
}
