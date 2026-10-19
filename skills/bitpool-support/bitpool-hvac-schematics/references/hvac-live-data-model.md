# Live Data Model — the model() / paint() / wire() Pattern

Every schematic uses the same tiny architecture. Keep it; it's what makes the pages
feel live and lets you swap the mock for a real feed in one place.

```
S          → command state (set by the segmented controls)
model(S)   → pure function returning a snapshot of all live values
paint(p)   → writes snapshot p into the SVG chips, KPI strip, points list, alarms
wire()     → binds a segmented control to S and repaints
setInterval(() => paint(model()), 2200)   → the "live" tick
```

The key discipline: **`paint()` is the only thing that touches the DOM**, and it reads
*everything* from the snapshot `p` plus the command state `S`. To go live, replace the
body of `model()` with a fetch/websocket read and keep `paint()` unchanged.

## Helpers (top of every script)
```js
const $ = id => document.getElementById(id);
const rnd = (b,j)=> b + (Math.random()*2-1)*j;   // jittered mock value
const f1 = v => v.toFixed(1);
const i0 = v => Math.round(v);
```

## Command state + staging
Equipment staging is the backbone of the plant pages. Run/standby is derived, never stored per-unit:
```js
const S = { plant:true, auto:true, stage:2, sp:6.0 };
function model(){
  const on = S.plant, n = on ? S.stage : 0;
  const run = i => on && i < n;                     // unit i (0-based) runs?
  // ... derive temps/flows/speeds from on, n, sp ...
  return {
    chws, chwr, dt:Math.max(0,chwr-chws), flow,
    ch:[0,1,2].map(i=>({ run:run(i), t:run(i)?rnd(sp+0.4,0.2):null, l:run(i)?i0(rnd(70,4)):0 })),
    p :[0,1,2].map(i=>({ run:run(i), spd:run(i)?i0(rnd(77,3)):0 })),
  };
}
```
Physical realism that reads well: supply temp drifts toward setpoint when running; a tower's
achieved supply is clamped to `wet-bulb + approach`; flow scales with `n`; fan/pump speed
modulates to hold setpoint. Off units show `--`, `0`, greyed boxes and shut valves.

## paint(): the four write targets

**1. SVG chips & equipment state**
```js
$('c_chws').textContent = f1(p.chws);
p.ch.forEach((c,i)=>{ const n=i+1;
  $('ch'+n+'dot').setAttribute('fill', c.run?'var(--ok)':'var(--off)');
  $('ch'+n+'box').classList.toggle('off', !c.run);
  $('c_ch'+n+'t').textContent = c.run ? f1(c.t) : '--';
  document.querySelectorAll('#ch'+n+'iv path').forEach(e=>{ e.classList.toggle('valve-open',c.run); e.classList.toggle('valve-shut',!c.run); });
  document.querySelectorAll('.ch'+n+'f').forEach(e=>e.classList.toggle('stopped',!c.run)); // flow overlays for that unit
});
['fl_s','fl_r'].forEach(id=>$(id).classList.toggle('stopped',!S.plant)); // header flow
```
> Tip: tag each unit's flow overlays with a shared class like `ch1f`, `ct2f` so one
> `querySelectorAll(...).toggle('stopped')` starts/stops just that unit's animation.

**2. KPI strip** (top). First cell is mode (state dot), last is alarm count (state dot).
```js
$('s_chws').textContent=f1(p.chws); $('s_dt').textContent=f1(p.dt);
$('modeTxt').textContent = S.plant?'Enabled':'Disabled';
$('modeDot').className = 'dot '+(S.plant?'ok':'off');
```

**3. Alarm roll-up** (`#almList`). Build from a small array; severity drives the dot + chip class.
```js
const alarms = [
  {n:'Lead pump proven', st:p.p[0].run?'ok':'off', txt:p.p[0].run?'Proven':'Stopped'},
  {n:'Low ΔT syndrome',  st:p.dt<4.5?'warn':'ok', txt:p.dt<4.5?'ΔT low':'OK'},
  // st ∈ 'ok' | 'warn' | 'alarm' | 'off'
];
const active = alarms.filter(a=>a.st==='warn'||a.st==='alarm').length;
$('almTxt').textContent = active;
$('almDot').className = 'dot '+(alarms.some(a=>a.st==='alarm')?'alarm':(active?'warn':'ok'));
$('almList').innerHTML = alarms.map(a=>`<div class="row"><span class="dot ${a.st}"></span>${a.n}<span class="st ${a.st}">${a.txt}</span></div>`).join('');
```
Only flag a *real* fault. Don't warn for normal conditions (e.g. a high approach-to-wet-bulb
is normal when the setpoint sits well above wet-bulb — only alarm if the unit can't hold
setpoint at high fan: `cws > sp+1.5 && fan >= 95`).

**4. Live points list** (`#ptList`) — a flat table of code / description / value / unit.
```js
const rows = [
  ['CHWS','Plant supply temp',f1(p.chws),'°C'],
  ['ΔT','Plant delta-T',f1(p.dt),'K'],
  ['P1.SPD','Pump 1 speed',p.p[0].spd,'%'],
];
$('ptList').innerHTML = rows.map(r=>`<div class="row"><span class="code">${r[0]}</span><span class="desc">${r[1]}</span><span class="pv">${r[2]}<span class="u"> ${r[3]}</span></span></div>`).join('');
$('ts').textContent = new Date().toLocaleTimeString('en-AU',{hour12:false});
```

## wire(): segmented commands
```js
function wire(segId, cb){
  const seg = $(segId);
  seg.querySelectorAll('button').forEach(b=>b.addEventListener('click',()=>{
    seg.querySelectorAll('button').forEach(x=>x.classList.remove('on','alarm'));
    b.classList.add('on'); cb(b.dataset.v, b); paint(model());
  }));
}
wire('seg_plant', (v,b)=>{ S.plant = v==='en'; if(v==='dis') b.classList.add('alarm'); });
wire('seg_stage', v=> S.stage = parseInt(v));
wire('seg_sp',    v=> S.sp    = parseFloat(v));
```
Give the "off/stop/disable" choice the `alarm` class so it reads red when selected.

## Damper / modulating feedback (AHU)
For a single-blade damper, rotate the blade by % open so the position is visible:
```js
const DAMP = { oad:{el:'bl_oad',cx:85,cy:110,axis:'h'} };  // axis 'h' = horizontal duct
function setBlade(key,pct){ const d=DAMP[key];
  const a = d.axis==='h' ? (90 - pct*0.9) : (pct*0.9);     // 0%=across(closed) … 100%=along(open)
  $(d.el).setAttribute('transform', `rotate(${a} ${d.cx} ${d.cy})`);
}
```

## The tick
```js
paint(model());
setInterval(()=>paint(model()), 2200);   // 2.2 s feels alive without being twitchy
```

## Going live (when wiring to Bitpool data)
- Replace `model()`'s mock body with a read from the live source (Bitpool stream/graph,
  websocket, or polled REST), mapping each point key to the same snapshot shape.
- Keep `paint()` byte-for-byte. Keep the chip `id`s stable — they are the binding contract.
- Commands (`wire`) should issue point writes instead of (or in addition to) mutating `S`.
- Per the platform rules, treat write/command points as side-effecting: confirm before
  actually writing to plant.
