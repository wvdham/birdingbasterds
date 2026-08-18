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

## Vastgesteld op de proef

De methode is getoetst aan punten die al in de scorelijst staan. Twee dingen
liggen daarmee vast:

- **Tellen tot en met vorig jaar.** De gevallen van het lopende jaar tellen
  niet mee voor de puntenwaarde van dat jaar.
- **"Na 2000" is inclusief 2000**, en een factor die precies op een grens valt
  hoort bij de hogere band (0,800 valt in 0,8 - 0,9).

| Soort | Claimjaar | Gevallen | Factor | Basis | Correctie | Uitkomst | In de lijst |
|---|---|---|---|---|---|---|---|
| Brilzee-eend | 2026 | 35 | 0,800 | 40 | -15 | 25 | 25 |
| Zwartkopgors | 2025 | 23 | 0,652 | 50 | -5 | 45 | 45 |
| Zwartkopgors | 2024 | 23 | 0,652 | 50 | -5 | 45 | 46 |
| Koningseider | 2024 | 19 | 0,632 | 70 | -5 | 65 | 50 |

De twee onderste wijken af. Bij de Zwartkopgors gaat het om één punt, wat past
bij de speelruimte die de spelregels zelf noemen. Bij de Koningseider is het
verschil groot; 50 punten is precies de basiswaarde bij twintig gevallen
zonder correctie, terwijl de teller op negentien stond.

## Rekenhulp

`python3 tools/punten.py [peiljaar] <soort>` doet de telling en de berekening.
Zonder peiljaar telt hij tot en met vorig jaar. De soort mag als slug of als
Nederlandse naam worden opgegeven; bij een naam zoekt het script de slug op in
de soortenlijst.

## Openstaande vragen

1. Geldt de oude regel nog dat de correctie alleen wordt toegepast op soorten
   met meer dan vijf gevallen? Die stond wel in de spelregels van 2023, niet
   in het werkblad van 2025.
2. Wat krijgt een geval dat tussen twee regels van de basistabel valt, zoals
   het derde geval: de waarde van de vorige regel, of iets ertussenin?
   In de proef hierboven is de vorige regel aangehouden.
3. Tellen gevallen die nog in roulatie zijn mee zodra vaststaat dat ze
   aanvaard worden? Dat zou het verschil bij de Koningseider verklaren.
