# No webfont link, deliberately. This artefact is evidence: it must make ZERO network
# requests, so it renders identically offline, on a locked-down network, and in five
# years when a hosted font service may not answer. The IBM Plex families are still
# named first in every stack — if a reader has them installed locally they get them —
# and the system fallbacks behind them carry the same roles (grotesque / mono / serif).
CSS = """
<style>
:root{
  --paper:#F4F7F9; --surface:#FFFFFF; --surface-2:#EDF1F4;
  --ink:#0F1720; --ink-soft:#48565F; --ink-faint:#74838D;
  --rule:#D9E1E6; --rule-soft:#E7ECEF;
  --public:#A2661F; --private:#2F5B87; --isolated:#186354;
  --public-bg:#F7EEE1; --private-bg:#E7EFF7; --isolated-bg:#E1F0EB;
  --flag:#A2352A; --flag-bg:#F8E9E6; --vendor:#63548A; --vendor-bg:#EDEAF4;
  --warn:#8A6412; --edge:#7A8992;
  --shadow:0 1px 2px rgba(15,23,32,.06),0 8px 24px -12px rgba(15,23,32,.16);
}
@media (prefers-color-scheme:dark){
  :root:not([data-theme="light"]){
    --paper:#0B1116; --surface:#131B22; --surface-2:#18222B;
    --ink:#E3EAEF; --ink-soft:#9DACB6; --ink-faint:#74848E;
    --rule:#26323B; --rule-soft:#1E2830;
    --public:#D9A05C; --private:#7FB0DD; --isolated:#5DBCA6;
    --public-bg:#2A2015; --private-bg:#152431; --isolated-bg:#122924;
    --flag:#E2867A; --flag-bg:#2E1A18; --vendor:#A899CE; --vendor-bg:#211D2E;
    --warn:#D6AC5A; --edge:#63737D;
    --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px -12px rgba(0,0,0,.6);
  }
}
:root[data-theme="dark"]{
  --paper:#0B1116; --surface:#131B22; --surface-2:#18222B;
  --ink:#E3EAEF; --ink-soft:#9DACB6; --ink-faint:#74848E;
  --rule:#26323B; --rule-soft:#1E2830;
  --public:#D9A05C; --private:#7FB0DD; --isolated:#5DBCA6;
  --public-bg:#2A2015; --private-bg:#152431; --isolated-bg:#122924;
  --flag:#E2867A; --flag-bg:#2E1A18; --vendor:#A899CE; --vendor-bg:#211D2E;
  --warn:#D6AC5A; --edge:#63737D;
  --shadow:0 1px 2px rgba(0,0,0,.4),0 8px 24px -12px rgba(0,0,0,.6);
}
*{box-sizing:border-box}
body{background:var(--paper);color:var(--ink);
  font-family:"IBM Plex Sans",ui-sans-serif,system-ui,sans-serif;
  font-size:16px;line-height:1.6;margin:0;-webkit-font-smoothing:antialiased}
.wrap{max-width:1180px;margin:0 auto;padding:0 28px 96px}
code,.mono{font-family:"IBM Plex Mono",ui-monospace,monospace;font-variant-ligatures:none}

.rail{background:var(--surface);border-bottom:1px solid var(--rule);position:sticky;top:0;z-index:20}
.rail-in{max-width:1180px;margin:0 auto;padding:9px 28px;display:flex;flex-wrap:wrap;
  gap:7px 26px;align-items:baseline}
.rail .grp{white-space:nowrap}
.rail dt{font-size:9.5px;letter-spacing:.11em;text-transform:uppercase;color:var(--ink-faint);
  font-weight:600;margin:0 6px 0 0;display:inline}
.rail dd{margin:0;display:inline;font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--ink-soft)}

header.hero{padding:52px 0 30px;border-bottom:1px solid var(--rule)}
.eyebrow{font-size:11px;letter-spacing:.15em;text-transform:uppercase;color:var(--private);
  font-weight:600;margin:0 0 14px}
h1{font-size:clamp(30px,4.4vw,46px);line-height:1.08;letter-spacing:-.021em;margin:0 0 16px;
  font-weight:600;text-wrap:balance}
.standfirst{font-family:"IBM Plex Serif",Georgia,serif;font-size:19px;line-height:1.58;
  color:var(--ink-soft);margin:0;max-width:64ch}

h2{font-size:23px;letter-spacing:-.012em;margin:0 0 6px;font-weight:600;text-wrap:balance}
h3{font-size:15px;margin:0 0 8px;font-weight:600}
section{padding-top:52px}
.sec-head{display:flex;gap:14px;align-items:baseline;border-bottom:1px solid var(--rule-soft);
  padding-bottom:12px;margin-bottom:22px;flex-wrap:wrap}
.sec-n{font-family:"IBM Plex Mono",monospace;font-size:12px;color:var(--ink-faint);
  font-weight:500;padding-top:5px}
.lede{font-family:"IBM Plex Serif",Georgia,serif;font-size:16.5px;color:var(--ink-soft);
  margin:0 0 22px;max-width:66ch;line-height:1.62}
p{margin:0 0 15px}

.verdict{display:grid;grid-template-columns:repeat(auto-fit,minmax(258px,1fr));gap:14px;margin:26px 0 4px}
.vcard{background:var(--surface);border:1px solid var(--rule);border-radius:9px;padding:17px 18px;
  box-shadow:var(--shadow)}
.vcard .k{font-size:10px;letter-spacing:.11em;text-transform:uppercase;font-weight:600;margin:0 0 9px}
.vcard.yes .k{color:var(--isolated)}
.vcard.no .k{color:var(--flag)}
.vcard.part .k{color:var(--warn)}
.vcard p{margin:0;font-size:14px;color:var(--ink-soft);line-height:1.55}
.vcard strong{color:var(--ink);font-weight:600}

.figure{margin:0 0 12px}
.scroller{overflow-x:auto;background:var(--surface);border:1px solid var(--rule);
  border-radius:10px;padding:18px;box-shadow:var(--shadow)}
.scroller svg{display:block;min-width:840px;width:100%;height:auto}
figcaption{font-size:12.5px;color:var(--ink-faint);margin-top:11px;max-width:74ch}
figcaption b{color:var(--ink-soft);font-weight:600}
.key{display:flex;flex-wrap:wrap;gap:8px 20px;margin:16px 0 0;font-size:12px;color:var(--ink-soft)}
.key i{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:7px;
  vertical-align:-1px;font-style:normal}

.s-untrust{fill:var(--flag-bg);stroke:var(--flag);stroke-width:1;stroke-dasharray:4 3}
.s-bandlab{font:600 9.5px "IBM Plex Sans";letter-spacing:.13em;fill:var(--flag)}
.s-bandval{font:500 12.5px "IBM Plex Mono";fill:var(--ink-soft)}
.s-bandnote{font:400 11px "IBM Plex Sans";fill:var(--ink-faint)}
.s-acct{fill:var(--surface-2);stroke:var(--rule);stroke-width:1}
.s-acctname{font:600 12.5px "IBM Plex Sans";fill:var(--ink)}
.s-acctid{font:400 11.5px "IBM Plex Mono";fill:var(--ink-faint)}
.s-vpc{fill:var(--surface);stroke:var(--rule);stroke-width:1}
.s-vpc-flag{fill:var(--surface);stroke:var(--flag);stroke-width:1.6;stroke-dasharray:5 3}
.s-vpcname{font:600 13.5px "IBM Plex Sans";fill:var(--ink)}
.s-vpccidr{font:500 12px "IBM Plex Mono";fill:var(--private)}
.s-vpceni{font:400 10.5px "IBM Plex Sans";fill:var(--ink-faint)}
.s-chip{font:600 8.5px "IBM Plex Sans";letter-spacing:.1em;fill:var(--flag)}
.s-t-public{fill:var(--public-bg)}
.s-b-public{fill:var(--public)}
.s-l-public{fill:var(--public)}
.s-t-private{fill:var(--private-bg)}
.s-b-private{fill:var(--private)}
.s-l-private{fill:var(--private)}
.s-t-isolated{fill:var(--isolated-bg)}
.s-b-isolated{fill:var(--isolated)}
.s-l-isolated{fill:var(--isolated)}
.s-t-unrouted{fill:var(--surface-2)}
.s-b-unrouted{fill:var(--edge)}
.s-l-unrouted{fill:var(--ink-faint)}
.s-tierlab{font:600 9.5px "IBM Plex Sans";letter-spacing:.05em}
.s-cidr{font:400 11px "IBM Plex Mono";fill:var(--ink-soft)}
.s-igw{stroke:var(--edge);stroke-width:1.2;stroke-dasharray:3 3}
.e-int{fill:none;stroke:var(--private);stroke-width:1.7}
.e-ext{fill:none;stroke:var(--vendor);stroke-width:1.7;stroke-dasharray:6 4}
.e-flag{fill:none;stroke:var(--flag);stroke-width:2.6}
.e-lab-flag{font:600 11px "IBM Plex Sans";fill:var(--flag)}
.n-int{fill:var(--surface);stroke:var(--private);stroke-width:1.4}
.n-ext{fill:var(--vendor-bg);stroke:var(--vendor);stroke-width:1.4;stroke-dasharray:5 3}
.n-lab{font:600 12.5px "IBM Plex Sans";fill:var(--ink)}
.n-cidr{font:500 11px "IBM Plex Mono";fill:var(--private)}
.n-sub{font:400 10px "IBM Plex Sans";fill:var(--ink-faint)}

table{border-collapse:collapse;width:100%;font-size:13.5px;font-variant-numeric:tabular-nums}
th{text-align:left;font-size:9.5px;letter-spacing:.11em;text-transform:uppercase;color:var(--ink-faint);
  font-weight:600;padding:0 14px 9px 0;border-bottom:1px solid var(--rule);white-space:nowrap}
td{padding:9px 14px 9px 0;border-bottom:1px solid var(--rule-soft);vertical-align:top;color:var(--ink-soft)}
td.k{color:var(--ink);font-weight:500}
tr:last-child td{border-bottom:none}
.pill{display:inline-block;font-size:10px;font-weight:600;letter-spacing:.05em;padding:2.5px 8px;
  border-radius:999px;white-space:nowrap;text-transform:uppercase}
.p-public{background:var(--public-bg);color:var(--public)}
.p-private{background:var(--private-bg);color:var(--private)}
.p-isolated{background:var(--isolated-bg);color:var(--isolated)}
.p-flag{background:var(--flag-bg);color:var(--flag)}
.p-ok{background:var(--isolated-bg);color:var(--isolated)}
.p-vendor{background:var(--vendor-bg);color:var(--vendor)}
.p-warn{background:var(--public-bg);color:var(--warn)}

.finding{background:var(--surface);border:1px solid var(--rule);border-left-width:4px;
  border-radius:8px;padding:17px 20px;margin-bottom:12px;box-shadow:var(--shadow)}
.finding.high{border-left-color:var(--flag)}
.finding.medium{border-left-color:var(--warn)}
.finding.low{border-left-color:var(--edge)}
.f-top{display:flex;gap:12px;align-items:baseline;flex-wrap:wrap;margin-bottom:7px}
.f-sev{font-size:9.5px;letter-spacing:.11em;text-transform:uppercase;font-weight:700}
.high .f-sev{color:var(--flag)}
.medium .f-sev{color:var(--warn)}
.low .f-sev{color:var(--ink-faint)}
.f-ctl{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--ink-faint)}
.f-title{font-size:16px;font-weight:600;margin:0 0 7px;color:var(--ink);width:100%}
.finding p{font-size:14px;margin:0 0 10px;color:var(--ink-soft)}
.f-test{font-family:"IBM Plex Serif",Georgia,serif;font-style:italic;font-size:14px;
  color:var(--ink-soft);border-top:1px solid var(--rule-soft);padding-top:10px;margin:0}

pre{background:var(--surface);border:1px solid var(--rule);border-radius:9px;padding:16px 18px;
  overflow-x:auto;font-family:"IBM Plex Mono",monospace;font-size:12.5px;line-height:1.62;
  color:var(--ink-soft);margin:0 0 14px;box-shadow:var(--shadow)}
pre b{color:var(--private);font-weight:600}
pre i{color:var(--ink-faint);font-style:normal}
.steps{display:grid;grid-template-columns:repeat(auto-fit,minmax(212px,1fr));gap:12px;margin:22px 0}
.step{background:var(--surface);border:1px solid var(--rule);border-radius:9px;padding:15px 16px}
.step .n{font-family:"IBM Plex Mono",monospace;font-size:11px;color:var(--private);font-weight:600;
  display:block;margin-bottom:7px}
.step h3{margin:0 0 6px;font-size:14px}
.step p{font-size:13px;margin:0;color:var(--ink-soft);line-height:1.5}
.note{background:var(--surface-2);border:1px solid var(--rule);border-radius:9px;padding:16px 18px;
  font-size:14px;color:var(--ink-soft);margin:20px 0}
.note strong{color:var(--ink)}
footer{margin-top:64px;padding-top:22px;border-top:1px solid var(--rule);font-size:12px;
  color:var(--ink-faint);display:flex;justify-content:space-between;gap:18px;flex-wrap:wrap}
a{color:var(--private)}
a:focus-visible{outline:2px solid var(--private);outline-offset:3px;border-radius:3px}
@media (prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}
@media (max-width:640px){.wrap{padding:0 18px 64px}.rail-in{padding:9px 18px}}
</style>
"""
