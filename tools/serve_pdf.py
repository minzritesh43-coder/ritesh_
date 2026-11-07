#!/usr/bin/env python3
"""Serve the notes as a real, downloadable PDF.

- Serves .pdf with Content-Type: application/pdf and no X-Frame-Options,
  so the browser's built-in PDF viewer opens it inline.
- Landing page has an explicit Download button + inline preview fallback.

Run:  python3 tools/serve_pdf.py 8000
"""

import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PDF_NAME = "Life-Processes-Class10-Notes.pdf"

MIME = {
    ".pdf": "application/pdf",
    ".html": "text/html; charset=utf-8",
    ".md": "text/markdown; charset=utf-8",
}

LANDING = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Life Processes — Class 10 Notes (PDF)</title>
<style>
  :root {{ color-scheme: light; }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0; min-height: 100vh; font-family: -apple-system, BlinkMacSystemFont,
    "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: #0f2c24; color: #12211c;
    display: flex; align-items: center; justify-content: center; padding: 28px;
  }}
  .card {{
    background: #fff; border-radius: 18px; max-width: 760px; width: 100%;
    padding: 40px 40px 32px; box-shadow: 0 30px 70px rgba(0,0,0,.45);
  }}
  .kicker {{ letter-spacing: .14em; text-transform: uppercase; font-size: 11px;
            font-weight: 700; color: #0f6b52; }}
  h1 {{ font-size: 27px; line-height: 1.25; margin: 10px 0 14px; color: #0a4a39; }}
  p  {{ margin: 0 0 10px; color: #46534d; font-size: 14.5px; line-height: 1.65; }}
  .facts {{ display: flex; gap: 10px; flex-wrap: wrap; margin: 18px 0 24px; }}
  .pill {{ background: #e6f2ee; color: #0a4a39; font-size: 12px; font-weight: 700;
           padding: 6px 12px; border-radius: 999px; }}
  .btn {{
    display: inline-flex; align-items: center; gap: 10px; text-decoration: none;
    background: #0f6b52; color: #fff; font-weight: 700; font-size: 16px;
    padding: 15px 26px; border-radius: 11px; box-shadow: 0 8px 20px rgba(15,107,82,.32);
    transition: transform .12s ease, background .12s ease;
  }}
  .btn:hover {{ background: #0a4a39; transform: translateY(-1px); }}
  .hint {{ margin-top: 14px; font-size: 12.5px; color: #7a8781; }}
  .preview {{ margin-top: 26px; border: 1px solid #dbe6e1; border-radius: 12px;
              overflow: hidden; background: #f4f7f6; }}
  object, iframe {{ display: block; width: 100%; height: 420px; border: 0; }}
</style>
</head>
<body>
  <main class="card">
    <div class="kicker">Study notes · delivery</div>
    <h1>Life Processes — Class 10 Biology (PDF)</h1>
    <p>Your Markdown notes have been typeset into a print-ready PDF. Click the button to
       download the file; it is a genuine PDF document, not a text or script file.</p>
    <div class="facts">
      <span class="pill">9 pages</span>
      <span class="pill">A4 · PDF 1.7</span>
      <span class="pill">~88 KB</span>
      <span class="pill">20 bookmarks</span>
      <span class="pill">Selectable text</span>
    </div>
    <a class="btn" href="/{pdf}" download="{pdf}" type="application/pdf">
      ⬇ &nbsp;Download the PDF
    </a>
    <p class="hint">Serves as <code>application/pdf</code>. If your browser downloads instead
       of previewing, that is expected — the file is still the PDF.</p>
    <div class="preview">
      <object data="/{pdf}" type="application/pdf">
        <iframe src="/{pdf}" title="PDF preview"></iframe>
      </object>
    </div>
  </main>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    server_version = "NotesPDF/1.0"

    def log_message(self, fmt, *args):  # keep the log readable
        sys.stdout.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, code, body=b"", ctype="text/plain; charset=utf-8", extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Access-Control-Allow-Origin", "*")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def do_GET(self):
        path = unquote(self.path.split("?")[0])

        if path in ("/", "/index.html"):
            html = LANDING.format(pdf=PDF_NAME).encode("utf-8")
            return self._send(200, html, MIME[".html"])

        rel = path.lstrip("/")
        target = os.path.normpath(os.path.join(ROOT, rel))
        if not target.startswith(ROOT) or not os.path.isfile(target):
            return self._send(404, b"Not found")

        ext = os.path.splitext(target)[1].lower()
        ctype = MIME.get(ext, "application/octet-stream")
        with open(target, "rb") as fh:
            body = fh.read()

        extra = {}
        if ext == ".pdf":
            # inline in the browser + explicit download name
            extra["Content-Disposition"] = 'inline; filename="%s"' % os.path.basename(target)

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Accept-Ranges", "none")
        self.send_header("Cache-Control", "no-store, must-revalidate")
        self.send_header("Access-Control-Allow-Origin", "*")
        for k, v in extra.items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    do_HEAD = do_GET


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    pdf = os.path.join(ROOT, PDF_NAME)
    if not os.path.isfile(pdf):
        sys.exit("PDF missing: %s" % pdf)
    srv = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print("Serving %s on http://0.0.0.0:%d" % (PDF_NAME, port), flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
