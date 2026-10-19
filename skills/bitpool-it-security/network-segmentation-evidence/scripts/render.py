"""Render the evidence pack: HTML page + Mermaid adjacency + archived dump.

THE OUTPUT MUST MAKE ZERO NETWORK REQUESTS. It is evidence: it has to render identically
offline, on a locked-down network, and years from now. Three rules follow, and all three
were broken in the first version:

  * No webfont link, no CDN, no remote anything. Font stacks name IBM Plex first and fall
    back to system faces, so a reader with Plex installed gets it and everyone else still
    gets the right role (grotesque / mono / serif).
  * Emit a COMPLETE document -- doctype, html, head, body. Writing a fragment for an
    Artifact wrapper leaves a standalone file rendering in quirks mode.
  * Never emit `<pre class="mermaid">`. Artifacts render Mermaid natively; a browser
    opening a local file does not, so the block silently displays as a wall of code.
    Mermaid goes to a separate file for targets that can render it.

EVERY MERMAID OUTPUT IS A .md FILE WITH A FENCED BLOCK, never a bare .mmd. v1.1
emitted the adjacency graph as a bare adjacency.mmd, which does not render in
Drata's evidence viewer -- and Drata is the only place this file goes. A reviewer
opening it got raw source. Fenced in Markdown it renders there, and degrades to
readable source anywhere it does not. One shape, so a consumer never has to know
which.

v1.1: provenance from the collection manifest, scope/coverage section, region
column throughout, and the Mermaid *topology* emitter removed — a stale wiki
diagram is a worse answer than querying live, so only the adjacency graph (which
Mermaid genuinely renders better than hand-laid SVG) survives.

v1.2: diagram.py deleted and network-topology.md no longer emitted. That file was
a second rendering of what sections 02, 03 and 05 already carry -- the same
topology as a Mermaid flowchart rather than hand-laid SVG, the same networks and
boundary-crossing tables, a second copy of the internal addressing -- and it was
the drift surface behind three separate divergence logs on 2026-09-16: the two
files disagreed about coverage, about the dump's file count, and about what shape
a Mermaid graph ships in. Shared helpers fixed the symptom; removing the duplicate
removes the cause. Its stated job, "show me the network", is one SKILL.md assigns
to /aws-query and explicitly disclaims for this skill. The pack plus the dump are
the output contract, and DCF-22 is met by the SVG in section 02.
"""
import os
import shutil
import sys

import model as M
import svg as S
import findings as F
from style import CSS

TIER_PILL = {"public": "p-public", "private": "p-private",
             "isolated": "p-isolated", "unrouted": "p-warn"}
e = S.esc


def rail(m):
    p = m["provenance"]
    who = (p.get("collected_by") or "").split("/")[-1]
    items = [("collected", p.get("collected_utc") or "—"),
             ("by", who or "—"),
             ("digest", p.get("digest") or "—"),
             ("regions probed", str(len(m["regions_enabled"]))),
             ("accounts", str(m.get("org_account_count") or "—")),
             ("generator", p.get("generator") or "netpack")]
    inner = "".join(f'<div class="grp"><dt>{k}</dt><dd>{e(v)}</dd></div>' for k, v in items)
    return f'<div class="rail"><dl class="rail-in">{inner}</dl></div>'


