// Node module hooks: resolve the desktop app's three import specifiers to local stubs,
// so plugin.js can be imported under `node --test` without the Hermes desktop app.
const STUB = new URL('./sdk-stub.mjs', import.meta.url).href
const STUBBED = new Set(['@hermes/plugin-sdk', 'react', 'react/jsx-runtime'])

export async function resolve(specifier, context, nextResolve) {
  if (STUBBED.has(specifier)) return { url: STUB, shortCircuit: true }
  return nextResolve(specifier, context)
}
