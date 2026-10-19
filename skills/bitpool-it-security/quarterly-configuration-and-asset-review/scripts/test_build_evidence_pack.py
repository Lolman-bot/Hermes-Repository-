#!/usr/bin/env python3
"""Tests for build_evidence_pack.py -- the properties that make the pack evidence.

Each test guards a property whose failure would be quiet: the pack would still build,
still look authoritative, and be wrong.

    reproducible     identical inputs give byte-identical output, including from a copy
                     of the tree at a different absolute path, and with the pack written
                     into the folder it describes
    zero network     the only `http` in the page is the SVG namespace; no script, link,
                     @import, url() or src= at all -- and, judged on the PARSED page (so a
                     character reference inside an attribute is seen as the browser sees
                     it), no element, attribute, handler or stylesheet that could fetch,
                     even when every input field carries hostile markup
    complete         a manifest recording incidents (a dump placed with
                     --accept-incomplete) is a high finding, shown in the header, the rail
                     and section 01; a missing incidents list reads NOT RECORDED, never
                     clean; tool.git_dirty is shown beside the commit it qualifies
    hashed           every input file's sha256 appears in the page HEADER, and the
                     advertised `sha256sum ... | sha256sum` recomputes the input digest
    escaped          a policy named <script>alert(1)</script> and values carrying & and
                     quotes print as text -- in the rows AND in differ output
    baseline         with --baseline the differ is run through its CLI with --format json
                     and its events render; without it the page says no comparison was made
    provenance       a missing manifest refuses by default, and with the override the page
                     says NOT RECORDED and never invents a collection time
    refusals         v1 rows, rows from a different dump, a self-comparison and a failing
                     differ all exit 2 and write nothing

The differ is stubbed: the tests pin this builder's contract with the differ's CLI, not the
differ's own semantics, which diff_baseline.py's tests own.

Pure stdlib. Run through WSL:
    python3 -m unittest discover -s scripts -p 'test_build_evidence_pack.py' -v
    python3 scripts/test_build_evidence_pack.py
"""

import hashlib
from html import unescape as html_unescape
from html.parser import HTMLParser
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
BUILDER = os.path.join(HERE, "build_evidence_pack.py")
sys.path.insert(0, HERE)
import build_evidence_pack as bep  # noqa: E402

EVIL_NAME = "<script>alert(1)</script> Firewall"
EVIL_VALUE = 'A & B "quoted" \'single\''
POLICY_A = "11111111-aaaa-4aaa-8aaa-111111111111"
POLICY_B = "22222222-bbbb-4bbb-8bbb-222222222222"
CONFIG_C = "33333333-cccc-4ccc-8ccc-333333333333"
EXCLUDED = "44444444-dddd-4ddd-8ddd-444444444444"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sha_file(p):
    with open(p, "rb") as f:
        return sha(f.read())


def write_bytes(path, b):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(b)


def jbytes(obj):
    return (json.dumps(obj, indent=2, sort_keys=True) + "\n").encode("utf-8")


def mk_row(platform, collection, oid, oname, setting_id, raw, rid, display=None, mode=None):
    name_row = setting_id == "@displayName"
    return {
        "row_key": "%s|%s|%s" % (collection, oid.lower(), setting_id.lower()),
        "id": rid,
        "platform": platform,
        "collection": collection,
        "object_type": "#microsoft.graph.deviceManagementConfigurationPolicy",
        "object_id": oid,
        "object_name": oname,
        "setting_id": setting_id,
        "setting_name": "Policy name" if name_row else setting_id,
        "required_value": raw,
        "display_value": display if display is not None else raw,
        "mode": mode or ("identity" if name_row else "enforced"),
        "enforced_at": "Intune > %s > %s" % (collection, oname),
        "verify": "$.%s[0].settings[0]" % collection,
    }


def fixture_objects(name_a=EVIL_NAME, value_b="device_vendor_msft_bitlocker_true",
                    label_a="Enabled"):
    """Three assigned objects on two platforms, one excluded object."""
    return [
        ("windows10", "configurationPolicies", POLICY_A, name_a, "WIN",
         [("device_vendor_msft_firewall_enable", "device_vendor_msft_firewall_enable_true",
           label_a),
          ("device_vendor_msft_policy_config_note", EVIL_VALUE, None)]),
        ("windows10", "configurationPolicies", POLICY_B, "Disk Encryption", "WIN",
         [("device_vendor_msft_bitlocker_requiredeviceencryption", value_b, None)]),
        ("macOS", "deviceConfigurations", CONFIG_C, "Mac Restrictions", "MAC",
         [("airDropBlocked", True, None)]),
    ]


def make_folder(dumps, date, objects=None, manifest=True, definitions=True, readable=True,
                truncate=False, generator_version="2.0", tamper_rows_sha=False,
                manifest_overrides=None, collector_upn="collector@example.com",
                unbaselined_marker="s1"):
    """Write one dated folder to contract v2 and return its path."""
    objects = objects if objects is not None else fixture_objects()
    folder = os.path.join(dumps, date)
    os.makedirs(folder, exist_ok=True)

    cps, dcs = [], []
    for platform, coll, oid, oname, _, settings in objects:
        if coll == "configurationPolicies":
            ss = [{"id": str(i), "settingInstance": {"settingDefinitionId": sid,
                                                     "choiceSettingValue": {"value": val}}}
                  for i, (sid, val, _) in enumerate(settings)]
            cps.append({"id": oid, "name": oname, "platforms": platform, "isAssigned": True,
                        "assignments": [{"target": {}}], "settings": ss,
                        "settingCount": len(ss) + (5 if truncate else 0)})
        else:
            o = {"id": oid, "displayName": oname, "@odata.type": "#microsoft.graph.x",
                 "assignments": [{"target": {}}]}
            for sid, val, _ in settings:
                o[sid] = val
            dcs.append(o)
    cps.append({"id": EXCLUDED, "name": "TESTING Unassigned Thing", "platforms": "windows10",
                "isAssigned": False, "assignments": [], "settings": [], "settingCount": 0})
    raw = {"configurationPolicies": cps, "deviceConfigurations": dcs,
           "deviceCompliancePolicies": [],
           # outside the baseline: varying it changes the dump's hash but no row
           "deviceManagementScripts": [{"id": unbaselined_marker}]}
    raw_b = jbytes(raw)
    write_bytes(os.path.join(folder, bep.RAW_EXPORT), raw_b)
    files = {bep.RAW_EXPORT: {"sha256": sha(raw_b), "bytes": len(raw_b)}}

    if readable:
        rb = jbytes({"readable": True, "configurationPolicies": cps})
        write_bytes(os.path.join(folder, bep.RAW_READABLE), rb)
        files[bep.RAW_READABLE] = {"sha256": sha(rb), "bytes": len(rb)}
    defs_sha = None
    if definitions:
        defs = {"_unresolved": []}
        for _, coll, _, _, _, settings in objects:
            if coll == "configurationPolicies":
                for sid, _, _ in settings:
                    defs[sid] = {"id": sid, "displayName": "Label for " + sid}
        db = jbytes(defs)
        write_bytes(os.path.join(folder, bep.DEFINITIONS), db)
        files[bep.DEFINITIONS] = {"sha256": sha(db), "bytes": len(db)}
        defs_sha = sha(db)

    rows, counts, n = [], {}, {}
    for platform, coll, oid, oname, prefix, settings in objects:
        def nid():
            n[prefix] = n.get(prefix, 0) + 1
            return "BP-%s-%04d" % (prefix, n[prefix])
        rows.append(mk_row(platform, coll, oid, oname, "@displayName", oname, nid()))
        for sid, val, disp in settings:
            rows.append(mk_row(platform, coll, oid, oname, sid, val, nid(), display=disp))
        counts.setdefault(platform, {}).setdefault(coll, 0)
        counts[platform][coll] += 1 + len(settings)
    doc = {"meta": {
        "generator_version": generator_version,
        "generated_from": bep.RAW_EXPORT,
        "generated_at": "%sT00:00:00Z" % date,
        "source_sha256": ("0" * 64) if tamper_rows_sha else sha(raw_b),
        "definitions_sha256": defs_sha,
        "display_resolution": {"mode": "catalog" if definitions else "none",
                               "resolved": 1 if definitions else 0, "unresolved": 0},
        "row_count": len(rows),
        "counts": counts,
        "scope": {"assigned_only": True,
                  "excluded_objects": [{"collection": "configurationPolicies",
                                        "object_id": EXCLUDED,
                                        "name": "TESTING Unassigned Thing",
                                        "platform": "windows10", "reason": "unassigned"}],
                  "assignment_disagreements": []}},
        "rows": rows}
    write_bytes(os.path.join(folder, bep.ROWS), jbytes(doc))

    if manifest:
        man = {"schema": 1, "collected_at_utc": "%sT03:14:15Z" % date, "collection_date": date,
               "collector": {"upn": collector_upn, "object_id": "oid-1234",
                             "source": "access-token claims"},
               "tenant_id": "tenant-0000", "client_id": "client-0000",
               "tool": {"name": "export-intune-config.sh", "git_commit": "abc1234",
                        "git_dirty": False},
               "files": files, "incidents": []}
        man.update(manifest_overrides or {})
        write_bytes(os.path.join(folder, bep.MANIFEST), jbytes(man))
    return folder


