"""Werkzeugkasten des Skills blog-pdf: Blog (Obsidian-Markdown) als druckfertiges PDF (A4).

Aufruf:
  python3 -I blog_pdf.py check
  python3 -I blog_pdf.py build <blog.md> <image-dir> <out.pdf>

Exit-Codes: 0 Erfolg, 1 Voraussetzung fehlt oder Schritt scheitert, 2 falscher Aufruf.
Nur Standardbibliothek. Herkunft: P-Publikation/PB-Blogs/@/@!Tool/blog2pdf (Stand 2026-11-16).
"""
import html
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.parse import quote

SIPS = "/usr/bin/sips"
CHROME_DEFAULT = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
USAGE = "Aufruf: blog_pdf.py check | build <blog.md> <image-dir> <out.pdf>"


def chrome_path():
    return os.environ.get("BLOG_PDF_CHROME") or CHROME_DEFAULT


def check():
    """Prüft die Voraussetzungen; gibt True zurück, wenn alles da ist."""
    items = [("sips", SIPS), ("Google Chrome", chrome_path())]
    ok = True
    for name, path in items:
        if os.path.isfile(path) and os.access(path, os.X_OK):
            print(f"ok: {name} ({path})")
        else:
            print(f"fehlt: {name} ({path})")
            ok = False
    return ok


# --- Markdown → HTML (aus blog2html.py) ---------------------------------------


def inline(text):
    codes = []

    def keep(m):
        codes.append(f"<code>{html.escape(m.group(1), quote=False)}</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", keep, text)
    text = html.escape(text, quote=False)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?![\s*])(.+?)(?<![\s*])\*(?![\w*])", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


