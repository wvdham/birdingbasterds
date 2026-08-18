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

PAGINAS = [
    ("index", "Scorelijst"),
    ("scorelijst-archief", "Scorelijst 2023 en ouder"),
    ("spelregels", "Spelregels"),
    ("puntenlijst", "Puntenlijst"),
    ("all-time-ontdeklijst", "All-Time Ontdeklijst"),
    ("cana", "CANA"),
]

# ---------------------------------------------------------------- ontleden

TAGRUIS = r"(?:&nbsp;|\s|</?strong>|</?b>)*"
NA_DP = re.compile(r":" + TAGRUIS + r"(\d+)")     # Naam: 68
VOOR_DP = re.compile(r"(\d+)" + TAGRUIS + r":")   # Naam 104:
ZONDER = re.compile(r":" + TAGRUIS + r"\(")       # Naam: (soorten), geen totaal


def kaal(tekst):
    return html.unescape(re.sub(r"<[^>]+>", "", tekst)).replace("\xa0", " ").strip(" :")


def deelnemer(blok):
    """Geeft (naam, totaal, soortenreeks) terug, of None als het geen stand-regel is."""
    s = re.sub(r"^\s*\d+\s*[.:)]\s*", "", blok.strip())
    for patroon in (NA_DP, VOOR_DP):
        m = patroon.search(s)
        if not m:
            continue
        naam = kaal(s[: m.start()])
        if not naam:
            continue
        rest = re.sub(r"^<br\s*/?>", "", s[m.end():].strip()).strip()
        if rest.startswith("(") and rest.endswith(")"):
            rest = rest[1:-1]
        return naam, m.group(1), rest.strip()
    m = ZONDER.search(s)
    if m:
        rest = s[m.end() - 1:].strip()
        if rest.startswith("(") and rest.endswith(")"):
            rest = rest[1:-1]
        return kaal(s[: m.start()]), None, rest.strip()
    return None


def soortenreeks(ruw):
    """De puntenaantallen achter een soort worden losse plaatjes op de regel."""
    tekst = re.sub(r"\s+</strong>", "</strong>", ruw)
    tekst = re.sub(r"\s*\((\d+)\)", r'<b class="pts">\1</b>', tekst)
    return re.sub(r"\s+", " ", tekst).strip().strip(",")


def rij(positie, naam, totaal, vondsten, leider=False):
    klasse = "row row--leader" if leider else "row"
    score = totaal if totaal is not None else ""
    return (
        f'<li class="{klasse}">'
        f'<span class="row__pos">{positie}</span>'
        f'<span class="row__name">{html.escape(naam)}</span>'
        f'<span class="row__score">{score}</span>'
        f'<span class="row__finds">{soortenreeks(vondsten)}</span>'
        f"</li>"
    )


def bord_uit_ol(match):
    """Het archief: elke <li> is een deelnemer, soms twee bij een gedeelde plek."""
    rijen, positie = [], 0
    for li in re.findall(r"(?s)<li>(.*?)</li>", match.group(0)):
        positie += 1
        for deel in re.split(r"<br\s*/?>", li):
            if not deel.strip():
                continue
            ontleed = deelnemer(deel)
            if ontleed:
                rijen.append(rij(positie, *ontleed, leider=positie == 1))
    if not rijen:
        return match.group(0)
    return '<ol class="board">' + "".join(rijen) + "</ol>"


def bord_uit_paragrafen(body):
    """De lopende scorelijst: losse alinea's die met een rangnummer beginnen."""
    blokken = re.split(r"\n\s*\n", body)
    uit, buffer = [], []

    staart = []

    def leeg():
        if not buffer:
            return
        rijen = []
        for nummer, alinea in buffer:
            ontleed = deelnemer(alinea)
            if ontleed:
                rijen.append(rij(nummer, *ontleed, leider=nummer == "1"))
        uit.append('<ol class="board">' + "".join(rijen) + "</ol>" if rijen else "")
        buffer.clear()
        # markup die aan de laatste alinea vastzat (zoals een sluitende div)
        while staart:
            uit.append(staart.pop(0))

    for blok in blokken:
        m = re.match(r"(?s)^<p>\s*(\d+)\s*[.:)]\s*(.*?)</p>(.*)$", blok.strip())
        if m and deelnemer(m.group(2)):
            buffer.append((m.group(1), m.group(2)))
            if m.group(3).strip():
                staart.append(m.group(3).strip())
        else:
            leeg()
            uit.append(blok)
    leeg()
    return "\n\n".join(b for b in uit if b.strip())


# ---------------------------------------------------------------- opschonen


