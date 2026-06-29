# github-actions-sandbox

Projet minimal pour apprendre GitHub Actions.

## Workflow 1 : Hello World

Le workflow **Mon Premier Hello World** se trouve dans [`.github/workflows/helloworld.yaml`](.github/workflows/helloworld.yaml).

Il se declenche :
- a chaque push sur `main`
- manuellement depuis l'onglet [Actions](https://github.com/dimiphoton/github-actions-sandbox/actions)

## Workflow 2 : NASA Hunter (asteroide le plus proche)

Le workflow [`.github/workflows/nasa_hunter.yaml`](.github/workflows/nasa_hunter.yaml) appelle l'API NASA chaque jour, identifie l'asteroide au passage le plus proche et affiche sa probabilite d'impact en decibels (10 * log10(p), via JPL Sentry).

Donnees brutes : [`data/asteroide_plus_proche.csv`](data/asteroide_plus_proche.csv)

<!-- NASA_START -->

### Asteroide le plus proche le 2026-06-29

| Nom        |   Distance (km) |   Diametre max (m) |   Vitesse (km/h) | Potentiellement dangereux   |   Probabilite d'impact | Probabilite (dB)                          |
|:-----------|----------------:|-------------------:|-----------------:|:----------------------------|-----------------------:|:------------------------------------------|
| (2019 YO4) |     3.59465e+07 |             248.91 |          78532.6 | non                         |                      0 | N/A (probabilite nulle ou non surveillee) |

<!-- NASA_END -->