STUB_DIFFER = r'''
import json, os, sys
here = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(here, "argv.json"), "w") as f:
    json.dump(sys.argv[1:], f)
with open(os.path.join(here, "spec.json")) as f:
    spec = json.load(f)
sys.stderr.write(spec.get("stderr", ""))
sys.stdout.write(spec.get("stdout", ""))
sys.exit(spec["exit"])
'''


def standard_page(std_id, title, version="1.0", approver="Approver Name",
                  approved_on="2026-09-26", effective_from=None, ratified_from="—",
                  rows_cited=None, newline="\r\n", table_after_block=False):
    """A standard page shaped the way ratify leaves one: frontmatter, the approval table,
    then a generated block that cites the rows it was rendered from (rows_cited, the
    'dumps/DATE/baseline-rows.json (sha256 ...)' text) and carries a decoy
    '| Standard ID |' row the pack must not read."""
    table = ["| Field | Value |", "|---|---|",
             "| Standard ID | %s |" % std_id, "| Version | %s |" % version,
             "| Approved by | %s |" % approver, "| Approved on | %s |" % approved_on,
             "| Effective from | %s |" % (effective_from or approved_on),
             "| Ratified from | %s |" % ratified_from, "| Next review | Quarterly |", ""]
    block = ["<!-- GENERATED:START -->", ""]
    if rows_cited:
        block += ["<!-- Generated by run_config_cycle.py ratify from %s. Do not edit. -->"
                  % rows_cited, ""]
    block += ["| Standard ID | DECOY |", "<!-- GENERATED:END -->", ""]
    head = ["---", "type: Standard", "title: %s" % title, "status: active", "---", "",
            "# %s" % title, ""]
    lines = head + (block + table if table_after_block else table + block)
    return newline.join(lines).encode("utf-8")


def ratify_fixture(dumps, date, pages=True, **cells):
    """Point RATIFIED at a folder and write the three standard pages approving it, citing
    the folder's raw export by sha256 as ratify does. cells overrides page values."""
    write_bytes(os.path.join(dumps, "RATIFIED"), ("%s\n" % date).encode())
    if not pages:
        return
    raw = os.path.join(dumps, date, bep.RAW_EXPORT)
    rows = os.path.join(dumps, date, bep.ROWS)
    kw = {"ratified_from": "dumps/%s (sha256 %s)" % (date, sha_file(raw)[:16]),
          "rows_cited": "dumps/%s/%s (sha256 %s)" % (date, bep.ROWS, sha_file(rows)[:16])}
    kw.update(cells)
    for _platform, fname, std_id in bep.PAGES:
        write_bytes(os.path.join(os.path.dirname(dumps), fname),
                    standard_page(std_id, fname, **kw))


def stub_differ(tmp, exit_code, report=None, stdout=None, stderr=""):
    d = os.path.join(tmp, "stub")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "diff_baseline.py"), "w") as f:
        f.write(STUB_DIFFER)
    out = stdout if stdout is not None else json.dumps(report or {})
    with open(os.path.join(d, "spec.json"), "w") as f:
        json.dump({"exit": exit_code, "stdout": out, "stderr": stderr}, f)
    return os.path.join(d, "diff_baseline.py")


def stub_argv(differ):
    with open(os.path.join(os.path.dirname(differ), "argv.json")) as f:
        return json.load(f)


# The v2 differ's counted classes (diff_baseline.COUNTED). Mirrored, not imported: the
# builder may only depend on the differ's CLI output.
COUNTED = ("integrity", "renamed", "reassigned", "object_removed", "object_added",
           "changed", "removed", "added")

# Stub report in the v2 shape. `changed` deliberately carries the v1 nested-`row` shape,
# so the fallback lookup in pick() stays covered.
DIFF_REPORT = {
    "diff_version": "2.0", "row_contract": 2,
    "summary": dict({k: 0 for k in COUNTED}, added=1, removed=1, changed=1, renamed=1),
    "difference_count": 4, "unchanged_rows": 3,
    "warnings": [],
    "baseline": {"row_count": 7}, "current": {"row_count": 7},
    "renamed": [{"object_id": POLICY_A, "collection": "configurationPolicies",
                 "from": "Old <b>bold</b> name", "to": EVIL_NAME,
                 "unaffected_settings": 2, "total_settings": 2}],
    "changed": [{"row": {"id": "BP-WIN-0005", "object_name": "Disk Encryption",
                         "setting_id": "device_vendor_msft_bitlocker_requiredeviceencryption"},
                 "from": "device_vendor_msft_bitlocker_true",
                 "to": "device_vendor_msft_bitlocker_false"}],
    "added": [{"id": "BP-MAC-0002", "object_name": "Mac Restrictions",
               "setting_id": "cameraBlocked", "required_value": True}],
    "removed": [{"id": "BP-MAC-0009", "object_name": "Mac Restrictions",
                 "setting_id": "siriBlocked", "required_value": 'x & "y"'}],
    "reassigned": [], "object_added": [], "object_removed": [], "integrity": [],
    "not_counted": {"display_only": [], "excluded_added": [], "excluded_removed": []},
}
NO_DIFF_REPORT = {
    "diff_version": "2.0", "row_contract": 2,
    "summary": {k: 0 for k in COUNTED},
    "difference_count": 0, "unchanged_rows": 7, "warnings": [],
    "baseline": {"row_count": 7}, "current": {"row_count": 7},
    "not_counted": {"display_only": [], "excluded_added": [], "excluded_removed": []},
}