def verdict(m, fs):
    """The three cards an auditor reads first. EVERY CLAUSE HERE IS COMPUTED.

    v1.1 shipped this block with the counts interpolated but the prose around
    them hardcoded from the first run. By the second run one of those clauses --
    "including accounts in the Organization this sweep could not reach at all"
    -- was flatly false: the exclusions had since been written, findings.py no
    longer emitted the uncovered-accounts finding, and section 01 said in as
    many words that none were unaccounted for. The page conceded a scope gap it
    did not have, in its own opening sentence.

    So: no sentence in this function may assert a fact about the estate unless
    it is derived from `m` or `fs` on this run. If a clause cannot be computed,
    it does not belong in the verdict.
    """
    live = [(a, v) for a in m["accounts"] for v in a["vpcs"] if v["enis"] > 0]
    tiered = [v for _, v in live if len({"public", "private"} & set(v["tiers"])) == 2]
    highs = [x for x in fs if x["sev"] == "high"]
    unc = m.get("uncovered_accounts") or []
    exc = m.get("excluded_accounts") or []

    # card 1 -- the isolated tier is worth calling out, but only if one exists
    iso = [(a, v) for a, v in live if v["tiers"].get("isolated")]
    if iso:
        n = sum(len(v["tiers"]["isolated"]) for _, v in iso)
        where = iso[0][1]["name"] if len(iso) == 1 else f"{len(iso)} networks"
        seg_tail = (f' {n} subnet{"" if n == 1 else "s"} in {e(where)} '
                    f'{"has" if n == 1 else "have"} no default route at all.')
    else:
        seg_tail = " No subnet in the estate is fully isolated."
    seg_cls = "yes" if tiered and len(tiered) == len(live) else "part"

    # card 2 -- which layer actually enforces, read from the NACL rules
    filtering = [v for _, v in live if v["nacl_filters"]]
    if not filtering:
        ctl_cls, ctl_txt = "part", (
            "Partly. Security groups are the <strong>only</strong> enforcement layer — every "
            "network ACL on a live network is default allow-all.")
    elif len(filtering) == len(live):
        ctl_cls, ctl_txt = "yes", (
            "Two layers. Security groups <strong>and</strong> network ACLs both filter on every "
            f"one of the {len(live)} live networks.")
    else:
        ctl_cls, ctl_txt = "part", (
            f"Unevenly. Network ACLs filter on <strong>{len(filtering)} of {len(live)}</strong> "
            "live networks; on the rest, security groups are the only enforcement layer.")

    # card 3 -- severity count, then the scope position. The scope sentence is
    # the one that went wrong; it now reads straight off uncovered_accounts.
    if unc:
        scope_txt = (f' <strong>{len(unc)} account{"" if len(unc) == 1 else "s"}</strong> in the '
                     f'Organization {"was" if len(unc) == 1 else "were"} neither surveyed nor '
                     f'excluded, so the claim does not cover {"it" if len(unc) == 1 else "them"}.')
    elif exc:
        scope_txt = (f' Scope is closed: every account in the Organization was either surveyed or '
                     f'excluded by written decision ({len(exc)}).')
    else:
        scope_txt = " Scope is closed: every account in the Organization was surveyed."
    if highs:
        bnd_cls = "no"
        bnd_txt = (f'<strong>{len(highs)} high-severity finding'
                   f'{"" if len(highs) == 1 else "s"}</strong>.{scope_txt}')
    else:
        bnd_cls = "yes"
        bnd_txt = f"<strong>No high-severity findings</strong>.{scope_txt}"

    return f"""
<div class="verdict">
  <div class="vcard {seg_cls}"><p class="k">Segments exist</p><p><strong>{len(tiered)} of {len(live)}
    live VPCs</strong> carry a real public / private split derived from route tables, not from subnet
    names.{seg_tail}</p></div>
  <div class="vcard {ctl_cls}"><p class="k">Traffic between them is controlled</p><p>{ctl_txt}</p></div>
  <div class="vcard {bnd_cls}"><p class="k">Boundaries hold</p><p>{bnd_txt}</p></div>
</div>"""


