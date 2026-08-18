#!/usr/bin/env python3
"""Berekent de CDNA-punten van een soort volgens de tabellen in PUNTEN.md.

Gebruik:  python3 tools/punten.py [peiljaar] <soort> [<soort> ...]

Het peiljaar is het jaar van de claim; geteld wordt tot en met het jaar
daarvoor. Zonder peiljaar telt het script tot en met vorig jaar.

Telt de aanvaarde gevallen op de soortpagina van dutchavifauna.nl tot en met
vorig jaar, bepaalt de correctiefactor (gevallen vanaf 2000 gedeeld door het
totaal) en past basispunten en correctie toe.
"""
import html
import re
import sys
import urllib.error
import urllib.request

BASIS = [(1, 100), (2, 90), (5, 80), (10, 70), (20, 50), (30, 40), (50, 25), (60, 20), (61, 16)]
CORRECTIE = [(0.10, 25), (0.15, 20), (0.20, 15), (0.30, 10), (0.40, 5),
             (0.60, 0), (0.70, -5), (0.80, -10), (0.90, -15), (1.01, -20)]
MAX_OMHOOG, MIN_OMLAAG = 85, 16


def zoek_slug(naam):
    """Nederlandse naam -> slug op dutchavifauna, via de soortenlijst."""
    verzoek = urllib.request.Request("https://www.dutchavifauna.nl/list",
                                     headers={"User-Agent": "birdingbasterds-punten/1.0"})
    pagina = urllib.request.urlopen(verzoek, timeout=40).read().decode("utf-8", "replace")
    lijst = re.findall(r'href="/species/([^"]+)"[^>]*>\s*([^<]+)', pagina)
    schoon = lambda t: " ".join(html.unescape(t).lower().replace("-", " ").split())
    doel = schoon(naam)
    for slug, gevonden in lijst:
        if schoon(gevonden) == doel:
            return slug
    for slug, gevonden in lijst:
        if doel in schoon(gevonden):
            return slug
    return None


def gevallen(slug):
    url = f"https://www.dutchavifauna.nl/species/{slug}"
    verzoek = urllib.request.Request(url, headers={"User-Agent": "birdingbasterds-punten/1.0"})
    pagina = urllib.request.urlopen(verzoek, timeout=40).read().decode("utf-8", "replace")
    jaren = []
    for rij in re.findall(r"(?s)<tr[^>]*>(.*?)</tr>", pagina):
        cellen = [" ".join(html.unescape(re.sub(r"<[^>]+>", " ", c)).split())
                  for c in re.findall(r"(?s)<t[dh][^>]*>(.*?)</t[dh]>", rij)]
        # alleen rijen uit de gevallentabel: die beginnen met een volgnummer
        if len(cellen) < 3 or not re.match(r"^\d+\.$", cellen[0]):
            continue
        jaar = re.search(r"\b(1[89]\d\d|20\d\d)\b", cellen[1])
        if jaar:
            jaren.append(int(jaar.group(1)))
    return jaren


def basispunten(aantal):
    punten = 16
    for drempel, waarde in BASIS:
        if aantal >= drempel:
            punten = waarde
    return punten


def correctie(factor):
    for grens, waarde in CORRECTIE:
        if factor < grens:
            return waarde
    return -20


def bereken(slug, peiljaar):
    try:
        jaren = gevallen(slug)
    except (urllib.error.HTTPError, urllib.error.URLError):
        return None
    tot = [j for j in jaren if j < peiljaar]
    if not tot:
        return None
    vanaf2000 = [j for j in tot if j >= 2000]
    factor = len(vanaf2000) / len(tot)
    basis, corr = basispunten(len(tot)), correctie(factor)
    punten = basis + corr
    punten = min(punten, MAX_OMHOOG) if corr > 0 else max(punten, MIN_OMLAAG)
    return dict(slug=slug, gevallen=len(tot), vanaf2000=len(vanaf2000),
                factor=factor, basis=basis, correctie=corr, punten=punten,
                dit_jaar=len(jaren) - len(tot))


if __name__ == "__main__":
    from datetime import date
    peiljaar = date.today().year
    argumenten = sys.argv[1:]
    if argumenten and re.fullmatch(r"\d{4}", argumenten[0]):
        peiljaar = int(argumenten.pop(0))
    for naam in argumenten:
        slug = naam.rsplit("/", 1)[-1]
        u = None if " " in slug else bereken(slug, peiljaar)
        if u is None:
            gevonden = zoek_slug(naam)
            if gevonden:
                slug, u = gevonden, bereken(gevonden, peiljaar)
        if not u:
            print(f"{naam}: geen gevallen gevonden")
            continue
        print(f"{u['slug']:26} {u['gevallen']:3} gevallen t/m {peiljaar-1}, "
              f"{u['vanaf2000']:3} vanaf 2000, factor {u['factor']:.3f}  ->  "
              f"basis {u['basis']:3} correctie {u['correctie']:+3d} = {u['punten']:3} punten"
              + (f"   (+{u['dit_jaar']} dit jaar)" if u['dit_jaar'] else ""))
