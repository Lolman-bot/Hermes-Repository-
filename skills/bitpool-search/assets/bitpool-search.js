/* ============================================================================
 * BitpoolSearch — Google-style predictive search for Bitpool pages
 * Self-contained, dependency-free. Pairs with bitpool-search.css.
 *
 *   const search = BitpoolSearch({
 *     mount: '#searchHost',
 *     placeholder: 'Search projects, people or clients…',
 *     items: [ {type:'project', label:'BP-0726', meta:'Dexus full-scope', tag:'90%', ref:proj} , … ],
 *     types: { project:{icon:'BP'}, person:{icon:'@'}, client:{icon:'C'} },
 *     onSelect: (item) => { … },   // user picked a suggestion (click / Enter)
 *     onInput:  (query) => { … },  // query changed — use to live-filter a table
 *   });
 *
 * Returns: { setItems, setQuery, clear, focus, open, close, destroy }
 * ==========================================================================*/
window.BitpoolSearch = function (cfg) {
  cfg = cfg || {};
  const host = typeof cfg.mount === 'string' ? document.querySelector(cfg.mount) : cfg.mount;
  if (!host) { console.warn('BitpoolSearch: mount not found'); return {}; }

  // ---- config + defaults -------------------------------------------------
  let items       = cfg.items || [];
  const maxResults = cfg.maxResults || 8;
  const minChars   = cfg.minChars != null ? cfg.minChars : 1;
  const placeholder = cfg.placeholder || 'Search…';
  // type → {icon,color}. Falls back to a neutral chip for unknown types.
  const TYPES = Object.assign({
    project: { icon: 'BP', color: 'var(--navy,#1B2732)' },
    person:  { icon: '@',  color: 'var(--accent,#00ADEF)' },
    client:  { icon: 'C',  color: '#6d8aa8' }
  }, cfg.types || {});
  const fieldsOf = cfg.searchFields || (it => [it.label, it.meta]); // what text to match against
  const rank     = cfg.rank || defaultRank;

  // ---- build DOM ---------------------------------------------------------
  host.classList.add('bp-search');
  host.innerHTML =
    '<div class="bp-search-input">' +
      '<svg class="bp-search-mag" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">' +
        '<circle cx="11" cy="11" r="7"></circle><path d="m21 21-4.3-4.3"></path></svg>' +
      '<input type="text" autocomplete="off" spellcheck="false">' +
      '<span class="bp-search-clear" role="button" aria-label="Clear">&times;</span>' +
    '</div>' +
    '<div class="bp-suggest" role="listbox"></div>';

  const input  = host.querySelector('input');
  const box     = host.querySelector('.bp-suggest');
  const clearBtn = host.querySelector('.bp-search-clear');
  input.placeholder = placeholder;

  let active = -1;     // highlighted suggestion index
  let current = [];    // current suggestion list

  // ---- helpers -----------------------------------------------------------
  function esc(s){ return String(s).replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }
  function hl(text, q){
    if (!q) return escapeHtml(text);
    return escapeHtml(text).replace(new RegExp('(' + esc(escapeHtml(q)) + ')', 'ig'), '<mark>$1</mark>');
  }
  function escapeHtml(s){ return String(s == null ? '' : s)
    .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }

  // default ranking: startsWith-label beats includes-label beats includes-meta
  function defaultRank(q, it){
    const ql = q.toLowerCase();
    const fields = fieldsOf(it).filter(Boolean).map(s => String(s).toLowerCase());
    if (!fields.length) return Infinity;
    if (fields[0].startsWith(ql)) return 0;
    if (fields[0].includes(ql))  return 1;
    if (fields.slice(1).some(f => f.includes(ql))) return 2;
    return Infinity; // no match
  }

  // ---- suggestions -------------------------------------------------------
  function buildSuggest(q){
    if (!q || q.length < minChars){ close(); return; }
    current = items
      .map(it => ({ it, score: rank(q, it) }))
      .filter(x => x.score !== Infinity)
      .sort((a, b) => a.score - b.score)
      .slice(0, maxResults)
      .map(x => x.it);

    if (!current.length){ close(); return; }

    box.innerHTML = current.map((s, i) => {
      const t = TYPES[s.type] || { icon: (s.type || '?')[0].toUpperCase(), color: '#6d8aa8' };
      return '<div class="bp-sg' + (i === active ? ' active' : '') + '" data-i="' + i + '" role="option">' +
        '<div class="bp-sg-ic" style="background:' + t.color + '">' + escapeHtml(t.icon) + '</div>' +
        '<div class="bp-sg-tx"><div class="bp-sg-n">' + hl(s.label, q) + '</div>' +
          (s.meta ? '<div class="bp-sg-m">' + hl(s.meta, q) + '</div>' : '') + '</div>' +
        (s.tag ? '<div class="bp-sg-tag">' + escapeHtml(s.tag) + '</div>' : '') +
      '</div>';
    }).join('');
    box.classList.add('open');
    box.querySelectorAll('.bp-sg').forEach(el =>
      el.addEventListener('mousedown', e => { e.preventDefault(); choose(+el.dataset.i); }));
  }

  function choose(i){
    const s = current[i]; if (!s) return;
    input.value = s.label;
    clearBtn.style.display = 'block';
    close();
    if (cfg.onInput)  cfg.onInput(s.label, s);
    if (cfg.onSelect) cfg.onSelect(s);
  }

  function close(){ box.classList.remove('open'); active = -1; }
  function open(){ if (current.length) box.classList.add('open'); }

  // ---- events ------------------------------------------------------------
  input.addEventListener('input', e => {
    active = -1;
    const v = e.target.value.trim();
    clearBtn.style.display = v ? 'block' : 'none';
    buildSuggest(v);
    if (cfg.onInput) cfg.onInput(v, null);
  });

  input.addEventListener('keydown', e => {
    if (!box.classList.contains('open')) {
      if (e.key === 'ArrowDown') { buildSuggest(input.value.trim()); }
      return;
    }
    if (e.key === 'ArrowDown')      { active = Math.min(active + 1, current.length - 1); paint(); e.preventDefault(); }
    else if (e.key === 'ArrowUp')   { active = Math.max(active - 1, 0); paint(); e.preventDefault(); }
    else if (e.key === 'Enter')     { if (active >= 0) choose(active); else close(); }
    else if (e.key === 'Escape')    { close(); }
  });

  function paint(){
    box.querySelectorAll('.bp-sg').forEach((el, i) => el.classList.toggle('active', i === active));
    const el = box.querySelector('.bp-sg.active');
    if (el && el.scrollIntoView) el.scrollIntoView({ block: 'nearest' });
  }

  clearBtn.addEventListener('click', () => {
    input.value = ''; clearBtn.style.display = 'none'; close();
    if (cfg.onInput) cfg.onInput('', null);
    if (cfg.onClear) cfg.onClear();
    input.focus();
  });

  const outside = e => { if (!host.contains(e.target)) close(); };
  document.addEventListener('click', outside);

  // ---- public API --------------------------------------------------------
  return {
    setItems(next){ items = next || []; if (input.value.trim()) buildSuggest(input.value.trim()); },
    setQuery(q){ input.value = q || ''; clearBtn.style.display = q ? 'block' : 'none'; buildSuggest((q||'').trim()); if (cfg.onInput) cfg.onInput(q||'', null); },
    clear(){ clearBtn.click(); },
    focus(){ input.focus(); },
    open, close,
    el: { host, input, box },
    destroy(){ document.removeEventListener('click', outside); host.innerHTML = ''; }
  };
};