def table(rows):
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    if len(cells) > 1 and all(re.fullmatch(r":?-+:?", c) for c in cells[1]):
        head, rest = cells[0], cells[2:]
    else:
        head, rest = None, cells
    out = ["<table>"]
    if head:
        out.append("<thead><tr>" + "".join(f"<th>{inline(c)}</th>" for c in head) + "</tr></thead>")
    out.append("<tbody>")
    out += ["<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rest]
    out.append("</tbody></table>")
    return out


CSS = """
@page { size: A4; margin: 20mm 20mm 22mm 20mm; }
body { font-family: Georgia, 'Times New Roman', serif; font-size: 11pt; line-height: 1.5; color: #222; }
h1 { font-size: 24pt; line-height: 1.2; margin: 6mm 0 2mm; color: #5a1d14; }
h2 { font-size: 14pt; margin: 7mm 0 2mm; color: #5a1d14; break-after: avoid; }
p { margin: 0 0 3mm; text-align: justify; hyphens: auto; orphans: 3; widows: 3; }
.byline { color: #777; font-size: 9.5pt; text-align: left; margin-bottom: 6mm; }
ul, ol { margin: 0 0 3mm 5mm; padding-left: 4mm; }
code { font-family: Menlo, Consolas, monospace; font-size: 9pt; background: #f4efe9; padding: 0 0.6mm; border-radius: 1px; white-space: nowrap; hyphens: none; }
pre { margin: 2mm 0 4mm; padding: 2.5mm 3mm; background: #f4efe9; border-left: 0.6mm solid #d8cfc4; break-inside: avoid; white-space: pre-wrap; }
pre code { padding: 0; background: none; white-space: pre-wrap; font-size: 8.5pt; line-height: 1.4; }
li { margin-bottom: 1.5mm; }
figure { margin: 5mm 0; break-inside: avoid; }
figure img { width: 100%; display: block; border-radius: 2px; }
.title-img { margin-top: 0; }
table { width: 100%; border-collapse: collapse; margin: 2mm 0 4mm; font-size: 10pt; break-inside: avoid; }
th, td { text-align: left; vertical-align: top; padding: 1.5mm 2mm; border-bottom: 0.3mm solid #d8cfc4; }
th { color: #5a1d14; border-bottom: 0.5mm solid #5a1d14; }
"""


class BuildError(Exception):
    pass


def to_html(src, img_dir):
    lines = src.read_text(encoding="utf-8").splitlines()
    meta = {}
    body = []
    in_list = None  # "ul" oder "ol"
    rows = []
    code = None  # Zeilen eines Code-Blocks
    for line in lines:
        if code is not None:
            if line.startswith("```"):
                body.append("<pre><code>" + html.escape("\n".join(code), quote=False) + "</code></pre>")
                code = None
            else:
                code.append(line)
            continue
        if line.startswith("```"):
            if rows:
                body += table(rows)
                rows = []
            if in_list:
                body.append(f"</{in_list}>")
                in_list = None
            code = []
            continue
        if line.startswith("|"):
            rows.append(line)
            continue
        if rows:
            body += table(rows)
            rows = []
        m_meta = re.match(r"^\*\*(Datum|Version|Status|Autor|Quelle):\*\*\s*(.*)$", line)
        if m_meta:
            meta[m_meta.group(1)] = m_meta.group(2)
            continue
        m_ol = re.match(r"^\d+\. (.*)$", line)
        kind = "ul" if line.startswith("- ") else "ol" if m_ol else None
        if in_list and kind != in_list:
            body.append(f"</{in_list}>")
            in_list = None
        m_img = re.match(r"^!\[\[(.+?)\]\]$", line)
        if m_img:
            path = (img_dir / m_img.group(1)).resolve()
            if not path.exists():
                raise BuildError(f"Bild fehlt: {path}")
            cls = "title-img" if not any(b.startswith("<h1") for b in body) else "img"
            body.append(f'<figure class="{cls}"><img src="file://{quote(str(path))}"></figure>')
        elif line.startswith("# "):
            body.append(f"<h1>{inline(line[2:])}</h1>")
            body.append("@@META@@")
        elif line.startswith("## "):
            body.append(f"<h2>{inline(line[3:])}</h2>")
        elif kind:
            if not in_list:
                body.append(f"<{kind}>")
                in_list = kind
            body.append(f"<li>{inline(line[2:] if kind == 'ul' else m_ol.group(1))}</li>")
        elif line.strip():
            body.append(f"<p>{inline(line)}</p>")
    if rows:
        body += table(rows)
    if in_list:
        body.append(f"</{in_list}>")

    byline = " · ".join(
        x for x in (meta.get("Autor"), meta.get("Datum"), meta.get("Version") and "Version " + meta["Version"]) if x
    )
    doc = "\n".join(body).replace("@@META@@", f'<p class="byline">{html.escape(byline)}</p>')
    return (
        f'<!doctype html><html lang="de"><head><meta charset="utf-8">'
        f"<title>{html.escape(src.stem)}</title><style>{CSS}</style></head>"
        f"<body>{doc}</body></html>"
    )


# --- build --------------------------------------------------------------------


def build(blog, img_dir, out):
    if not check():
        return 1
    blog, img_dir, out = Path(blog), Path(img_dir), Path(out)
    if not blog.is_file():
        print(f"fehlt: Blog ({blog})")
        return 1
    if not out.parent.is_dir():
        print(f"fehlt: Zielordner ({out.parent})")
        return 1
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        small = tmp / "img"
        small.mkdir()
        if img_dir.is_dir():
            for f in sorted(img_dir.iterdir()):
                if not f.is_file() or f.name.startswith("."):
                    continue
                subprocess.run(
                    [SIPS, "-s", "format", "jpeg", "-s", "formatOptions", "82", "-Z", "1600", str(f),
                     "--out", str(small / f.name)],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                )
        try:
            page = to_html(blog, small)
        except BuildError as e:
            print(str(e))
            return 1
        page_file = tmp / "blog.html"
        page_file.write_text(page, encoding="utf-8")
        if out.exists():
            out.unlink()
        result = subprocess.run(
            [chrome_path(), "--headless=new", "--disable-gpu", "--allow-file-access-from-files",
             "--no-pdf-header-footer", f"--print-to-pdf={out}", f"file://{page_file}"],
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True,
        )
        if result.returncode != 0 or not out.is_file():
            print("Chrome hat kein PDF geschrieben.")
            print(result.stdout.strip()[-2000:])
            return 1
    print(f"geschrieben: {out}")
    return 0


def main(argv):
    if len(argv) == 1 and argv[0] == "check":
        return 0 if check() else 1
    if len(argv) == 4 and argv[0] == "build":
        return build(*argv[1:])
    print(USAGE, file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