def scope(m):
    unc = m.get("uncovered_accounts") or []
    exc = m.get("excluded_accounts") or []
    rows = "".join(
        f'<tr><td class="k mono">{e(x.get("Id"))}</td><td>{e(x.get("Name"))}</td>'
        f'<td><span class="pill p-flag">not surveyed</span></td></tr>' for x in unc)
    unc_block = ("" if not unc else f"""
  <h3 style="margin-top:24px">Accounts neither surveyed nor excluded</h3>
  <div class="scroller"><table><thead><tr><th>Account</th><th>Name</th><th>Status</th></tr></thead>
    <tbody>{rows}</tbody></table></div>
  <figcaption style="margin-top:11px">These exist in AWS Organizations, have no local profile, and
    carry no written exclusion — so nothing here describes them and nothing says they shouldn't.
    <b>Naming the gap is the evidence</b>; a silent omission is not.</figcaption>""")

    exc_rows = "".join(
        f'<tr><td class="k mono">{e(x.get("id"))}</td><td>{e(x.get("name"))}</td>'
        f'<td>{e(x.get("reason"))}</td><td class="mono">{e(x.get("decided"))} · '
        f'{e(x.get("decided_by"))}</td></tr>' for x in exc)
    exc_block = ("" if not exc else f"""
  <h3 style="margin-top:24px">Accounts deliberately out of scope</h3>
  <div class="scroller"><table><thead><tr><th>Account</th><th>Name</th><th>Reason</th>
    <th>Decision</th></tr></thead><tbody>{exc_rows}</tbody></table></div>
  <figcaption style="margin-top:11px">These are in the Organization but hold no Bitpool workload or
    data. <b>An exclusion with a written reason and a named decision-maker is a scope statement an
    auditor can test</b> — which is a different thing from an account nobody looked at.</figcaption>""")
    return f"""
<section id="scope">
  <div class="sec-head"><span class="sec-n">01</span><div><h2>What was surveyed</h2></div></div>
  <p class="lede">Scope claims are the first thing an auditor tests, so the sweep establishes its own
    boundary rather than assuming one. The account list comes from AWS Organizations, and every
    enabled region was probed — not just the one everything is expected to be in.</p>
  <div class="verdict">
    <div class="vcard yes"><p class="k">Regions</p><p><strong>{len(m['regions_enabled'])} enabled
      regions probed.</strong> {(
        'Every one holds at least a default VPC, so all ' + str(len(m['regions_enabled'])) +
        ' were swept in full.'
        if len(m['regions_with_vpcs']) == len(m['regions_enabled']) else
        'VPCs found in ' + str(len(m['regions_with_vpcs'])) + ': ' +
        e(', '.join(m['regions_with_vpcs'])) + '. The rest hold nothing at all.')}</p></div>
    <div class="vcard {'no' if unc else 'yes'}"><p class="k">Accounts</p><p>Organizations reports
      <strong>{m.get('org_account_count')} active accounts</strong>: {len(m['accounts'])} surveyed,
      {len(exc)} excluded by written decision{', ' + str(len(unc)) + ' neither' if unc else
      ' — and none unaccounted for'}.</p>
    </div>
    <div class="vcard yes"><p class="k">Reproducible</p><p>Dump digest
      <span class="mono">{e(m['provenance'].get('digest'))}</span> over
      {m['provenance'].get('files')} JSON files, zipped and attached alongside this page. The
      zip holds {m['provenance'].get('files_in_zip')} — the extra is
      <span class="mono">_manifest.json</span>, which carries this digest and so is not
      covered by it.</p></div>
  </div>
  {unc_block}
  {exc_block}
</section>"""


def diagrams(m):
    return f"""
<section id="topology">
  <div class="sec-head"><span class="sec-n">02</span><div><h2>Where the segments are</h2></div></div>
  <p class="lede">Every subnet below is classified by what its route table actually does, not by what
    its Name tag claims. A subnet called <span class="mono">private</span> that holds an internet
    gateway route is drawn as public here — that distinction is the whole point of the artefact.</p>
  <figure class="figure">
    <div class="scroller">{S.topology(m)}</div>
    <div class="key">
      <span><i style="background:var(--public)"></i>public — reachable via internet gateway</span>
      <span><i style="background:var(--private)"></i>private — NAT egress, no inbound</span>
      <span><i style="background:var(--isolated)"></i>isolated — no default route at all</span>
      <span><i style="background:var(--flag)"></i>flagged — default VPC carrying live workloads</span>
    </div>
    <figcaption><b>Only VPCs with live network interfaces are drawn.</b> The rest are provisioned but
      unused and appear in the inventory table instead, so the diagram shows the estate that operates
      rather than the estate that merely exists.</figcaption>
  </figure>
</section>

<section id="external">
  <div class="sec-head"><span class="sec-n">03</span><div><h2>Connections to external networks</h2>
    </div></div>
  <p class="lede">`DCF-22` asks for two things — system boundaries, drawn above, and connections to
    external networks, drawn here. A segment is only as separated as the paths leaving it, so this
    shows <em>every</em> way traffic crosses a boundary: internet ingress, peering both internal and
    to a vendor, administrative VPN, and private service endpoints.</p>
  <figure class="figure">
    <div class="scroller">{S.external_connections(m)}</div>
    <div class="key">
      <span><i style="background:var(--edge)"></i>internet ingress into a public tier</span>
      <span><i style="background:var(--private)"></i>internal peering, and private service endpoints</span>
      <span><i style="background:var(--vendor)"></i>leaves Bitpool's estate — vendor peering, VPN</span>
      <span><i style="background:var(--flag)"></i>flagged — environments that should not meet</span>
    </div>
    <figcaption>{_tagging_note(m)}
      <b>One caveat:</b> VPN presence is the only item here inferred rather than read from a definitive
      field — it is detected from security group naming, so treat it as indicative. Everything else
      comes from the resource records themselves.</figcaption>
  </figure>
</section>"""


