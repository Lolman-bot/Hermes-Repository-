// Minimal stand-in for @hermes/plugin-sdk, react and react/jsx-runtime.
// It records what the plugin registers; it does not render anything.
// Add a named export here when a plugin imports something new.
export const jsx = (type, props) => ({ type, props })
export const jsxs = jsx
export const Fragment = 'Fragment'
export const useState = (v) => [typeof v === 'function' ? v() : v, () => {}]
export const useEffect = () => {}
export const useMemo = (f) => f()
export const useCallback = (f) => f
export const useRef = (v) => ({ current: v })
export const atom = (v) => { let x = v; return { get: () => x, set: (n) => { x = n } } }
export const computed = (f) => ({ get: f })
export const useValue = (a) => a.get()
export const PALETTE_AREA = 'palette'
export const KEYBINDS_AREA = 'keybinds'
export const THEMES_AREA = 'themes'
export const ROUTES_AREA = 'routes'
export const SIDEBAR_NAV_AREA = 'sidebar.nav'
export const TRANSCRIPT_DIRECTIVE_AREA = 'transcript.directive'
export const host = {
  state: new Proxy({}, { get: () => atom(undefined) }),
  request: async () => ({}),
  onEvent: () => () => {},
  notify: () => {},
  navigate: () => {},
}
// Fake ctx for tests: call plugin.register(fakeCtx()) and inspect .registered
export function fakeCtx() {
  const registered = []
  const store = new Map()
  return {
    registered,
    register: (c) => { registered.push(c); return () => {} },
    storage: { get: (k) => store.get(k), set: (k, v) => store.set(k, v), remove: (k) => store.delete(k) },
    os: { notify: () => true },
  }
}
