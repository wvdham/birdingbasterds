#!/usr/bin/env python3
"""Bouwt de statische site voor Birding Basterds: content/ -> docs/."""
import hashlib
import html
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
DOCS = ROOT / "docs"

# volgorde in de navigatie; index is de homepage
PAGINAS = [
    ("index", "Scorelijst"),
    ("scorelijst-archief", "Scorelijst 2023 en ouder"),
    ("spelregels", "Spelregels"),
    ("puntenlijst", "Puntenlijst"),
    ("all-time-ontdeklijst", "All-Time Ontdeklijst"),
    ("cana", "CANA"),
]


def css_versie():
    css = DOCS / "assets" / "style.css"
    return hashlib.md5(css.read_bytes()).hexdigest()[:8]


def frontmatter(tekst):
    kop, _, rest = tekst.partition("\n---\n")
    velden = {}
    for regel in kop.splitlines():
        if ":" in regel:
            sleutel, _, waarde = regel.partition(":")
            velden[sleutel.strip()] = waarde.strip()
    return velden, rest.strip()


def opschonen(body):
    """WordPress-blokopmaak omzetten naar schone HTML."""
    # het navigatieblok dat WordPress in de paginainhoud meelevert: die links
    # wijzen terug naar wordpress.com en de site heeft zijn eigen navigatie
    body = re.sub(r"(?s)<nav[^>]*>.*?</nav>", "", body)
    # lege paragrafen en de lege ankers die Gutenberg achterlaat
    body = re.sub(r'<p[^>]*>\s*(?:<a></a>)?\s*</p>', "", body)
    body = body.replace("<a></a>", "")
    # jaarkopjes: een alinea die alleen "Scorelijst JAAR" vetgedrukt bevat
    body = re.sub(
        r'<p[^>]*>(?:\s|&nbsp;)*<strong>(?:\s|&nbsp;)*(Scorelijst(?:\s|&nbsp;)*(\d{4}))(?:\s|&nbsp;)*</strong>(?:\s|&nbsp;)*</p>',
        lambda m: f'<h2 id="s{m.group(2)}">Scorelijst {m.group(2)}</h2>',
        body,
    )
    # regel "(Laatste update: ...)" krijgt een eigen klasse
    body = re.sub(
        r'<p[^>]*>\s*(\(Laatste update:[^<]*\))\s*</p>',
        r'<p class="update">\1</p>',
        body,
    )
    # wp-block-klassen weg, uitlijning behouden we niet: de opmaak zit in de stylesheet
    body = re.sub(r'\s*class="[^"]*wp-block[^"]*"', "", body)
    body = re.sub(r'\s*class="has-[^"]*"', "", body)
    # tabellen scrollbaar maken op smalle schermen
    body = re.sub(r"<figure[^>]*>\s*(<table)", r'<div class="tablewrap">\1', body)
    body = re.sub(r"(</table>)\s*</figure>", r"\1</div>", body)
    # de puntentabel heeft geen koprij; die staat nergens in de bron
    if "<table" in body and "<thead" not in body:
        body = body.replace(
            "<tbody>",
            "<thead><tr><th>Soort</th><th>Punten</th><th>Toelichting</th></tr></thead><tbody>",
            1,
        )
    body = re.sub(r"\n{3,}", "\n\n", body)
    return body.strip()


def jaarnavigatie(body):
    jaren = re.findall(r'<h2 id="s(\d{4})">', body)
    if len(jaren) < 3:
        return ""
    items = "".join(f'<li><a href="#s{j}">{j}</a></li>' for j in jaren)
    return f'<ul class="years">{items}</ul>'


def beschrijving(body, titel):
    tekst = html.unescape(re.sub(r"<[^>]+>", " ", body))
    tekst = " ".join(tekst.split())
    if not tekst:
        return f"{titel} van de Birding Basterds."
    return (tekst[:152] + "...") if len(tekst) > 155 else tekst


def navigatie(huidig):
    links = []
    for slug, label in PAGINAS:
        href = "./" if slug == "index" else f"../{slug}/" if huidig != "index" else f"{slug}/"
        if slug == "index":
            href = "./" if huidig == "index" else "../"
        current = ' aria-current="page"' if slug == huidig else ""
        links.append(f'<a href="{href}"{current}>{label}</a>')
    return "".join(links)


def bouw():
    for pad in DOCS.iterdir():
        if pad.name != "assets" and pad.name != "CNAME":
            shutil.rmtree(pad) if pad.is_dir() else pad.unlink()

    cssv = css_versie()
    for slug, label in PAGINAS:
        bron = CONTENT / f"{slug}.html"
        velden, ruw = frontmatter(bron.read_text())
        body = opschonen(ruw)
        h1 = velden.get("title", label)
        pagina = (ROOT / "templates" / "base.html").read_text()
        paginatitel = h1 if h1 == "Birding Basterds" else f"{h1} \u00b7 Birding Basterds"
        pagina = (
            pagina.replace("{{title}}", html.escape(paginatitel))
            .replace("{{h1}}", html.escape(h1))
            .replace("{{description}}", html.escape(beschrijving(body, h1)))
            .replace("{{nav}}", navigatie(slug))
            .replace("{{body}}", jaarnavigatie(body) + "\n" + body)
            .replace("{{root}}", "" if slug == "index" else "../")
            .replace("{{cssv}}", cssv)
            .replace("{{slug}}", slug)
        )
        doel = DOCS / "index.html" if slug == "index" else DOCS / slug / "index.html"
        doel.parent.mkdir(parents=True, exist_ok=True)
        doel.write_text(pagina)
        print(f"{doel.relative_to(ROOT)}  ({len(pagina)} tekens)")


if __name__ == "__main__":
    bouw()
