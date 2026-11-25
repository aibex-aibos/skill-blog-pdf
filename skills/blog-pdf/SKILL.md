---
name: blog-pdf
version: 0.1.0
description: >
  Wandelt einen Blog aus @Blog/ in ein druckfertiges PDF in @PDF/ um, mit derselben Nummer
  und demselben Titel (Regel "Blog als PDF"); prüft macOS und Google Chrome, zeigt den Plan,
  sieht das PDF an und committet nach Ja. Verwenden bei "/blog-pdf", "Mach ein PDF vom Blog",
  "Blog als PDF".
---

# Blog als PDF

Ein Blog `@Blog/NN Titel.md` wird zu `@PDF/NN Titel.pdf` (A4) im selben Projekt, mit derselben Nummer und demselben Titel. Das gilt auch für Essays und andere Texte in `@Blog/`. Das PDF zeigt die aktuelle Version des Blogs und überschreibt ein älteres PDF; frühere Fassungen bleiben in Git.

**Werkzeug:** `blog_pdf.py` liegt im Ordner dieser `SKILL.md`. `<skill-ordner>` ist dieser Ordner („Base directory for this skill“, nach dem Registrieren `<projekt>/.claude/skills/blog-pdf/`). Setze ihn in jedem Aufruf wörtlich als absoluten Pfad ein; er überlebt einen Aufruf nicht. Ruf das Werkzeug je als einzelnen Befehl auf:

- `python3 -I "<skill-ordner>/blog_pdf.py" check`: prüft `/usr/bin/sips` und Google Chrome, eine Zeile `ok: …` bzw. `fehlt: …` je Voraussetzung; Exit-Code 0, wenn alles da ist, sonst 1.
- `python3 -I "<skill-ordner>/blog_pdf.py" build "<blog.md>" "<image-dir>" "<out.pdf>"`: erzeugt das PDF und meldet zuletzt `geschrieben: <out.pdf>`; Exit-Code 0 bei Erfolg, 1 bei einem Fehler, 2 bei falschem Aufruf.

Die Umgebungsvariable `BLOG_PDF_CHROME` überschreibt den Pfad zu Chrome; setze sie nur, wenn der User es verlangt.

**Arbeitsweise:** Arbeite mit absoluten Pfaden, wechsle nie mit `cd`. Dateien findest du mit `ls` und liest sie mit Read über den vollen Pfad, nicht mit Glob: Unter Pfaden mit `§` findet Glob vorhandene Dateien nicht verlässlich.

**Fragen:** Jede Frage mit Optionen stellst du mit dem Auswahlwerkzeug. In Claude Code lädst du es zu Beginn mit `ToolSearch` und `select:AskUserQuestion`, noch vor der ersten Frage. Die erste Option ist die Empfehlung. Wird ein Aufruf abgelehnt (etwa headless), stellst du dieselbe Frage sofort als nummerierte Liste derselben Form.

## 1. Blog bestimmen

- **Mit Angabe** (`/blog-pdf "@Blog/NN Titel.md"` oder ein Pfad im Satz): Dieser Blog gilt. Ein relativer Pfad gilt vom Arbeitsverzeichnis aus.
- **Ohne Angabe:** Das Projekt der Session ist vom Arbeitsverzeichnis aufwärts der erste Ordner mit `@/`. Liste `<projekt>/@Blog/` mit `ls -t` und schlag den zuletzt geänderten Blog vor: „<Blog> (Empfohlen)“, dazu bis zu zwei weitere, „Abbrechen“.
- Gibt es `@Blog/` nicht, ist er leer oder fehlt der genannte Blog, sag das und ende.

Das **Projekt des Blogs** ist vom Blog aufwärts der erste Ordner mit `@/`. Bildordner ist `<projekt>/@Image/`, Ziel `<projekt>/@PDF/<name des Blogs ohne .md>.pdf`.

## 2. Prüfen

Ruf `check` auf. Fehlt etwas, nenne die Zeilen `fehlt: …`, sag, dass das PDF ohne diese Voraussetzung nicht entstehen kann, und halte an. Eine Anleitung zur Installation gibst du nicht.

## 3. Plan zeigen

Zeig vor dem Schreiben:

- Quelle: der Blog mit seiner Version (Zeile `**Version:**`)
- Bildordner `@Image/`
- Ziel `@PDF/NN Titel.pdf`
- ob `@PDF/` angelegt wird
- ob ein vorhandenes PDF überschrieben wird

Dann frag: „Erzeugen (Empfohlen)“ oder „Abbrechen“. Der Wunsch nach einem PDF ist keine Bestätigung dieses Plans.

## 4. Erzeugen

Nach Ja: Leg `<projekt>/@PDF/` an, wenn es fehlt, dann ruf `build` auf. Scheitert der Aufruf, nenne die Ausgabe und halte an.

## 5. Ansehen

Lies das PDF mit Read. Zähl im Blog die eingebetteten Bilder (`grep -c '^!\[\['`) und die Tabellen und lies seine Version. Melde:

- Seitenzahl des PDF
- Bilder: im PDF gesehen gegen gezählt im Blog
- Tabellen: vorhanden ja/nein
- Version unter dem Titel gegen `**Version:**` im Blog

Weicht etwas ab, nenne es.

## 6. Committen

Liegt das Projekt in einem Git-Repo, frag: „Committen (Empfohlen)“ (Blog und PDF in einem Commit, Nachricht `<Titel>: PDF Version <x.y>`) oder „Nicht committen“. Committe nur nach Ja, nur diese beiden Dateien. Einen Push oder Sync bietest du nicht an.

## Grenzen

- Nur macOS mit `/usr/bin/sips` und Google Chrome.
- Du schreibst nur nach `@PDF/` des Projekts, in dem der Blog liegt, und committest nur nach Ja.
- Den Blog änderst du nicht. Andere Markdown-Elemente als die im README genannten setzt das Werkzeug nicht um; fehlt eines im PDF, sag das.