def css_versie():
    return hashlib.md5((DOCS / "assets" / "style.css").read_bytes()).hexdigest()[:8]


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
    # het navigatieblok dat WordPress in de paginainhoud meelevert wijst terug
    # naar wordpress.com; de site heeft zijn eigen navigatie
    body = re.sub(r"(?s)<nav[^>]*>.*?</nav>", "", body)
    body = re.sub(r"<p[^>]*>\s*(?:<a></a>)?\s*</p>", "", body)
    body = body.replace("<a></a>", "")
    body = re.sub(
        r"<p[^>]*>(?:\s|&nbsp;)*<strong>(?:\s|&nbsp;)*(Scorelijst(?:\s|&nbsp;)*(\d{4}))(?:\s|&nbsp;)*</strong>(?:\s|&nbsp;)*</p>",
        lambda m: f'<h2 id="s{m.group(2)}">Scorelijst {m.group(2)}</h2>',
        body,
    )
    body = re.sub(
        r"<p[^>]*>\s*\(Laatste update:([^<]*)\)\s*</p>",
        r'<p class="update"><span>Laatste update</span>\1</p>',
        body,
    )
    body = re.sub(r'\s*class="[^"]*wp-block[^"]*"', "", body)
    body = re.sub(r'\s*class="has-[^"]*"', "", body)
    body = re.sub(r"<figure[^>]*>\s*(<table)", r'<div class="tablewrap">\1', body)
    body = re.sub(r"(</table>)\s*</figure>", r"\1</div>", body)
    if "<table" in body and "<thead" not in body:
        body = body.replace(
            "<tbody>",
            "<thead><tr><th>Soort</th><th>Punten</th><th>Toelichting</th></tr></thead><tbody>",
            1,
        )
    body = re.sub(
        r'(?s)(<ul class="punten">.*?</ul>)',
        lambda m: re.sub(r"</strong>\s*-\s*", "</strong> ", m.group(1)),
        body,
    )
    body = re.sub(r"(?s)<ol[^>]*>.*?</ol>", bord_uit_ol, body)
    body = bord_uit_paragrafen(body)
    return re.sub(r"\n{3,}", "\n\n", body).strip()


def jaarnavigatie(body):
    jaren = re.findall(r'<h2 id="s(\d{4})">', body)
    if len(jaren) < 3:
        return ""
    items = "".join(f'<li><a href="#s{j}">{j}</a></li>' for j in jaren)
    return f'<ul class="years">{items}</ul>'


def beschrijving(body, titel):
    tekst = " ".join(html.unescape(re.sub(r"<[^>]+>", " ", body)).split())
    if not tekst:
        return f"{titel} van de Birding Basterds."
    return (tekst[:152] + "...") if len(tekst) > 155 else tekst


def navigatie(huidig):
    links = []
    for slug, label in PAGINAS:
        if slug == "index":
            href = "./" if huidig == "index" else "../"
        else:
            href = f"{slug}/" if huidig == "index" else f"../{slug}/"
        current = ' aria-current="page"' if slug == huidig else ""
        links.append(f'<a href="{href}"{current}>{label}</a>')
    return "".join(links)


def bouw():
    for pad in DOCS.iterdir():
        if pad.name not in ("assets", "CNAME"):
            shutil.rmtree(pad) if pad.is_dir() else pad.unlink()

    cssv = css_versie()
    sjabloon = (ROOT / "templates" / "base.html").read_text()
    for slug, label in PAGINAS:
        velden, ruw = frontmatter((CONTENT / f"{slug}.html").read_text())
        body = opschonen(ruw)
        h1 = velden.get("title", label)
        titel = h1 if h1 == "Birding Basterds" else f"{h1} · Birding Basterds"
        pagina = (
            sjabloon.replace("{{title}}", html.escape(titel))
            .replace("{{h1}}", html.escape(h1))
            .replace("{{description}}", html.escape(beschrijving(body, h1)))
            .replace("{{nav}}", navigatie(slug))
            .replace("{{body}}", jaarnavigatie(body) + "\n" + body)
            .replace("{{root}}", "" if slug == "index" else "../")
            .replace("{{cssv}}", cssv)
            .replace("{{slug}}", slug)
            .replace("{{brand_open}}", "h1" if slug == "index" else "span")
            .replace("{{brand_close}}", "h1" if slug == "index" else "span")
            .replace("{{pagekop}}", "" if slug == "index" else f"<h1>{html.escape(h1)}</h1>")
        )
        doel = DOCS / "index.html" if slug == "index" else DOCS / slug / "index.html"
        doel.parent.mkdir(parents=True, exist_ok=True)
        doel.write_text(pagina)
        print(f"{doel.relative_to(ROOT)}  ({len(pagina)} tekens)")


if __name__ == "__main__":
    bouw()
