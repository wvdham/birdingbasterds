# Birding Basterds

Statische site van de zelfontdekcompetitie Birding Basterds. Overgezet vanaf
birdingbasterds.wordpress.com (augustus 2026); de WordPress-inhoud is via de
publieke API opgehaald en zit ongewijzigd in `content/`.

## Opzet

    content/*.html      de teksten, met een regel `title:` bovenaan
    templates/base.html het paginasjabloon
    build.py            zet content om naar docs/
    docs/               het bouwresultaat dat GitHub Pages serveert

Aanpassen gaat altijd via `content/`. Draai daarna:

    python3 build.py

`docs/` is bouwresultaat: wat je daar met de hand in zet, is bij de volgende
bouw weg. Enige uitzondering is `docs/assets/style.css`, dat is bron.

## Wat build.py doet

- vetgedrukte regels "Scorelijst JAAR" worden koppen met een anker (`#s2019`)
- pagina's met drie of meer jaren krijgen bovenaan een rij jaarknoppen
- lege alinea's en lege ankers uit de WordPress-editor gaan eruit
- de puntentabel krijgt een koprij (Soort, Punten, Toelichting)
- achter de stylesheet komt een hash, zodat een stijlwijziging niet
  achter de browsercache blijft hangen

## Preview

    python3 -m http.server 4603 --directory docs

of via `preview_start` op naam `bb-preview`.

## Publiceren

GitHub Pages staat ingesteld op de map `docs/` van de hoofdtak. Pushen is dus
deployen.