def findings_html(fs):
    rows = "".join(f"""<div class="finding {x['sev']}">
  <div class="f-top"><span class="f-sev">{x['sev']}</span><span class="f-ctl">{e(x['ctl'])}</span></div>
  <p class="f-title">{e(x['title'])}</p><p>{e(x['body'])}</p>
  <p class="f-test">{e(x['test'])}</p></div>""" for x in fs)
    return f"""
<section id="findings">
  <div class="sec-head"><span class="sec-n">04</span><div><h2>What the data says</h2></div></div>
  <p class="lede">Each finding is derived by the generator from the dump — thresholds and comparisons
    in code, not judgement typed into a document. Re-run it after a fix and a resolved finding
    disappears on its own.</p>
  {rows}
</section>"""


def tables(m):
    inv = []
    for a in m["accounts"]:
        for v in sorted(a["vpcs"], key=lambda x: (-x["enis"], x["region"])):
            tiers = " ".join(f'<span class="pill {TIER_PILL[t]}">{t} {len(c)}</span>'
                             for t, c in sorted(v["tiers"].items()))
            fl = ('<span class="pill p-ok">' + str(v["flowlog"].get("TrafficType")).lower() + '</span>'
                  if v["flowlog"] else '<span class="pill p-flag">none</span>')
            state = ('<span class="pill p-flag">default · in use</span>' if v["default"] and v["enis"]
                     else ('<span class="pill p-warn">default · empty</span>' if v["default"]
                           else '<span class="pill p-ok">purpose-built</span>'))
            extra = []
            if v["endpoints"]:
                extra.append(f'{len(v["endpoints"])} endpoint(s)')
            if v["tgw"]:
                extra.append(f'{len(v["tgw"])} TGW')
            inv.append(f'<tr><td class="k">{e(v["name"])}</td><td class="mono">{e(v["cidr"])}</td>'
                       f'<td class="mono">{e(a["profile"])}</td><td class="mono">{e(v["region"])}</td>'
                       f'<td>{state}</td><td style="text-align:right">{v["enis"]}</td>'
                       f'<td>{tiers}</td><td>{fl}</td>'
                       f'<td class="mono">{e(", ".join(extra))}</td></tr>')
    peers = "".join(
        f'<tr><td class="k">{e(p["name"])}</td><td class="mono">{e(p["id"])}</td>'
        f'<td>{"<span class=\'pill p-vendor\'>vendor</span>" if p["external"] else "<span class=\'pill p-private\'>internal</span>"}</td>'
        f'<td class="mono">{e(p["a_cidr"])} &rarr; {e(p["b_cidr"])}</td>'
        f'<td class="mono">{e(p["a_owner"])} &rarr; {e(p["b_owner"])}</td>'
        f'<td><span class="pill p-ok">{e(p["state"])}</span></td></tr>' for p in m["peerings"])
    exps = []
    for a in m["accounts"]:
        for v in a["vpcs"]:
            for x in v["exposures"]:
                sev = "p-flag" if x["scheme"] == "internet-facing" else "p-warn"
                exps.append(f'<tr><td class="k">{e(", ".join(x["services"]))}</td>'
                            f'<td class="mono">{e(x["port"])}</td><td class="mono">{e(x["sg"])}</td>'
                            f'<td class="mono">{e(x["name"][:28])}</td>'
                            f'<td class="mono">{e(v["name"])}</td>'
                            f'<td class="mono">{e(a["profile"])}</td>'
                            f'<td><span class="pill {sev}">{e(x["scheme"])}</span></td></tr>')
    return f"""
<section id="evidence">
  <div class="sec-head"><span class="sec-n">05</span><div><h2>The evidence tables</h2></div></div>
  <p class="lede">These are the artefacts to attach against the control. They are the diagram's own
    source data rendered as tables, so the picture and the register can never disagree.</p>

  <h3>VPC inventory — every account, every region</h3>
  <div class="scroller" style="margin-bottom:30px"><table><thead><tr><th>VPC</th><th>CIDR</th>
    <th>Account</th><th>Region</th><th>Provenance</th><th style="text-align:right">Live ENIs</th>
    <th>Subnet tiers</th><th>Flow logs</th><th>Attached</th></tr></thead>
    <tbody>{''.join(inv)}</tbody></table></div>

  <h3>Peering — every route that leaves a segment</h3>
  <div class="scroller" style="margin-bottom:30px"><table><thead><tr><th>Name tag</th>
    <th>Connection</th><th>Kind</th><th>CIDRs</th><th>Accounts</th><th>State</th></tr></thead>
    <tbody>{peers}</tbody></table></div>

  <h3>Data-store ports open to 0.0.0.0/0</h3>
  <div class="scroller"><table><thead><tr><th>Service</th><th>Port</th><th>Security group</th>
    <th>Group name</th><th>VPC</th><th>Account</th><th>Attached to</th></tr></thead>
    <tbody>{''.join(exps)}</tbody></table></div>
  <figcaption style="margin-top:12px">Scheme is resolved by joining each security group to the load
    balancers that actually carry it, <b>in the same account and region</b> — v1.0 resolved this only
    for the production account and would have mislabelled anything found elsewhere.</figcaption>
</section>"""


