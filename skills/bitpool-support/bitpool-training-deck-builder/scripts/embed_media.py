"""Inline every local image and video a deck points at, so the deck is one self-contained file.

Usage:
    python embed_media.py <draft.html> <final.html>

While building, slides reference media by relative path (src="media/step1.png"). This script
replaces each such src/url() with a base64 data URI and writes the result to <final.html>.
It stops with an error if any referenced file is missing, so a broken image can't ship.
"""
import base64, mimetypes, pathlib, re, sys

mimetypes.add_type("video/mp4", ".mp4")
mimetypes.add_type("video/webm", ".webm")
mimetypes.add_type("image/webp", ".webp")
mimetypes.add_type("image/svg+xml", ".svg")

def main():
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    base = src.parent
    html = src.read_text(encoding="utf-8")
    missing, count = [], 0

    def inline(path_text):
        nonlocal count
        p = (base / path_text).resolve()
        if not p.is_file():
            missing.append(path_text)
            return None
        mime = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        count += 1
        return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode()

    def sub_attr(m):
        uri = inline(m.group(2))
        return m.group(0) if uri is None else f'{m.group(1)}="{uri}"'

    def sub_url(m):
        uri = inline(m.group(1))
        return m.group(0) if uri is None else f'url("{uri}")'

    local = r'(?!data:|https?:|//|#)([^"]+)'
    html = re.sub(r'\b(src|poster)="' + local + '"', sub_attr, html)
    html = re.sub(r'url\(["\']?' + r'(?!data:|https?:|//|#)([^"\')]+)' + r'["\']?\)', sub_url, html)

    if missing:
        sys.exit("Missing media files (nothing written):\n  " + "\n  ".join(sorted(set(missing))))
    with open(dst, "w", encoding="utf-8", newline="") as fh:  # no CRLF translation on Windows
        fh.write(html)
    print(f"embedded {count} file(s) -> {dst} ({dst.stat().st_size / 1e6:.1f} MB)")

if __name__ == "__main__":
    main()
