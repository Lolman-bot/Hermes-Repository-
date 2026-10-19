"""Programmatic SVG layout for the two network diagrams.

Nothing here is hand-placed: every coordinate is computed from the model, so a new
VPC or a new peering changes the picture without anyone editing a drawing.
"""
import math

TIER_ORDER = ["public", "private", "isolated", "unrouted"]
TIER_LABEL = {"public": "public — IGW route",
              "private": "private — NAT egress only",
              "isolated": "isolated — no default route",
              "unrouted": "unrouted"}

W, GAP, PAD = 258, 18, 16
BAND, HEAD, ROWH, TIERHEAD = 46, 62, 17, 19
MAXCOLS = 3


def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def _card_h(v):
    h = HEAD
    for t in TIER_ORDER:
        if t in v["tiers"]:
            h += TIERHEAD + ROWH * len(v["tiers"][t]) + 18
    return h + 6


def _frame_w(n):
    return PAD * 2 + n * (W + GAP) - GAP


# ---------------------------------------------------------------- diagram 1
def topology(model):
    """Accounts -> VPCs -> subnet tiers, with the untrusted band above."""
    groups = []
    for a in model["accounts"]:
        vs = [v for v in a["vpcs"] if v["enis"] > 0]
        if vs:
            groups.append({"acct": a, "vpcs": vs, "cards": len(vs),
                           "ch": max(_card_h(v) for v in vs)})

    rows, cur = [], []
    for g in groups:
        if cur and sum(x["cards"] for x in cur) + g["cards"] > MAXCOLS:
            rows.append(cur)
            cur = []
        cur.append(g)
    if cur:
        rows.append(cur)

    total_w = max(_frame_w(MAXCOLS) + 16, 880)
    y = BAND + 30
    for row in rows:
        row_h = max(g["ch"] for g in row) + PAD * 2 + 26
        x = 8
        for g in row:
            g["_h"], g["_x"], g["_y"] = row_h, x, y
            g["_w"] = _frame_w(g["cards"])
            x += g["_w"] + 14
        y += row_h + 20
    H = y - 10

    o = [f'<svg viewBox="0 0 {total_w} {H}" role="img" '
         f'aria-label="AWS network topology: accounts, VPCs and their subnet tiers" '
         f'xmlns="http://www.w3.org/2000/svg">',
         '<defs><marker id="ar" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6.5" '
         'markerHeight="6.5" orient="auto"><path d="M0 0 L8 4 L0 8 z" fill="var(--edge)"/></marker>'
         '</defs>']

    o.append(f'<rect x="0" y="0" width="{total_w}" height="{BAND}" rx="7" class="s-untrust"/>')
    o.append('<text x="16" y="20" class="s-bandlab">UNTRUSTED</text>')
    o.append('<text x="16" y="36" class="s-bandval">0.0.0.0/0 — the public internet</text>')
    o.append(f'<text x="{total_w-16}" y="29" class="s-bandnote" text-anchor="end">'
             f'dashed arrows mark every tier it reaches directly</text>')

    for row in rows:
        for g in row:
            a, fx, fy, fw, fh = g["acct"], g["_x"], g["_y"], g["_w"], g["_h"]
            o.append(f'<rect x="{fx}" y="{fy}" width="{fw}" height="{fh}" rx="9" class="s-acct"/>')
            o.append(f'<text x="{fx+PAD}" y="{fy+20}" class="s-acctname">{esc(a["profile"])}</text>')
            o.append(f'<text x="{fx+fw-PAD}" y="{fy+20}" class="s-acctid" text-anchor="end">'
                     f'{esc(a["id"])}</text>')
            cx, cy = fx + PAD, fy + 30
            for v in g["vpcs"]:
                h = _card_h(v)
                flagged = v["default"] and v["enis"] > 0
                o.append(f'<rect x="{cx}" y="{cy}" width="{W}" height="{h}" rx="7" '
                         f'class="{"s-vpc-flag" if flagged else "s-vpc"}"/>')
                o.append(f'<text x="{cx+13}" y="{cy+21}" class="s-vpcname">{esc(v["name"][:24])}</text>')
                o.append(f'<text x="{cx+13}" y="{cy+39}" class="s-vpccidr">{esc(v["cidr"])}</text>')
                o.append(f'<text x="{cx+W-13}" y="{cy+39}" class="s-vpceni" text-anchor="end">'
                         f'{esc(v.get("region", ""))} &#183; {v["enis"]} interfaces</text>')
                if flagged:
                    o.append(f'<text x="{cx+W-13}" y="{cy+21}" class="s-chip" text-anchor="end">'
                             f'DEFAULT VPC</text>')
                ty = cy + HEAD
                for t in TIER_ORDER:
                    if t not in v["tiers"]:
                        continue
                    cidrs = v["tiers"][t]
                    bh = TIERHEAD + ROWH * len(cidrs) + 6
                    o.append(f'<rect x="{cx+9}" y="{ty}" width="{W-18}" height="{bh}" rx="5" '
                             f'class="s-t-{t}"/>')
                    o.append(f'<rect x="{cx+9}" y="{ty}" width="3.5" height="{bh}" rx="1.75" '
                             f'class="s-b-{t}"/>')
                    o.append(f'<text x="{cx+21}" y="{ty+14}" class="s-tierlab s-l-{t}">'
                             f'{esc(TIER_LABEL[t])}</text>')
                    for i, c in enumerate(cidrs):
                        o.append(f'<text x="{cx+21}" y="{ty+TIERHEAD+13+i*ROWH}" '
                                 f'class="s-cidr">{esc(c)}</text>')
                    if t == "public":
                        o.append(f'<line x1="{cx+W/2}" y1="{fy-13}" x2="{cx+W/2}" y2="{ty-4}" '
                                 f'class="s-igw" marker-end="url(#ar)"/>')
                    ty += bh + 12
                cx += W + GAP
    o.append("</svg>")
    return "\n".join(o)