def _tier_src():
    """The real subnet_tier(), read out of model.py at render time.

    The pack used to display a RETYPED paraphrase of this function. It had
    drifted: no `unrouted` branch, no `nat-` gateway test, and an indexing
    style the real code does not use. This is the one function the entire
    tier classification rests on, and the page stakes its credibility on
    showing it -- so it is read from the module rather than transcribed, and
    can no longer disagree with the code that actually ran.
    """
    import inspect
    try:
        src = inspect.getsource(M.subnet_tier)
    except (OSError, TypeError):
        return "  <i># subnet_tier() source unavailable at render time</i>"
    lines = [ln for ln in src.rstrip().splitlines()
             if '"""' not in ln]
    return "\n".join("  " + e(ln) for ln in lines)


def _tagging_note(m):
    """Whether every peering is name-tagged -- computed, not asserted."""
    ps = m.get("peerings") or []
    named = [x for x in ps if x.get("name")]
    if not ps:
        return "No peering connection leaves a segment in this estate."
    if len(named) == len(ps):
        return ("Every peering connection carries a descriptive Name tag, which is why the vendor "
                "links could be identified without guesswork \u2014 <b>that tagging discipline is "
                "itself evidence</b>.")
    return (f"<b>{len(named)} of {len(ps)} peering connections carry a descriptive Name tag.</b> "
            f"The untagged ones could not be identified as vendor or internal from the record "
            f"alone, so their classification here rests on the accounts either side rather than "
            f"on a stated purpose.")


PIPE_TMPL = """<b>collect.ps1</b>  <i># read-only. accounts from Organizations, every enabled region probed</i>
  aws organizations list-accounts          <i># scope comes from the org, not a literal</i>
  aws ec2 describe-regions                 <i># then probe each one for VPCs</i>
  <i>full sweep only where VPCs exist: vpcs, subnets, route-tables, security-groups,</i>
  <i>network-acls, flow-logs, peering, transit-gateways, endpoints, ENIs, load-balancers</i>
  <i>-&gt; writes _manifest.json: UTC timestamp, caller ARN, region list, SHA-256 digest</i>

<b>model.py</b>     <i># normalise. tier comes from the ROUTE TABLE, never the Name tag</i>
{TIER_SRC}

<b>findings.py</b>  <i># thresholds in code, so a fixed finding disappears by itself</i>
<b>svg.py</b>       <i># both diagrams laid out from the model. no hand-placed coordinates</i>
<b>render.py</b>    <i># emit the page, the Mermaid adjacency graph, and copy the dump alongside</i>"""


