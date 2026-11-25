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

Oder im Chat: „Mach ein PDF vom Blog“. Ohne Angabe schlägt der Skill den zuletzt geänderten Blog vor.

## Lizenz

Apache-2.0, siehe `LICENSE` und `NOTICE`.
