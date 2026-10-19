import { test } from 'node:test'
import assert from 'node:assert/strict'
import { coincideProceso, opcionSolicitudesActiva } from './portal.js'

test('el menú marca una sola opción para solicitudes y verificaciones', () => {
  const solicitudes = { path: '/usuario/mis-solicitudes', query: {} }
  assert.equal(opcionSolicitudesActiva(solicitudes), true)
  assert.equal(opcionSolicitudesActiva(solicitudes, true), false)

  const verificaciones = {
    path: '/usuario/mis-solicitudes', query: { vista: 'verificaciones' },
  }
  assert.equal(opcionSolicitudesActiva(verificaciones), false)
  assert.equal(opcionSolicitudesActiva(verificaciones, true), true)
})

test('el filtro separa soporte y mantenimiento', () => {
  assert.equal(coincideProceso({ proceso: 'SOPORTE' }, 'SOPORTE'), true)
  assert.equal(coincideProceso({ origen_modulo: 'MANTENIMIENTO' }, 'SOPORTE'), false)
  assert.equal(coincideProceso({ jefatura: 'UTIC' }, 'SOPORTE'), true)
  assert.equal(coincideProceso({ proceso: 'SOPORTE' }, ''), true)
})