def pipeline(m):
    return f"""
<section id="pipeline">
  <div class="sec-head"><span class="sec-n">06</span><div><h2>How this page was made — and how it
    stays true</h2></div></div>
  <p class="lede">Nothing here was drawn by hand. A diagram anyone can edit is a diagram that drifts
    from the thing it describes, and nothing about the document itself reveals when it started to.
    This one is a pure function of a dated, hashed dump.</p>

  <div class="steps">
    <div class="step"><span class="n">01</span><h3>Collect</h3><p>Read-only
      <span class="mono">describe-*</span> calls. Scope is resolved from Organizations, so a new
      account cannot be silently missed.</p></div>
    <div class="step"><span class="n">02</span><h3>Model</h3><p>Normalise into VPCs, tiers, peerings
      and exposures. Tier comes from the route table, never the Name tag.</p></div>
    <div class="step"><span class="n">03</span><h3>Judge</h3><p>Findings computed from the model, so
      severity is reproducible rather than remembered.</p></div>
    <div class="step"><span class="n">04</span><h3>Render</h3><p>This page, the Mermaid adjacency
      graph, and the raw dump zipped &mdash; attached together as one evidence record.</p></div>
  </div>

  <pre>{PIPE_TMPL.replace('{TIER_SRC}', _tier_src())}</pre>

  <h3 style="margin-top:34px">The adjacency graph, also emitted as Mermaid</h3>
  <p>The diagrams above are SVG, laid out by this generator, so they render in any browser with no
    library. The same model is also written to <span class="mono">adjacency.md</span>, attached in
    Drata alongside this page and fenced so a reviewer opening it sees a diagram, not source. The source is shown below for reference —
    <strong>this page deliberately does not try to render it</strong>, because a standalone HTML file
    has no Mermaid library and a diagram that silently displays as code is worse than no diagram.</p>
  <div class="scroller" style="margin-bottom:10px"><pre>{e(mermaid_adjacency(m))}</pre></div>
  <div class="note"><strong>Two constraints encoded in the emitter.</strong> Mermaid
    <span class="mono">block-beta</span> renders as raw code and fails silently in every
    viewer tested, so only
    <span class="mono">flowchart</span> is ever produced. And every Mermaid graph ships as a
    <span class="mono">.md</span> file with a fenced block rather than a bare
    <span class="mono">.mmd</span> — a bare <span class="mono">.mmd</span> renders in none of the
    places these files are actually read.</div>

  <h3 style="margin-top:30px">What this unlocks</h3>
  <div class="steps">
    <div class="step"><span class="n">&rarr;</span><h3>Provenance by construction</h3><p>&ldquo;Is this
      current?&rdquo; stops being a matter of trust. The dump is timestamped, hashed, attributed to an
      identity, and attached in Drata alongside the pack it produced.</p></div>
    <div class="step"><span class="n">&rarr;</span><h3>Comparable between runs</h3><p>Both dumps are
      hashed, so any two runs can be compared directly. Bitpool does not operate a scheduled diff;
      annual renewal of this evidence in Drata is the cadence, and neither control requires more.</p></div>
    <div class="step"><span class="n">&rarr;</span><h3>Review becomes cheap</h3><p>An annual approval
      of a diagram nobody can verify is theatre. Approving a pack whose findings are computed from
      the dump is a real control, and it takes minutes.</p></div>
  </div>
</section>"""


def _slug(s):
    return "".join(ch if ch.isalnum() else "_" for ch in s)


