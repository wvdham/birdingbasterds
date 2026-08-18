# CDNA-punten berekenen

Bij elke update van de scorelijst worden de punten voor CDNA-soorten berekend
in plaats van opgezocht. Bron van de tabellen: `bron/bbpunten_wout.xlsx`
(Wouter, mei 2025). De tabellen staan ook op de site, op `/spelregels/`.

## Werkwijze

1. **Aantal gevallen bepalen** voor Nederland, inclusief gevallen waarvan we
   weten dat ze aanvaard worden. Bron: dutchavifauna.nl, de soortpagina staat
   op `https://www.dutchavifauna.nl/species/<slug>` met de slug uit
   `/list` (bijvoorbeeld `/species/brilzee-eend`). Elke rij in de tabel op die
   pagina is een geval, met datum, provincie en gemeente.
2. **Basispunten opzoeken** bij dat aantal.
3. **Correctiefactor berekenen**: gevallen na 2000 gedeeld door het totaal.
4. **Correctie toepassen**, met de grenzen: omhoog tot maximaal 85 punten,
   omlaag tot minimaal 16 punten.

## Basispunten

| Aantal gevallen | Punten |
|---|---|
| 1e NL | 100 |
| 2e | 90 |
| 5e | 80 |
| 10e | 70 |
| 20e | 50 |
| 30e | 40 |
| 50e | 25 |
| 60e | 20 |
| 60+ | 16 |

## Correctie

| Factor | Correctie |
|---|---|
| <0,1 | +25 |
| 0,1 - 0,15 | +20 |
| 0,15 - 0,2 | +15 |
| 0,2 - 0,3 | +10 |
| 0,3 - 0,4 | +5 |
| 0,4 - 0,6 | 0 |
| 0,6 - 0,7 | -5 |
| 0,7 - 0,8 | -10 |
| 0,8 - 0,9 | -15 |
| 0,9 - 1,0 | -20 |

## Openstaande vragen (nog niet met Wouter afgestemd)

1. Geldt de oude regel nog dat de correctie alleen wordt toegepast op soorten
   met meer dan vijf gevallen? Die stond wel in de spelregels van 2023, niet
   in het werkblad van 2025.
2. Wat krijgt een geval dat tussen twee regels van de basistabel valt, zoals
   het derde geval: de waarde van de vorige regel, of iets ertussenin?
3. Op welk moment wordt het aantal gevallen geteld: bij de claim, of aan het
   eind van het seizoen? Dat maakt verschil zodra er in hetzelfde jaar een
   influx is.

## Proefberekening die niet uitkomt

Brilzee-eend, augustus 2026, geteld op de soortpagina van dutchavifauna:
54 gevallen, waarvan 43 na 2000, dus factor 0,80. Dat geeft 25 basispunten
(vanaf het 50e geval) met een correctie van -10, samen 15, en dus 16 punten
door de ondergrens. In de scorelijst van 2026 staat de Brilzee-eend echter
voor 25 punten. Er zit dus een stap tussen die hier nog niet klopt; zie de
openstaande vragen hierboven.
