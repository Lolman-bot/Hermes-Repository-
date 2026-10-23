#!/usr/bin/env python3
"""Local helper for the build-skill-from-examples process canvas.

Two modes, standard library only, works the same on Windows, macOS and Linux:

  Served (the person is on the machine Hermes runs on):
      python canvas_server.py --seed seed.json --out process.mmd [--open]
    Serves assets/process-canvas.html and the bundled Mermaid library on 127.0.0.1,
    hands the page its seed, writes the submitted diagram to --out, then stops by itself
    after one successful submit, or after --timeout minutes. --open also opens the page
    in this machine's default browser.

  Standalone (the person is somewhere else, e.g. on a messaging app):
      python canvas_server.py --seed seed.json --standalone canvas.html
    Writes one self-contained HTML file (Mermaid and the seed inlined, nothing fetched)
    and exits. The person opens it in any browser and copies or downloads the diagram.

See references/process-canvas.md.
"""
import argparse
import json
import sys
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ASSETS = Path(__file__).resolve().parent.parent / "assets"
PAGE = ASSETS / "process-canvas.html"
MERMAID = ASSETS / "mermaid-10.9.0.min.js"
MERMAID_TAG = '<script src="/mermaid.min.js"></script>'
MAX_BODY = 256 * 1024


def read_seed(path):
    if not path:
        return "null"
    try:
        return json.dumps(json.loads(Path(path).read_text(encoding="utf-8")))
    except (OSError, ValueError) as e:
        sys.exit(f"Could not read seed file {path}: {e}")


def write_standalone(dest, seed):
    page = PAGE.read_text(encoding="utf-8")
    if page.count(MERMAID_TAG) != 1:
        sys.exit(f"Unexpected canvas page: expected one {MERMAID_TAG!r}")
    lib = MERMAID.read_text(encoding="utf-8")
    if "</script" in lib.lower():
        sys.exit("Bundled Mermaid contains '</script'; cannot inline it safely.")
    safe_seed = seed.replace("<", "\\u003c")
    inline = (
        "<script>" + lib + "</script>\n"
        "<script>window.CANVAS_STANDALONE=true;window.CANVAS_SEED=" + safe_seed + ";</script>"
    )
    dest = Path(dest).resolve()
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(page.replace(MERMAID_TAG, inline), encoding="utf-8", newline="\n")
    print(f"Standalone canvas written to {dest}", flush=True)


def main():
    ap = argparse.ArgumentParser(description="Serve the process canvas and save the submitted diagram.")
    ap.add_argument("--out", help="where to write the submitted Mermaid diagram (served mode)")
    ap.add_argument("--seed", help="seed JSON file with {nodes, links} to start the canvas from")
    ap.add_argument("--standalone", metavar="HTML", help="write a self-contained canvas file here and exit")
    ap.add_argument("--port", type=int, default=0, help="port to use (default: any free port)")
    ap.add_argument("--timeout", type=float, default=60, help="minutes before giving up (default 60)")
    ap.add_argument("--open", action="store_true", help="open the canvas in this machine's default browser")
    args = ap.parse_args()

    for f in (PAGE, MERMAID):
        if not f.is_file():
            sys.exit(f"Missing asset: {f}")
    seed = read_seed(args.seed)

    if args.standalone:
        write_standalone(args.standalone, seed)
        return
    if not args.out:
        ap.error("--out is required unless --standalone is given")

    out = Path(args.out).resolve()
    seed_bytes = seed.encode("utf-8")
    done = threading.Event()

    class Handler(BaseHTTPRequestHandler):
        def _send(self, code, body, ctype):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = self.path.split("?", 1)[0]
            if path in ("/", "/index.html"):
                self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
            elif path == "/mermaid.min.js":
                self._send(200, MERMAID.read_bytes(), "application/javascript; charset=utf-8")
            elif path == "/seed.json":
                self._send(200, seed_bytes, "application/json")
            else:
                self._send(404, b"Not found", "text/plain")

        def do_POST(self):
            if self.path != "/submit":
                return self._send(404, b"Not found", "text/plain")
            length = int(self.headers.get("Content-Length") or 0)
            if length <= 0 or length > MAX_BODY:
                return self._send(400, b"Bad request", "text/plain")
            text = self.rfile.read(length).decode("utf-8", "replace").strip()
            if not text.startswith("flowchart"):
                return self._send(400, b"Not a diagram", "text/plain")
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(text + "\n", encoding="utf-8")
            self._send(200, b"saved", "text/plain")
            print(f"Diagram saved to {out}", flush=True)
            done.set()

        def log_message(self, *a):
            pass

    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    print(f"Canvas ready: {url}", flush=True)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    if args.open and not webbrowser.open(url):
        print("Could not open a browser here; open the link by hand.", flush=True)
    if done.wait(timeout=args.timeout * 60):
        server.shutdown()
        sys.exit(0)
    server.shutdown()
    sys.exit(f"No diagram submitted within {args.timeout:g} minutes; canvas stopped.")


if __name__ == "__main__":
    main()