def mermaid_adjacency(m):
    """A plain graph — the one shape Mermaid is genuinely good at."""
    L = ["flowchart LR"]
    ids, seen, links = {}, set(), []
    names = {v["id"]: v["name"] for a in m["accounts"] for v in a["vpcs"]}
    for p in m["peerings"]:
        for vid, cidr in ((p["a_vpc"], p["a_cidr"]), (p["b_vpc"], p["b_cidr"])):
            if vid in seen:
                continue
            seen.add(vid)
            if vid in names:
                ids[vid] = "N_" + _slug(names[vid])[:18]
                L.append(f'    {ids[vid]}["{names[vid]}<br/>{cidr}"]')
            else:
                ids[vid] = "N_atlas"
                L.append(f'    N_atlas(["MongoDB Atlas<br/>{cidr}"]):::vendor')
    for p in m["peerings"]:
        x, y = ids.get(p["a_vpc"]), ids.get(p["b_vpc"])
        if not (x and y):
            continue
        arrow = "-.->" if p["external"] else "---"
        L.append(f'    {x} {arrow}|"{p["name"]}"| {y}')
        links.append(p["name"].strip().lower() == "development to production")
    for i, flag in enumerate(links):
        if flag:
            L.append(f"    linkStyle {i} stroke:#A2352A,stroke-width:3px")
    L.append("    classDef vendor fill:#EDEAF4,stroke:#63548A,color:#463A62")
    return "\n".join(L)


def adjacency_md(m):
    """The adjacency graph as Markdown: heading, lede, fenced block, provenance footer.

    Fenced, not bare. See the module docstring for why .mmd was retired. This is
    now the only Markdown deliverable -- network-topology.md went with diagram.py
    in v1.2 -- so the shape is defined here rather than borrowed from a sibling.
    """
    p = m["provenance"]
    body = mermaid_adjacency(m)
    return (
        "# AWS Network Adjacency\n\n"
        "Every peering that leaves a segment, and the segment it reaches. Internal peerings are\n"
        "drawn as plain links; vendor peerings as dashed arrows from the vendor's own range.\n\n"
        "A link here is a **route that exists**, read from the peering records in the dump. It is\n"
        "not an observation of traffic \u2014 the sweep does not see traffic, and nothing below should\n"
        "be read as though it did.\n\n"
        "```mermaid\n" + body + "\n```\n\n"
        + M.provenance_footer(p)
    )


def build(dumpdir, outdir):
    m = M.build(dumpdir)
    fs = F.compute(m)
    os.makedirs(outdir, exist_ok=True)
    html = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Bitpool Network Segmentation</title>
{CSS}
</head>
<body>
{rail(m)}
<div class="wrap">
<header class="hero">
  <p class="eyebrow">Evidence pack &middot; A.8.22 segregation of networks &middot; DCF-748 &middot; DCF-22</p>
  <h1>What actually segments the Bitpool network</h1>
  <p class="standfirst">Generated from a read-only sweep of every account in the AWS Organization,
    across every enabled region. It answers the only question A.8.22 really asks — if something got
    in, what stops it moving — and it answers it from route tables and security group rules rather
    than from intent.</p>
  {verdict(m, fs)}
</header>
{scope(m)}
{diagrams(m)}
{findings_html(fs)}
{tables(m)}
{pipeline(m)}
<footer>
  <span>{e(m['provenance'].get('generator'))} &middot; dump {e(m['provenance'].get('collected_utc'))}
    &middot; digest {e(m['provenance'].get('digest'))}</span>
  <span>Read-only. No AWS resource was modified.</span>
</footer>
</div>
</body>
</html>"""
    open(os.path.join(outdir, "network-evidence-pack.html"), "w", encoding="utf-8").write(html)
    open(os.path.join(outdir, "adjacency.md"), "w", encoding="utf-8").write(adjacency_md(m))

    # archive the dump beside the output so the page is reproducible
    archive = os.path.join(outdir, "dump")
    if os.path.isdir(archive):
        shutil.rmtree(archive)
    shutil.copytree(dumpdir, archive)

    print("wrote network-evidence-pack.html  ", len(html), "bytes")
    print("wrote adjacency.md                ", len(adjacency_md(m)), "bytes")
    print("archived dump ->", archive, f"({len(os.listdir(archive))} files)")
    print("findings:", ", ".join(x["sev"] for x in fs))
    return m, fs


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