def run(*args):
    p = subprocess.run([sys.executable, BUILDER] + list(args), capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def read(p):
    with open(p, "rb") as f:
        return f.read()


def header(page):
    s = page.decode("utf-8")
    return s[s.index('<header class="hero">'):s.index("</header>")]


def edit_manifest(folder, fn):
    """Rewrite a folder's manifest through fn(manifest) -> None."""
    mp = os.path.join(folder, bep.MANIFEST)
    with open(mp) as fh:
        man = json.load(fh)
    fn(man)
    write_bytes(mp, jbytes(man))


def section(page, sid):
    s = page.decode("utf-8") if isinstance(page, bytes) else page
    start = s.index('<section id="%s">' % sid)
    return s[start:s.index("</section>", start)]


# Written independently of build_evidence_pack.audit_offline, so a defect in one is not
# shared by the other. The tag list is an ALLOWLIST: exactly what the builder emits today.
ALLOWED_TAGS = {"b", "body", "dd", "div", "dl", "dt", "figcaption", "figure", "footer",
                "h1", "h2", "h3", "h4", "head", "header", "html", "i", "meta", "p", "pre",
                "rect", "section", "span", "strong", "style", "svg", "table", "tbody", "td",
                "text", "th", "thead", "title", "tr"}
RESOURCE_ATTRS = {"src", "href", "srcset", "action", "formaction", "xlink:href", "poster",
                  "data", "background", "ping", "codebase", "archive", "manifest"}
CSS_FETCH = re.compile(r"url\s*\(|@import|image-set\s*\(|expression\s*\(", re.I)
SVG_NS = "http://www.w3.org/2000/svg"


class FetchScan(HTMLParser):
    """html.parser decodes character references in attribute values, so an attribute
    holding `&#x68;ttps://...` is judged as the `https://...` a browser would fetch."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.found, self.in_style = [], False

    def handle_starttag(self, tag, attrs):
        if tag not in ALLOWED_TAGS:
            self.found.append("tag <%s>" % tag)
        self.in_style = self.in_style or tag == "style"
        for name, val in attrs:
            val = val or ""
            if name in RESOURCE_ATTRS:
                self.found.append("attr %s on <%s>" % (name, tag))
            if name.startswith("on"):
                self.found.append("handler %s on <%s>" % (name, tag))
            if tag == "meta" and name == "http-equiv":
                self.found.append("meta http-equiv")
            if name == "style" and CSS_FETCH.search(val):
                self.found.append("css in style= on <%s>" % tag)
            if "http" in val.lower() and (tag, name, val) != ("svg", "xmlns", SVG_NS):
                self.found.append("url in %s= on <%s>" % (name, tag))

    def handle_endtag(self, tag):
        if tag == "style":
            self.in_style = False

    def handle_data(self, data):
        if self.in_style and (CSS_FETCH.search(data) or "http" in data.lower()):
            self.found.append("css in <style>")


def fetch_scan(page):
    s = page.decode("utf-8") if isinstance(page, bytes) else page
    p = FetchScan()
    p.feed(s)
    p.close()
    return p.found


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="bep-test-")
        self.dumps = os.path.join(self.tmp, "repo", "dumps")
        os.makedirs(self.dumps)
        self.out = os.path.join(self.tmp, "out", "evidence-pack.html")

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def build(self, folder, *extra, expect=0):
        code, out, err = run("--folder", folder, "--out", self.out, *extra)
        self.assertEqual(code, expect, "exit %d\nstdout:\n%s\nstderr:\n%s" % (code, out, err))
        return code, out, err


class Reproducible(Base):
    def test_identical_inputs_give_identical_bytes(self):
        f = make_folder(self.dumps, "2026-09-25")
        self.build(f)
        first = read(self.out)
        self.build(f)
        self.assertEqual(first, read(self.out))

    def test_relocated_tree_gives_identical_bytes(self):
        """No absolute path, hostname or clock may leak into the page."""
        f = make_folder(self.dumps, "2026-09-25")
        self.build(f)
        first = read(self.out)
        moved = os.path.join(self.tmp, "elsewhere", "deeper", "dumps")
        shutil.copytree(self.dumps, moved)
        self.build(os.path.join(moved, "2026-09-25"))
        self.assertEqual(first, read(self.out))
        self.assertNotIn(self.tmp.encode(), first)

    def test_pack_written_into_its_own_folder_is_not_an_input(self):
        f = make_folder(self.dumps, "2026-09-25")
        inside = os.path.join(f, "evidence-pack.html")
        self.assertEqual(run("--folder", f, "--out", inside)[0], 0)
        first = read(inside)
        self.assertEqual(run("--folder", f, "--out", inside)[0], 0)
        self.assertEqual(first, read(inside))

    def test_identical_with_baseline(self):
        make_folder(self.dumps, "2026-06-24")
        f = make_folder(self.dumps, "2026-09-25")
        differ = stub_differ(self.tmp, 1, DIFF_REPORT)
        args = ("--baseline", os.path.join(self.dumps, "2026-06-24"), "--differ", differ)
        self.build(f, *args)
        first = read(self.out)
        self.build(f, *args)
        self.assertEqual(first, read(self.out))


class ZeroNetwork(Base):
    def assert_offline(self, page):
        s = page.decode("utf-8")
        hits = re.findall(r"https?://[^\s\"'<>)]*", s, flags=re.I)
        self.assertTrue(hits, "expected the SVG namespace to be present")
        self.assertEqual(set(hits), {"http://www.w3.org/2000/svg"}, hits)
        # the namespace is the only place the four letters may appear at all
        self.assertEqual(s.lower().count("http"), len(hits))
        low = s.lower()
        for bad in ("<script", "<link", "@import", "url(", " src=", "<iframe", "<object",
                    "<embed", "fetch(", "xmlhttprequest"):
            self.assertNotIn(bad, low, bad)
        # the byte checks above cannot see a decoded attribute; the parse can
        self.assertEqual(fetch_scan(s), [])

    def test_no_network_reference_without_baseline(self):
        self.build(make_folder(self.dumps, "2026-09-25"))
        self.assert_offline(read(self.out))

    def test_no_network_reference_with_baseline(self):
        make_folder(self.dumps, "2026-06-24")
        f = make_folder(self.dumps, "2026-09-25")
        self.build(f, "--baseline", os.path.join(self.dumps, "2026-06-24"),
                   "--differ", stub_differ(self.tmp, 1, DIFF_REPORT))
        self.assert_offline(read(self.out))

    def test_url_valued_settings_do_not_break_the_grep(self):
        """Real tenant values carry URLs (an SSO extension's login.microsoftonline.com
        list on 2026-09-24). They are text, not references -- the page must keep the
        literal-grep audit true AND still show the exact value."""
        objs = fixture_objects(name_a="Proxy HTTP://corp.example")
        b = list(objs[1])
        urls = ["https://login.microsoftonline.com", "https://evil.example/x.css"]
        b[5] = b[5] + [("com.apple.extensiblesso_urls", urls, None)]
        objs[1] = tuple(b)
        self.build(make_folder(self.dumps, "2026-09-25", objects=objs))
        page = read(self.out)
        self.assert_offline(page)
        shown = html_unescape(page.decode("utf-8"))
        self.assertIn(json.dumps(urls, sort_keys=True), shown)
        self.assertIn("Proxy HTTP://corp.example", shown)

    def test_complete_document(self):
        self.build(make_folder(self.dumps, "2026-09-25"))
        s = read(self.out).decode("utf-8")
        self.assertTrue(s.startswith("<!doctype html>\n<html lang=\"en\">"))
        self.assertIn("<title>Intune Hardening Evidence</title>", s)
        self.assertTrue(s.rstrip().endswith("</html>"))


class Hashed(Base):
    def test_every_input_sha256_is_in_the_header(self):
        make_folder(self.dumps, "2026-06-24")
        f = make_folder(self.dumps, "2026-09-25")
        self.build(f, "--baseline", os.path.join(self.dumps, "2026-06-24"),
                   "--differ", stub_differ(self.tmp, 1, DIFF_REPORT))
        head = header(read(self.out))
        expected = [os.path.join(f, n) for n in (bep.RAW_EXPORT, bep.RAW_READABLE,
                                                 bep.DEFINITIONS, bep.MANIFEST, bep.ROWS)]
        expected += [os.path.join(self.dumps, "2026-06-24", n)
                     for n in (bep.RAW_EXPORT, bep.MANIFEST, bep.ROWS)]
        for p in expected:
            self.assertIn(sha_file(p), head, p)

    def test_sha256sum_recomputes_the_advertised_digest(self):
        if not shutil.which("sha256sum"):
            self.skipTest("sha256sum not available")
        f = make_folder(self.dumps, "2026-09-25")
        _, out, _ = self.build(f)
        digest = re.search(r"input digest ([0-9a-f]{64})", out).group(1)
        page = read(self.out).decode("utf-8")
        files = re.search(r"sha256sum (.*?) \\\n    \| sha256sum", page, re.S).group(1)
        names = [x.strip() for x in files.replace("\\", " ").split()]
        p1 = subprocess.run(["sha256sum"] + names, cwd=self.dumps, capture_output=True)
        self.assertEqual(p1.returncode, 0, p1.stderr)
        self.assertEqual(sha(p1.stdout), digest)
        self.assertIn("expect %s" % digest, page)

    def test_altered_file_is_a_high_finding(self):
        f = make_folder(self.dumps, "2026-09-25")
        with open(os.path.join(f, bep.RAW_READABLE), "ab") as fh:
            fh.write(b" ")
        _, out, _ = self.build(f)
        self.assertIn("[high] 1 raw file differs from the hash recorded at collection", out)
        self.assertIn("differs from collection", read(self.out).decode("utf-8"))

    def test_file_the_manifest_attests_is_hashed_even_if_unknown(self):
        """A file the exporter learns to write later is hashed without this script
        having to learn its name first."""
        f = make_folder(self.dumps, "2026-09-25")
        extra = b'{"assignmentFilters": []}\n'
        write_bytes(os.path.join(f, "assignment-filters.json"), extra)
        mp = os.path.join(f, bep.MANIFEST)
        with open(mp) as fh:
            man = json.load(fh)
        man["files"]["assignment-filters.json"] = {"sha256": sha(extra), "bytes": len(extra)}
        write_bytes(mp, jbytes(man))
        self.build(f)
        head = header(read(self.out))
        self.assertIn(sha(extra), head)
        self.assertIn("2026-09-25/assignment-filters.json", head)

    def test_manifest_path_outside_the_folder_is_never_opened(self):
        f = make_folder(self.dumps, "2026-09-25")
        secret = b"outside the folder\n"
        write_bytes(os.path.join(self.dumps, "secret.json"), secret)
        mp = os.path.join(f, bep.MANIFEST)
        with open(mp) as fh:
            man = json.load(fh)
        man["files"]["../secret.json"] = {"sha256": sha(secret), "bytes": len(secret)}
        write_bytes(mp, jbytes(man))
        _, out, _ = self.build(f)
        self.assertIn("[high] The manifest names files outside the dated folder", out)
        self.assertNotIn(sha(secret), read(self.out).decode("utf-8"))

    def test_altered_baseline_raw_dump_is_high(self):
        base = make_folder(self.dumps, "2026-06-24")
        f = make_folder(self.dumps, "2026-09-25")
        rp, yp = os.path.join(base, bep.RAW_EXPORT), os.path.join(base, bep.ROWS)
        with open(rp, "ab") as fh:
            fh.write(b" ")
        with open(yp) as fh:          # rows re-pointed at the altered dump; manifest now stale
            doc = json.load(fh)
        doc["meta"]["source_sha256"] = sha_file(rp)
        write_bytes(yp, jbytes(doc))
        _, out, _ = self.build(f, "--baseline", base,
                               "--differ", stub_differ(self.tmp, 0, NO_DIFF_REPORT))
        self.assertIn("[high] The baseline's raw dump differs from the hash recorded", out)

    def test_absent_optional_file_is_listed_not_hashed(self):
        f = make_folder(self.dumps, "2026-09-25", definitions=False)
        _, out, _ = self.build(f)
        head = header(read(self.out)).replace("\n", " ")
        self.assertRegex(head, r"2026-09-25/setting-definitions\.json</td>.*?absent")
        self.assertIn("[low] Settings Catalog labels are raw setting ids", out)


class Escaped(Base):
    def test_policy_name_and_values_are_text(self):
        make_folder(self.dumps, "2026-06-24")
        f = make_folder(self.dumps, "2026-09-25")
        self.build(f, "--baseline", os.path.join(self.dumps, "2026-06-24"),
                   "--differ", stub_differ(self.tmp, 1, DIFF_REPORT))
        s = read(self.out).decode("utf-8")
        self.assertNotIn("<script", s.lower())
        self.assertNotIn("<b>bold</b>", s)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt; Firewall", s)
        self.assertIn("Old &lt;b&gt;bold&lt;/b&gt; name", s)       # differ output too
        self.assertIn("A &amp; B &quot;quoted&quot; &#x27;single&#x27;", s)
        self.assertIn("x &amp; &quot;y&quot;", s)
        self.assertNotIn(EVIL_VALUE, s)

    def test_escape_helper(self):
        self.assertEqual(bep.e('<a href="x">&\'</a>'),
                         "&lt;a href=&quot;x&quot;&gt;&amp;&#x27;&lt;/a&gt;")
        self.assertEqual(bep.e(True), "true")
        self.assertEqual(bep.e(None), "")
        self.assertEqual(bep.v(None), "null")


class WithAndWithoutBaseline(Base):
    def test_without_baseline_says_so(self):
        _, out, _ = self.build(make_folder(self.dumps, "2026-09-25"))
        s = read(self.out).decode("utf-8")
        self.assertIn("comparison: none (no --baseline)", out)
        self.assertIn("No comparison was made.", s)
        self.assertIn("<dd>not compared</dd>", s)
        self.assertIn("[medium] No baseline has been ratified", out)

    def test_with_baseline_runs_the_differ_cli(self):
        base = make_folder(self.dumps, "2026-06-24")
        f = make_folder(self.dumps, "2026-09-25")
        differ = stub_differ(self.tmp, 1, DIFF_REPORT)
        _, out, _ = self.build(f, "--baseline", base, "--differ", differ)
        argv = stub_argv(differ)
        self.assertEqual(argv[argv.index("--format") + 1], "json")
        self.assertEqual(os.path.realpath(argv[argv.index("--baseline") + 1]),
                         os.path.realpath(os.path.join(base, bep.ROWS)))
        self.assertEqual(os.path.realpath(argv[argv.index("--current") + 1]),
                         os.path.realpath(os.path.join(f, bep.ROWS)))
        s = read(self.out).decode("utf-8")
        self.assertIn("comparison: 2026-06-24 -> 2026-09-25, differ exit 1", out)
        self.assertIn("[high] Settings in the baseline are no longer enforced", out)
        self.assertIn("[medium] Required values changed: 1", out)
        self.assertIn("[low] Objects renamed: 1", out)
        self.assertIn("Counts by class &mdash; differ exit 1", s)
        self.assertIn("device_vendor_msft_bitlocker_false", s)
        self.assertIn("4 differences", s)
        self.assertIn('<div class="vcard no"><p class="k">Running configuration matches it', s)

    def test_no_difference_is_still_evidence(self):
        base = make_folder(self.dumps, "2026-06-24")
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-06-24")
        _, out, _ = self.build(f, "--baseline", base,
                               "--differ", stub_differ(self.tmp, 0, NO_DIFF_REPORT))
        s = read(self.out).decode("utf-8")
        self.assertIn("differ exit 0", out)
        self.assertIn('<div class="vcard yes"><p class="k">Running configuration matches it', s)
        self.assertIn("No differences", s)
        self.assertIn("Required values changed</td><td class=\"n mono\">0</td>", s)
        self.assertIn("findings: 0 high, 0 medium, 0 low", out)

    def test_baseline_that_is_not_the_ratified_one(self):
        make_folder(self.dumps, "2026-03-24")
        base = make_folder(self.dumps, "2026-06-24")
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-03-24")
        _, out, _ = self.build(f, "--baseline", base,
                               "--differ", stub_differ(self.tmp, 0, NO_DIFF_REPORT))
        self.assertIn("[medium] Compared against a baseline that is not the ratified one", out)

    def test_ratified_folder_packed_alone(self):
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-09-25")
        _, out, _ = self.build(f)
        s = read(self.out).decode("utf-8")
        self.assertIn("This dump is the ratified standard", s)
        self.assertNotIn("ratified", out.split("findings:")[1].lower())

    def test_differ_failure_refuses(self):
        base = make_folder(self.dumps, "2026-06-24")
        f = make_folder(self.dumps, "2026-09-25")
        differ = stub_differ(self.tmp, 2, stdout="",
                             stderr="error: refusing to compare generator 1.x with 2.x\n")
        _, _, err = self.build(f, "--baseline", base, "--differ", differ, expect=2)
        self.assertIn("refusing to compare generator 1.x with 2.x", err)
        self.assertFalse(os.path.exists(self.out))

    def test_differ_non_json_refuses(self):
        base = make_folder(self.dumps, "2026-06-24")
        f = make_folder(self.dumps, "2026-09-25")
        self.build(f, "--baseline", base, "--differ",
                   stub_differ(self.tmp, 1, stdout="SUMMARY: not json"), expect=2)
        self.assertFalse(os.path.exists(self.out))

    def test_self_comparison_refuses(self):
        f = make_folder(self.dumps, "2026-09-25")
        _, _, err = self.build(f, "--baseline", f, expect=2)
        self.assertIn("same folder", err)


class Provenance(Base):
    def test_missing_manifest_refuses_by_default(self):
        f = make_folder(self.dumps, "2026-09-25", manifest=False)
        _, _, err = self.build(f, expect=2)
        self.assertIn("has no collection-manifest.json", err)
        self.assertIn("--allow-missing-manifest", err)
        self.assertFalse(os.path.exists(self.out))

    def test_missing_manifest_override_never_invents_provenance(self):
        f = make_folder(self.dumps, "2026-09-25", manifest=False)
        _, out, err = self.build(f, "--allow-missing-manifest")
        s = read(self.out).decode("utf-8")
        self.assertIn("WARNING", err)
        self.assertIn("[high] No collection manifest", out)
        self.assertIn('<dt>collected</dt><dd class="flag">NOT RECORDED</dd>', s)
        self.assertIn('<dt>by</dt><dd class="flag">NOT RECORDED</dd>', s)
        self.assertIn("collection date not recorded", s)
        self.assertIn('<div class="vcard no"><p class="k">The evidence holds', s)
        # nothing shaped like a collection timestamp may appear anywhere
        self.assertIsNone(re.search(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}", s))
        self.assertNotIn("as collected on", s)
        # the rebuild command printed on the page must actually rebuild it
        self.assertIn("--folder dumps/2026-09-25 --allow-missing-manifest --out", s)

    def test_manifest_provenance_is_shown(self):
        _, _, _ = self.build(make_folder(self.dumps, "2026-09-25"))
        s = read(self.out).decode("utf-8")
        self.assertIn("<dt>collected</dt><dd>2026-09-25T03:14:15Z</dd>", s)
        self.assertIn("<dt>by</dt><dd>collector@example.com</dd>", s)
        self.assertIn("as collected on 2026-09-25", s)

    def test_null_collector_is_not_invented(self):
        f = make_folder(self.dumps, "2026-09-25", collector_upn=None)
        _, out, _ = self.build(f)
        s = read(self.out).decode("utf-8")
        self.assertIn("[medium] The collector's identity was not recorded", out)
        self.assertIn('<dt>by</dt><dd class="flag">NOT RECORDED</dd>', s)

    def test_corrupt_manifest_refuses_even_with_override(self):
        f = make_folder(self.dumps, "2026-09-25")
        write_bytes(os.path.join(f, bep.MANIFEST), b"{not json")
        self.build(f, "--allow-missing-manifest", expect=2)


class Refusals(Base):
    def test_v1_rows_refuse(self):
        f = make_folder(self.dumps, "2026-09-25", generator_version="1.0")
        _, _, err = self.build(f, expect=2)
        self.assertIn("generator_version '1.0'", err)

    def test_rows_from_a_different_dump_refuse(self):
        f = make_folder(self.dumps, "2026-09-25", tamper_rows_sha=True)
        _, _, err = self.build(f, expect=2)
        self.assertIn("a different dump", err)

    def test_missing_rows_refuse(self):
        f = make_folder(self.dumps, "2026-09-25")
        os.remove(os.path.join(f, bep.ROWS))
        self.build(f, expect=2)


class ComputedFindings(Base):
    def test_truncated_export_is_high(self):
        f = make_folder(self.dumps, "2026-09-25", truncate=True)
        _, out, _ = self.build(f)
        self.assertIn("[high] 2 Settings Catalog policies returned fewer settings than declared",
                      out)
        s = read(self.out).decode("utf-8")
        self.assertIn('<div class="vcard no"><p class="k">The evidence holds', s)

    def test_clean_folder_passes_acceptance_with_counts(self):
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-09-25")
        _, out, _ = self.build(f)
        s = read(self.out).decode("utf-8")
        self.assertIn("findings: 0 high, 0 medium, 0 low", out)
        self.assertIn("No findings on this run.", s)
        self.assertIn("3 of 3", s)          # 3 Settings Catalog policies, all complete
        self.assertIn("7 rows", s)            # 3 + 2 + 2, each object with its name row
        self.assertIn("TESTING Unassigned Thing", s)   # exclusion listed with reason
        self.assertIn("deviceManagementScripts", s)   # exported but not baselined
        self.assertIn("assignmentFilters", s)         # known blind spot, absent

    def test_undeclared_definition_drop_is_found(self):
        f = make_folder(self.dumps, "2026-09-25")
        p = os.path.join(f, bep.DEFINITIONS)
        with open(p) as fh:
            defs = json.load(fh)
        defs.pop("device_vendor_msft_firewall_enable")
        b = jbytes(defs)
        write_bytes(p, b)
        # keep manifest and rows consistent with the edited file
        mp = os.path.join(f, bep.MANIFEST)
        with open(mp) as fh:
            man = json.load(fh)
        man["files"][bep.DEFINITIONS] = {"sha256": sha(b), "bytes": len(b)}
        write_bytes(mp, jbytes(man))
        rp = os.path.join(f, bep.ROWS)
        with open(rp) as fh:
            doc = json.load(fh)
        doc["meta"]["definitions_sha256"] = sha(b)
        write_bytes(rp, jbytes(doc))
        _, out, _ = self.build(f)
        self.assertIn("[medium] 1 setting definition neither fetched nor listed unresolved", out)


class RealDiffer(Base):
    """End to end through the sibling diff_baseline.py, with no --differ override -- the
    path the cycle wrapper takes. Asserts only what the v2 differ's contract promises."""

    def test_rename_and_change_render_once_each(self):
        base = make_folder(self.dumps, "2026-06-24",
                           objects=fixture_objects(name_a="Old Firewall Name"))
        ratify_fixture(self.dumps, "2026-06-24")
        f = make_folder(self.dumps, "2026-09-25", objects=fixture_objects(
            value_b="device_vendor_msft_bitlocker_false", label_a="On"))
        _, out, _ = self.build(f, "--baseline", base)
        page = read(self.out)
        s = page.decode("utf-8")
        self.assertIn("differ exit 1", out)
        self.assertIn("[low] Objects renamed: 1", out)
        self.assertIn("[medium] Required values changed: 1", out)
        self.assertNotIn("no longer enforced", out)       # a rename is not a removal
        self.assertIn("Old Firewall Name", s)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt; Firewall", s)
        self.assertNotIn("<script", s.lower())
        self.assertIn("2 of 2", s)                         # settings unaffected by the rename
        self.assertIn("Labels changed, raw value unchanged &mdash; 1", s)   # relabel, not drift
        self.assertIn("row contract 2", s)
        ZeroNetwork.assert_offline(self, page)
        self.assertEqual(fetch_scan(page), [])
        self.build(f, "--baseline", base)
        self.assertEqual(page, read(self.out))

    def test_clean_cycle_is_evidence_not_silence(self):
        base = make_folder(self.dumps, "2026-06-24", unbaselined_marker="june")
        ratify_fixture(self.dumps, "2026-06-24")
        f = make_folder(self.dumps, "2026-09-25", unbaselined_marker="september")
        _, out, _ = self.build(f, "--baseline", base)
        s = read(self.out).decode("utf-8")
        self.assertIn("differ exit 0", out)
        self.assertIn("findings: 0 high, 0 medium, 0 low", out)
        self.assertIn('<div class="vcard yes"><p class="k">Running configuration matches it', s)
        self.assertIn("Rows unchanged</td><td class=\"n mono\">7</td>", s)


INCIDENTS = ["Settings Catalog policies: assignments sub-request FAILED for 3 policies",
             "deviceConfigurations: list TRUNCATED after 2 page(s) (HTTP 503): <b>busy</b> & retry"]


class Completeness(Base):
    """A dump placed with --accept-incomplete must read as incomplete wherever an auditor
    looks, and a manifest that does not say must read NOT RECORDED, never clean."""

    def test_incidents_are_high_and_shown_everywhere(self):
        f = make_folder(self.dumps, "2026-09-25", manifest_overrides={"incidents": INCIDENTS})
        _, out, err = self.build(f)
        page = read(self.out)
        s = page.decode("utf-8")
        self.assertIn("[high] The export recorded 2 incidents: this collection is incomplete",
                      out)
        self.assertIn("this export is INCOMPLETE", err)
        self.assertIn("Incomplete collection.", header(page))
        self.assertIn('<dt>export</dt><dd class="flag">INCOMPLETE, 2 incidents</dd>', s)
        self.assertIn('<div class="vcard no"><p class="k">The evidence holds', s)
        prov = section(page, "provenance")
        self.assertIn("This export is incomplete.", prov)
        self.assertIn("--accept-incomplete", prov)
        for t in INCIDENTS:                     # verbatim, escaped, in section 01
            self.assertIn(bep.e(t), prov)
        self.assertIn("recorded no incidents while reading Graph</td><td><span class=\"pill "
                      "p-flag\">fail</span></td><td class=\"mono\">2 incidents recorded", prov)
        self.assertIn("Export completeness</td><td class=\"mono\">INCOMPLETE, 2 incidents", prov)
        findings = section(page, "findings")
        self.assertIn("assignments sub-request FAILED for 3 policies", findings)
        self.assertIn("&lt;b&gt;busy&lt;/b&gt; &amp; retry", findings)
        self.assertNotIn("<b>busy</b>", s)
        self.assertEqual(fetch_scan(page), [])

    def test_incomplete_export_never_reads_as_matching(self):
        base = make_folder(self.dumps, "2026-06-24")
        f = make_folder(self.dumps, "2026-09-25", manifest_overrides={"incidents": INCIDENTS})
        ratify_fixture(self.dumps, "2026-06-24")
        _, out, _ = self.build(f, "--baseline", base,
                               "--differ", stub_differ(self.tmp, 0, NO_DIFF_REPORT))
        s = read(self.out).decode("utf-8")
        self.assertIn("differ exit 0", out)
        self.assertNotIn('<div class="vcard yes"><p class="k">Running configuration matches', s)
        self.assertIn('<div class="vcard part"><p class="k">Running configuration matches', s)
        self.assertIn("<strong>The export recorded 2 incidents</strong>, so it is an incomplete "
                      "collection", s)
        self.assertNotIn("findings: 0 high", out)

    def test_structured_incidents_are_kept_not_dropped(self):
        inc = [{"kind": "TRUNCATED", "label": "configurationPolicies"}]
        f = make_folder(self.dumps, "2026-09-25", manifest_overrides={"incidents": inc})
        _, out, _ = self.build(f)
        self.assertIn("[high] The export recorded 1 incident: this collection is incomplete", out)
        self.assertIn(bep.e(json.dumps(inc[0], sort_keys=True)),
                      section(read(self.out), "provenance"))

    def test_missing_incidents_record_is_not_recorded_not_clean(self):
        f = make_folder(self.dumps, "2026-09-25")
        edit_manifest(f, lambda man: man.pop("incidents"))
        _, out, _ = self.build(f)
        page = read(self.out)
        s = page.decode("utf-8")
        self.assertIn("[medium] The manifest does not record whether the export was complete",
                      out)
        self.assertIn('<dt>export</dt><dd class="flag">NOT RECORDED</dd>', s)
        prov = section(page, "provenance")
        self.assertIn("Export completeness</td><td class=\"mono\">NOT RECORDED", prov)
        self.assertIn('<span class="pill p-none">not recorded</span></td><td class="mono">'
                      'no incidents list', prov)
        self.assertNotIn("Incomplete collection.", header(page))
        self.assertNotIn("complete, no incidents recorded", s)

    def test_malformed_incidents_record_is_high(self):
        f = make_folder(self.dumps, "2026-09-25", manifest_overrides={"incidents": "all fine"})
        _, out, _ = self.build(f)
        page = read(self.out)
        self.assertIn("[high] The manifest's incidents record is unreadable", out)
        self.assertIn("incidents is a string, not a list", page.decode("utf-8"))
        self.assertIn("Completeness unreadable.", header(page))
        self.assertIn('<div class="vcard no"><p class="k">The evidence holds', page.decode())

    def test_empty_incidents_list_is_stated_complete(self):
        f = make_folder(self.dumps, "2026-09-25")
        _, out, _ = self.build(f)
        page = read(self.out)
        s = page.decode("utf-8")
        self.assertNotIn("incident", out.split("findings:")[1])
        self.assertIn("<dt>export</dt><dd>complete, no incidents recorded</dd>", s)
        self.assertIn("recorded no incidents while reading Graph</td><td><span class=\"pill "
                      "p-ok\">pass</span></td><td class=\"mono\">0 incidents recorded",
                      section(page, "provenance"))
        self.assertNotIn("Incomplete collection.", header(page))

    def test_no_manifest_leaves_completeness_not_recorded(self):
        f = make_folder(self.dumps, "2026-09-25", manifest=False)
        self.build(f, "--allow-missing-manifest")
        page = read(self.out)
        self.assertIn('<dt>export</dt><dd class="flag">NOT RECORDED</dd>', page.decode("utf-8"))
        self.assertIn('<span class="pill p-none">not recorded</span></td><td class="mono">'
                      'no manifest', section(page, "provenance"))

    def test_baseline_collected_incomplete_is_medium(self):
        base = make_folder(self.dumps, "2026-06-24", manifest_overrides={"incidents": INCIDENTS})
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-06-24")
        _, out, _ = self.build(f, "--baseline", base,
                               "--differ", stub_differ(self.tmp, 0, NO_DIFF_REPORT))
        self.assertIn("[medium] The baseline's own collection recorded 2 incidents", out)
        self.assertNotIn("[high] The export recorded", out)
        self.assertIn("<dt>export</dt><dd>complete, no incidents recorded</dd>",
                      read(self.out).decode("utf-8"))


class GitProvenance(Base):
    TOOL = "export-intune-config.sh"

    def tool(self, **kw):
        return {"tool": dict({"name": self.TOOL}, **kw)}

    def test_dirty_working_copy_is_shown_and_found(self):
        f = make_folder(self.dumps, "2026-09-25",
                        manifest_overrides=self.tool(git_commit="abc1234", git_dirty=True))
        _, out, _ = self.build(f)
        prov = section(read(self.out), "provenance")
        self.assertIn("[medium] The exporter that ran differed from its recorded git commit", out)
        self.assertIn("Tool git commit</td><td class=\"mono\">abc1234</td>", prov)
        self.assertIn("Tool git dirty</td><td class=\"mono\">true: the script that ran differed "
                      "from this commit</td>", prov)

    def test_clean_working_copy_is_stated(self):
        _, out, _ = self.build(make_folder(self.dumps, "2026-09-25"))
        self.assertNotIn("git commit", out)
        self.assertIn("Tool git dirty</td><td class=\"mono\">false: the script that ran was this "
                      "commit, unmodified</td>", section(read(self.out), "provenance"))

    def test_dirty_not_recorded_is_not_assumed_clean(self):
        f = make_folder(self.dumps, "2026-09-25",
                        manifest_overrides=self.tool(git_commit="abc1234"))
        _, out, _ = self.build(f)
        self.assertIn("[medium] Whether the exporter matched its recorded commit was not "
                      "recorded", out)
        self.assertIn("Tool git dirty</td><td class=\"mono\">NOT RECORDED</td>",
                      section(read(self.out), "provenance"))

    def test_commit_not_recorded(self):
        f = make_folder(self.dumps, "2026-09-25",
                        manifest_overrides=self.tool(git_commit=None, git_dirty=None))
        _, out, _ = self.build(f)
        self.assertIn("[medium] The exporter's git commit was not recorded", out)
        self.assertIn("Tool git commit</td><td class=\"mono\">NOT RECORDED</td>",
                      section(read(self.out), "provenance"))


HOSTILE = ('"><img src=x onerror=alert(1)><script>alert(2)</script></style>'
           '<a href="javascript:alert(3)">x</a> https://evil.example/x.css '
           '<svg onload=alert(4)><image xlink:href="//evil.example/i.png"/>'
           "<meta http-equiv=refresh content='0;url=//evil.example'> @import url(//e.example)")


class StructurallyOffline(Base):
    """The byte grep is blind to a character reference inside an attribute, which a
    browser decodes and fetches. These judge the parsed page instead."""

    def test_escape_helpers_defang_text_only(self):
        self.assertEqual(bep.e("https://x.example"), "&#x68;ttps://x.example")
        self.assertEqual(bep.attr("https://x.example"), "https://x.example")
        self.assertEqual(bep.attr('"><b>'), "&quot;&gt;&lt;b&gt;")
        self.assertEqual(bep.attr(True), "true")

    def test_scanners_see_a_defanged_reference_in_an_attribute(self):
        """The latent hole: e() in an attribute passes the grep but still fetches."""
        page = '<p><a href="%s">x</a></p>' % bep.e("https://evil.example/")
        self.assertNotIn("http", page)                     # the grep would pass
        self.assertTrue(fetch_scan(page))
        self.assertTrue(bep.audit_offline(page))

    def test_scanners_catch_each_fetching_construct(self):
        clean = '<svg xmlns="%s"><rect class="g-cp"></rect></svg>' % SVG_NS
        self.assertEqual(fetch_scan(clean), [])
        self.assertEqual(bep.audit_offline(clean), [])
        for bad in ('<img src="x">', '<div onclick="x()">t</div>',
                    '<div style="background:url(x.png)">t</div>',
                    '<meta http-equiv="refresh" content="0">',
                    '<style>@import "x.css";</style>',
                    '<svg xmlns="%s"><image xlink:href="i.png"/></svg>' % SVG_NS,
                    '<picture><source srcset="a.png"></picture>',
                    '<video poster="p.png"></video>', '<form action="/x"></form>',
                    '<object data="x.swf"></object>', '<div title="&#x68;ttp://x">t</div>'):
            self.assertTrue(fetch_scan(bad), bad)
            self.assertTrue(bep.audit_offline(bad), bad)

    def test_hostile_inputs_everywhere_stay_text(self):
        """Hostile markup in the policy name, a value, the collector, tenant and tool, an
        incident, and every differ field the page renders."""
        objs = fixture_objects(name_a=HOSTILE)
        b = list(objs[1])
        b[5] = b[5] + [("device_vendor_msft_hostile", HOSTILE, None)]
        objs[1] = tuple(b)
        make_folder(self.dumps, "2026-06-24")
        f = make_folder(self.dumps, "2026-09-25", objects=objs, manifest_overrides={
            "collector": {"upn": HOSTILE, "object_id": HOSTILE, "source": HOSTILE},
            "tenant_id": HOSTILE, "client_id": HOSTILE, "collection_date": HOSTILE,
            "tool": {"name": HOSTILE, "git_commit": HOSTILE, "git_dirty": True},
            "incidents": [HOSTILE]})
        report = json.loads(json.dumps(DIFF_REPORT))
        report["renamed"][0].update({"from": HOSTILE, "to": HOSTILE})
        report["changed"][0].update({"from": HOSTILE, "to": HOSTILE})
        report["added"][0].update({"object_name": HOSTILE, "required_value": HOSTILE,
                                   "setting_id": HOSTILE})
        report["warnings"] = [HOSTILE]
        report["surprise_class"] = [{"x": HOSTILE}]
        report["summary"]["surprise_class"] = 1
        self.build(f, "--baseline", os.path.join(self.dumps, "2026-06-24"),
                   "--differ", stub_differ(self.tmp, 1, report))
        page = read(self.out)
        s = page.decode("utf-8")
        self.assertEqual(fetch_scan(page), [])
        # ZeroNetwork's byte checks are not used here: escaped hostile TEXT legitimately
        # contains `src=`, `url(` and `@import`, which is exactly why the parse is the audit.
        self.assertEqual(set(re.findall(r"https?://[^\s\"'<>)]*", s, flags=re.I)), {SVG_NS})
        for raw in ("<img", "<script", "<a ", "<image", "<meta http-equiv", "<svg onload"):
            self.assertNotIn(raw, s.lower(), raw)
        self.assertIn(HOSTILE, html_unescape(s))          # still shown, as text

    def test_builder_refuses_to_write_a_page_that_would_fetch(self):
        f = make_folder(self.dumps, "2026-09-25")
        page = bep.render   # keep the real renderer reachable for the patched one

        def leaky(m, fs):
            return page(m, fs).replace("</footer>", '<img src="x"></footer>')

        with mock.patch.object(bep, "render", leaky):
            with self.assertRaises(bep.Refusal) as ctx:
                bep.build(f, self.out)
        self.assertIn("could make a network request", str(ctx.exception))
        self.assertFalse(os.path.exists(self.out))


class Approval(Base):
    """The pack shows who approved the standard, when and from which dump, as each standard
    page records it -- the question DCF-12 turns on -- and never takes RATIFIED alone as
    the approval."""

    def repo(self, *parts):
        return os.path.join(os.path.dirname(self.dumps), *parts)

    def approval_findings(self, out):
        return [ln for ln in out.split("findings:")[1].splitlines()
                if "standard" in ln.lower() or "ratif" in ln.lower()]

    def test_approval_is_shown_and_every_page_hashed(self):
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-09-25", approver="Jo Approver", approved_on="2026-09-26")
        _, out, _ = self.build(f)
        self.assertIn("findings: 0 high, 0 medium, 0 low", out)
        self.assertIn("approval: BP-MAC version 1.0, approved by Jo Approver on 2026-09-26", out)
        s = read(self.out).decode("utf-8")
        block = s[s.index("<h3>Approval of the standard</h3>"):]
        block = block[:block.index("</figcaption>")]
        for std_id in ("BP-WIN", "BP-MAC", "BP-IOS"):
            self.assertIn(std_id, block)
        self.assertEqual(block.count("matches RATIFIED"), 3)
        self.assertEqual(block.count("Jo Approver"), 3)
        self.assertNotIn("DECOY", s, "a table inside the generated block was read as the approval")
        self.assertIn("Approved by <strong>Jo Approver</strong> on <strong>2026-09-26</strong>", s)
        head = header(read(self.out))
        for _p, fname, _s in bep.PAGES:
            self.assertIn(sha_file(self.repo(fname)), head, fname)
            self.assertIn("../%s" % fname, head)

    def test_pages_join_the_sha256sum_recomputation(self):
        if not shutil.which("sha256sum"):
            self.skipTest("sha256sum not available")
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-09-25")
        _, out, _ = self.build(f)
        digest = re.search(r"input digest ([0-9a-f]{64})", out).group(1)
        page = read(self.out).decode("utf-8")
        files = re.search(r"sha256sum (.*?) \\\n    \| sha256sum", page, re.S).group(1)
        names = [x.strip() for x in files.replace("\\", " ").split()]
        self.assertEqual(sum(1 for n in names if n.startswith("../hardening-standard-")), 3)
        p1 = subprocess.run(["sha256sum"] + names, cwd=self.dumps, capture_output=True)
        self.assertEqual(p1.returncode, 0, p1.stderr)
        self.assertEqual(sha(p1.stdout), digest)

    def test_same_pages_same_bytes_and_relocatable(self):
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-09-25")
        self.build(f)
        first = read(self.out)
        self.build(f)
        self.assertEqual(first, read(self.out))
        moved = os.path.join(self.tmp, "elsewhere", "repo")
        shutil.copytree(os.path.dirname(self.dumps), moved)
        self.build(os.path.join(moved, "dumps", "2026-09-25"))
        self.assertEqual(first, read(self.out))

    def test_editing_a_page_changes_the_pack(self):
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-09-25", approver="Jo Approver")
        self.build(f)
        first = read(self.out)
        ratify_fixture(self.dumps, "2026-09-25", approver="Someone Else")
        self.build(f)
        self.assertNotEqual(first, read(self.out))
        self.assertIn(b"Someone Else", read(self.out))

    def test_missing_page_is_high(self):
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-09-25")
        os.remove(self.repo("hardening-standard-macos-endpoints.md"))
        _, out, _ = self.build(f)
        self.assertIn("[high] The macOS standard does not record the approval RATIFIED names", out)
        self.assertEqual(len(self.approval_findings(out)), 1, out)
        s = read(self.out).decode("utf-8")
        self.assertIn("page missing", s)
        self.assertIn("Its approval record is incomplete", s)

    def test_unapproved_page_is_high(self):
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-09-25", version="—", approver="—", approved_on="—")
        _, out, _ = self.build(f)
        self.assertIn("findings: 3 high", out)
        s = read(self.out).decode("utf-8")
        self.assertIn("records no Version, Approved by, Approved on, Effective from", s)

    def test_page_ratified_from_another_folder_is_high(self):
        make_folder(self.dumps, "2026-06-24")
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-06-24")          # pages approve 2026-06-24 ...
        write_bytes(os.path.join(self.dumps, "RATIFIED"), b"2026-09-25\n")   # ... pointer moved
        _, out, _ = self.build(f)
        self.assertIn("findings: 3 high", out)
        self.assertIn("was ratified from dumps/2026-06-24, but RATIFIED names 2026-09-25",
                      read(self.out).decode("utf-8"))

    def test_page_citing_the_wrong_hash_is_high(self):
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-09-25",
                       ratified_from="dumps/2026-09-25 (sha256 %s)" % ("0" * 16))
        _, out, _ = self.build(f)
        self.assertIn("findings: 3 high", out)
        self.assertIn("cites sha256 0000000000000000 for dumps/2026-09-25",
                      read(self.out).decode("utf-8"))

    def test_the_ratified_hash_is_checked_for_a_folder_that_is_neither_side(self):
        make_folder(self.dumps, "2026-03-24")
        base = make_folder(self.dumps, "2026-06-24")
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-03-24",
                       ratified_from="dumps/2026-03-24 (sha256 %s)" % ("f" * 16))
        _, out, _ = self.build(f, "--baseline", base,
                               "--differ", stub_differ(self.tmp, 0, NO_DIFF_REPORT))
        self.assertIn("findings: 3 high", out)

    def test_standard_id_mismatch_is_high(self):
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-09-25")
        write_bytes(self.repo("hardening-standard-ios-endpoints.md"),
                    standard_page("BP-WIN", "wrong", ratified_from="dumps/2026-09-25 (sha256 %s)"
                                  % sha_file(os.path.join(f, bep.RAW_EXPORT))[:16]))
        _, out, _ = self.build(f)
        self.assertIn("[high] The iOS standard does not record the approval RATIFIED names", out)
        self.assertIn("declares Standard ID BP-WIN, not BP-IOS", read(self.out).decode("utf-8"))

    def test_malformed_approval_table_is_high_and_never_crashes(self):
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-09-25")
        write_bytes(self.repo("hardening-standard-windows-endpoints.md"),
                    b"---\ntitle: x\n---\n| Standard ID | BP-WIN |\n| Version | 1.0 |\n\n"
                    b"<!-- GENERATED:START -->\n<!-- GENERATED:END -->\n")
        write_bytes(self.repo("hardening-standard-macos-endpoints.md"), b"\xff\xfe not utf-8")
        write_bytes(self.repo("hardening-standard-ios-endpoints.md"),
                    b"---\ntitle: x\n---\n| Standard ID | BP-IOS |\n")
        _, out, _ = self.build(f)
        self.assertIn("findings: 3 high", out)
        s = read(self.out).decode("utf-8")
        self.assertIn("has no single two-column &#x27;| Approved by |&#x27; row", s)
        self.assertIn("is not UTF-8", s)
        self.assertIn("does not have exactly one pair of generated markers", s)

    def test_untrusted_approver_text_is_escaped_and_unescaped_from_markdown(self):
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-09-25", approver=r"<script>x</script> A \| B")
        self.build(f)
        s = read(self.out).decode("utf-8")
        self.assertNotIn("<script>x", s)
        self.assertIn("&lt;script&gt;x&lt;/script&gt; A | B", s)

    def test_no_ratified_and_no_pages_adds_no_approval_finding(self):
        f = make_folder(self.dumps, "2026-09-25")
        _, out, _ = self.build(f)
        self.assertEqual(self.approval_findings(out),
                         ["  [medium] No baseline has been ratified"])
        self.assertIn("does not exist", read(self.out).decode("utf-8"))

    def test_a_page_approval_without_ratified_is_medium(self):
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-09-25")
        os.remove(os.path.join(self.dumps, "RATIFIED"))
        _, out, _ = self.build(f)
        self.assertIn("[medium] A standard page records an approval that RATIFIED does not", out)
        self.assertIn("not ratified", read(self.out).decode("utf-8"))

    # --- the defects an adversarial review reproduced, one test each ------------------------

    def test_rows_edited_after_approval_are_not_shown_as_approved(self):
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-09-25")
        rows = os.path.join(f, bep.ROWS)
        with open(rows) as fh:
            doc = json.load(fh)
        doc["rows"][1]["required_value"] = "tampered_after_approval"   # source_sha256 kept
        write_bytes(rows, jbytes(doc))
        _, out, _ = self.build(f)
        self.assertIn("findings: 3 high", out)
        s = read(self.out).decode("utf-8")
        self.assertIn("the rows changed after approval", s)
        self.assertNotIn("matches RATIFIED", s)
        self.assertIn("Its approval record is incomplete", s)

    def test_a_check_that_cannot_be_made_is_never_a_match(self):
        make_folder(self.dumps, "2026-06-24")
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-06-24",
                       ratified_from="dumps/2026-06-24 (sha256 %s)" % ("0" * 16))
        os.remove(os.path.join(self.dumps, "2026-06-24", bep.RAW_EXPORT))
        _, out, _ = self.build(f)
        self.assertIn("findings: 3 high", out)
        s = read(self.out).decode("utf-8")
        self.assertIn("cannot be verified", s)
        self.assertNotIn("matches RATIFIED", s)

    def test_the_baseline_side_counts_as_the_ratified_folder_too(self):
        base = make_folder(self.dumps, "2026-06-24")
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-06-24")
        os.remove(os.path.join(base, bep.RAW_EXPORT))
        _, out, _ = self.build(f, "--baseline", base,
                               "--differ", stub_differ(self.tmp, 0, NO_DIFF_REPORT))
        self.assertIn("findings: 3 high", out)
        self.assertNotIn("matches RATIFIED", read(self.out).decode("utf-8"))

    def test_ratified_from_is_matched_whole_not_searched(self):
        f = make_folder(self.dumps, "2026-09-25")
        good = "dumps/2026-09-25 (sha256 %s)" % sha_file(os.path.join(f, bep.RAW_EXPORT))[:16]
        ratify_fixture(self.dumps, "2026-09-25", ratified_from="REVOKED, was " + good)
        _, out, _ = self.build(f)
        self.assertIn("findings: 3 high", out)
        self.assertNotIn("matches RATIFIED", read(self.out).decode("utf-8"))
        os.remove(os.path.join(self.dumps, "RATIFIED"))
        _, out, _ = self.build(f)
        self.assertNotIn("records an approval that RATIFIED does not", out)

    def test_approver_text_round_trips_md_text_exactly(self):
        """The approver is written by run_config_cycle.md_text; the pack must show the name
        that was typed, not md_text's escaping of it."""
        import run_config_cycle as rcc
        name = "Eric Sharp <esharp@bitpool.com> & R&amp;D | *ops* [x] \\ _y_"
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-09-25", approver=rcc.md_text(name))
        _, out, _ = self.build(f)
        self.assertIn("findings: 0 high, 0 medium, 0 low", out)
        self.assertIn("approved by %s on" % name, out)
        self.assertIn(bep.e(name), read(self.out).decode("utf-8"))

    def test_approval_table_after_the_generated_block_is_read_as_ratify_allows(self):
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-09-25", table_after_block=True)
        _, out, _ = self.build(f)
        self.assertIn("findings: 0 high, 0 medium, 0 low", out)
        self.assertEqual(read(self.out).decode("utf-8").count("matches RATIFIED"), 3)

    def test_an_unreadable_page_is_a_finding_not_an_abort(self):
        if hasattr(os, "geteuid") and os.geteuid() == 0:
            self.skipTest("root reads a mode-000 file")
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-09-25")
        page = self.repo("hardening-standard-ios-endpoints.md")
        os.chmod(page, 0)
        try:
            _, out, _ = self.build(f)
        finally:
            os.chmod(page, 0o644)
        self.assertIn("[high] The iOS standard does not record the approval RATIFIED names", out)
        s = read(self.out).decode("utf-8")
        self.assertIn("cannot be read", s)
        self.assertNotIn(self.tmp, s)

    def test_a_standards_dir_outside_the_layout_is_flagged_and_rebuildable(self):
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-09-25")
        elsewhere = os.path.join(self.tmp, "standards")
        os.makedirs(elsewhere)
        for _p, fname, _s in bep.PAGES:
            shutil.move(self.repo(fname), os.path.join(elsewhere, fname))
        _, out, _ = self.build(f, "--standards-dir", elsewhere)
        self.assertIn("[low] The standard pages were read from outside the default layout", out)
        self.assertIn("--standards-dir dumps/../../standards", read(self.out).decode("utf-8"))

    def test_standards_dir_flag(self):
        f = make_folder(self.dumps, "2026-09-25")
        ratify_fixture(self.dumps, "2026-09-25")
        elsewhere = os.path.join(self.tmp, "standards")
        os.makedirs(elsewhere)
        for _p, fname, _s in bep.PAGES:
            shutil.move(self.repo(fname), os.path.join(elsewhere, fname))
        _, out, _ = self.build(f)
        self.assertIn("findings: 3 high", out)
        _, out, _ = self.build(f, "--standards-dir", elsewhere)
        self.assertIn("findings: 0 high, 0 medium, 1 low", out)


if __name__ == "__main__":
    unittest.main(verbosity=2)
