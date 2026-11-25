# skill-blog-pdf

Paket von AIbex AIBOS mit dem Skill `blog-pdf`: Ein Blog `@Blog/NN Titel.md` wird zu einem druckfertigen PDF `@PDF/NN Titel.pdf` (A4) im selben Projekt, mit derselben Nummer und demselben Titel.

## Voraussetzungen

- AIBOS v0.7, Vault gebunden
- macOS mit `/usr/bin/sips` und `python3`
- Google Chrome unter `/Applications`; ein anderer Pfad über die Umgebungsvariable `BLOG_PDF_CHROME`

Fehlt etwas, meldet der Skill es und hält an.

## Holen

```bash
aibos --fetch skill-blog-pdf
```

## Aufruf

```
/blog-pdf "@Blog/01 Titel.md"
```

Oder im Chat: „Mach ein PDF vom Blog“. Ohne Angabe schlägt der Skill den zuletzt geänderten Blog vor. Er zeigt den Plan, erzeugt das PDF nach Ja, sieht es an (Seiten, Bilder, Tabellen, Version) und committet Blog und PDF nach Ja.

## Was umgesetzt wird

| Markdown | im PDF |
|---|---|
| `# Titel` | Titel, darunter Autor · Datum · Version aus dem Header-Block |
| `## Abschnitt` | Zwischenüberschrift |
| Absatz, `**fett**`, `*kursiv*` | Absatz im Blocksatz, fett, kursiv |
| `` `Code` `` im Text | Festbreitenschrift, hinterlegt, ohne Umbruch |
| `- Punkt` | Aufzählung |
| `1. Punkt` | nummerierte Liste |
| Code-Block mit ```` ``` ```` | Block in Festbreitenschrift, hinterlegt, nicht über Seiten getrennt |
| Tabelle (`\| a \| b \|`, Kopfzeile mit `---`) | Tabelle über die volle Breite, Kopfzeile hervorgehoben, `**fett**` in Zellen |
| `![[Bild.png]]` | Bild in voller Breite aus `@Image/`; vor dem Titel als Titelbild |

Die Zeilen `**Datum:**`, `**Version:**`, `**Status:**`, `**Autor:**`, `**Quelle:**` erscheinen nicht als Text. Links, Zitate und `###`-Überschriften werden nicht umgesetzt.

## Werkzeug

`skills/blog-pdf/blog_pdf.py` (nur Standardbibliothek von Python):

```bash
python3 -I blog_pdf.py check
python3 -I blog_pdf.py build <blog.md> <image-dir> <out.pdf>
```

Bilder werden auf höchstens 1600 px als JPEG verkleinert (`sips`), gedruckt wird mit Chrome headless. Exit-Codes: 0 Erfolg, 1 Voraussetzung fehlt oder Schritt scheitert, 2 falscher Aufruf.

## Herkunft

Aus dem Werkzeug `blog2pdf` in `P-Publikation/PB-Blogs/@/@!Tool/blog2pdf` (Stand 2026-11-16); die Umwandlung stammt aus `blog2html.py`, das Bash-Skript ist durch den Werkzeugkasten ersetzt.

## Lizenz

Apache-2.0, siehe `LICENSE` und `NOTICE`.
