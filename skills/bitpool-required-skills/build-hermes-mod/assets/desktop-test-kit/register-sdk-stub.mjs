// Usage (from the mod folder): node --import ./tests/register-sdk-stub.mjs --test "tests/*.test.mjs"
// Points @hermes/plugin-sdk, react and react/jsx-runtime at ./sdk-stub.mjs so plugin.js
// imports under plain Node. Needs Node 20.6+ (registerHooks on 22.15+, register before that).
import * as mod from 'node:module'

const STUB = new URL('./sdk-stub.mjs', import.meta.url).href
const STUBBED = new Set(['@hermes/plugin-sdk', 'react', 'react/jsx-runtime'])

if (typeof mod.registerHooks === 'function') {
  mod.registerHooks({
    resolve(specifier, context, nextResolve) {
      if (STUBBED.has(specifier)) return { url: STUB, shortCircuit: true }
      return nextResolve(specifier, context)
    },
  })
} else {
  mod.register('./sdk-loader.mjs', import.meta.url)
}