# ---------------------------------------------------------------- diagram 2
def external_connections(model):
    """Every way traffic crosses a boundary — DCF-22's "connections to external networks".

    Four kinds, and all four must appear or the control's second limb is only
    partly evidenced: internet ingress, peering (internal and vendor), VPN
    administrative ingress, and service endpoints including PrivateLink.
    """
    live = [(a, v) for a in model["accounts"] for v in a["vpcs"] if v["enis"] > 0]
    if not live:
        return '<svg viewBox="0 0 100 40" xmlns="http://www.w3.org/2000/svg"></svg>'

    VW, PAD, GAP = 196, 16, 16
    W = max(PAD * 2 + len(live) * (VW + GAP) - GAP, 900)
    BAND_Y, BAND_H = 8, 46
    ARC_TOP, VPC_Y, VPC_H = 66, 150, 84
    EXT_Y, EXT_H = 306, 78
    H = EXT_Y + EXT_H + 46

    pos = {}
    for i, (a, v) in enumerate(live):
        pos[v["id"]] = PAD + i * (VW + GAP) + VW / 2

    o = [f'<svg viewBox="0 0 {W} {H}" role="img" '
         f'aria-label="Connections to external networks: internet, peering, VPN and service endpoints" '
         f'xmlns="http://www.w3.org/2000/svg">',
         '<defs><marker id="ax" viewBox="0 0 8 8" refX="7" refY="4" markerWidth="6" markerHeight="6" '
         'orient="auto"><path d="M0 0 L8 4 L0 8 z" fill="var(--edge)"/></marker></defs>']

    # --- untrusted band ---------------------------------------------------
    o.append(f'<rect x="0" y="{BAND_Y}" width="{W}" height="{BAND_H}" rx="7" class="s-untrust"/>')
    o.append(f'<text x="16" y="{BAND_Y+20}" class="s-bandlab">UNTRUSTED</text>')
    o.append(f'<text x="16" y="{BAND_Y+36}" class="s-bandval">0.0.0.0/0 — the public internet</text>')
    o.append(f'<text x="{W-16}" y="{BAND_Y+29}" class="s-bandnote" text-anchor="end">'
             f'solid arrows enter a public tier directly</text>')

    # --- internal peering, arced above the row ----------------------------
    known = {v["id"] for _, v in live}
    for p in model["peerings"]:
        if p.get("external"):
            continue
        x1, x2 = pos.get(p["a_vpc"]), pos.get(p["b_vpc"])
        if not (x1 and x2):
            continue
        flag = p["name"].strip().lower() == "development to production"
        dip = ARC_TOP + 18 + (abs(x1 - x2) / W) * 34
        o.append(f'<path d="M{x1:.0f} {VPC_Y} Q{(x1+x2)/2:.0f} {dip:.0f} {x2:.0f} {VPC_Y}" '
                 f'class="{"e-flag" if flag else "e-int"}"/>')
        if flag:
            o.append(f'<text x="{(x1+x2)/2:.0f}" y="{dip-6:.0f}" class="e-lab-flag" '
                     f'text-anchor="middle">routed both ways</text>')

    # --- the VPC row ------------------------------------------------------
    for a, v in live:
        cx = pos[v["id"]]
        x = cx - VW / 2
        flagged = v["default"]
        o.append(f'<rect x="{x:.0f}" y="{VPC_Y}" width="{VW}" height="{VPC_H}" rx="7" '
                 f'class="{"s-vpc-flag" if flagged else "s-vpc"}"/>')
        o.append(f'<text x="{cx:.0f}" y="{VPC_Y+24}" class="s-vpcname" text-anchor="middle">'
                 f'{esc(v["name"][:24])}</text>')
        o.append(f'<text x="{cx:.0f}" y="{VPC_Y+42}" class="s-vpccidr" text-anchor="middle">'
                 f'{esc(v["cidr"])}</text>')
        o.append(f'<text x="{cx:.0f}" y="{VPC_Y+59}" class="n-sub" text-anchor="middle">'
                 f'{esc(a["profile"])}</text>')
        pub = len(v["tiers"].get("public", []))
        o.append(f'<text x="{cx:.0f}" y="{VPC_Y+74}" class="n-sub" text-anchor="middle">'
                 f'{pub} public subnet{"" if pub == 1 else "s"}</text>')
        if pub:
            o.append(f'<line x1="{cx:.0f}" y1="{BAND_Y+BAND_H}" x2="{cx:.0f}" y2="{VPC_Y-4}" '
                     f'class="s-igw" marker-end="url(#ax)" stroke-dasharray="0"/>')

    # --- external systems below -------------------------------------------
    ext = []
    vendor = [p for p in model["peerings"] if p.get("external")]
    if vendor:
        touch = [p["b_vpc"] if p["b_vpc"] in known else p["a_vpc"] for p in vendor]
        ext.append({"label": "MongoDB Atlas", "sub": f'vendor peering · {vendor[0]["a_owner"]}',
                    "cidr": vendor[0]["a_cidr"], "touch": [t for t in touch if t in known],
                    "cls": "n-ext", "edge": "e-ext"})
    vpn_vpcs = [v["id"] for _, v in live if v.get("vpn")]
    if vpn_vpcs:
        ext.append({"label": "VPN — administrative", "sub": "inferred from group naming",
                    "cidr": "remote operators", "touch": vpn_vpcs,
                    "cls": "n-ext", "edge": "e-ext"})
    ep_vpcs = [v["id"] for _, v in live if v.get("endpoints")]
    if ep_vpcs:
        svc = sorted({e["service"] for _, v in live for e in v.get("endpoints", [])})
        pl = [s for s in svc if s.startswith("vpce-svc-")]
        shown = [s for s in svc if not s.startswith("vpce-svc-")]
        lbl = ", ".join(shown[:3]) + (f" +{len(pl)} PrivateLink" if pl else "")
        ext.append({"label": "AWS service endpoints", "sub": "PrivateLink — no internet path",
                    "cidr": lbl or "endpoints", "touch": ep_vpcs,
                    "cls": "n-int", "edge": "e-int"})

    if ext:
        EW = min(258, (W - PAD * 2 - GAP * (len(ext) - 1)) // len(ext))
        span = len(ext) * EW + (len(ext) - 1) * GAP
        start = (W - span) / 2
        for i, e in enumerate(ext):
            ex = start + i * (EW + GAP)
            ecx = ex + EW / 2
            for t in e["touch"]:
                if t in pos:
                    o.append(f'<path d="M{ecx:.0f} {EXT_Y} C{ecx:.0f} {EXT_Y-46} '
                             f'{pos[t]:.0f} {VPC_Y+VPC_H+46} {pos[t]:.0f} {VPC_Y+VPC_H}" '
                             f'class="{e["edge"]}"/>')
            o.append(f'<rect x="{ex:.0f}" y="{EXT_Y}" width="{EW}" height="{EXT_H}" rx="7" '
                     f'class="{e["cls"]}"/>')
            o.append(f'<text x="{ecx:.0f}" y="{EXT_Y+25}" class="n-lab" text-anchor="middle">'
                     f'{esc(e["label"])}</text>')
            o.append(f'<text x="{ecx:.0f}" y="{EXT_Y+44}" class="n-cidr" text-anchor="middle">'
                     f'{esc(e["cidr"][:34])}</text>')
            o.append(f'<text x="{ecx:.0f}" y="{EXT_Y+62}" class="n-sub" text-anchor="middle">'
                     f'{esc(e["sub"][:38])}</text>')

    o.append("</svg>")
    return "\n".join(o)
