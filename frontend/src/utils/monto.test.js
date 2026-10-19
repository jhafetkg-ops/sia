import { test } from 'node:test'
import assert from 'node:assert/strict'
import { monto } from './monto.js'

test('monto conserva el último valor válido al escribir o pegar caracteres inválidos', () => {
  let listener
  const el = { value: '', addEventListener: (name, callback, capture) => {
    assert.equal(name, 'input')
    assert.equal(capture, true)
    listener = callback
  } }
  monto.mounted(el)
  for (const [entrada, esperado] of [
    ['1250', '1250'], ['1250.5', '1250.5'], ['1250.50', '1250.50'],
    ['1250.501', '1250.50'], ['abc', '1250.50'], ['1e3', '1250.50'],
    ['-20', '1250.50'], ['$100', '1250.50'], ['100,25', '100.25'], ['', ''],
  ]) {
    el.value = entrada
    listener()
    assert.equal(el.value, esperado)
  }
  el.value = '50.00'
  monto.updated(el)
  el.value = 'letras'
  listener()
  assert.equal(el.value, '50.00')
})
