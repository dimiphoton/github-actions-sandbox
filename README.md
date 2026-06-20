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

### Asteroide le plus proche le 2026-06-20

| Nom          |   Distance (km) |   Diametre max (m) |   Vitesse (km/h) | Potentiellement dangereux   |   Probabilite d'impact | Probabilite (dB)   |
|:-------------|----------------:|-------------------:|-----------------:|:----------------------------|-----------------------:|:-------------------|
| (2014 WA201) |     2.02475e+07 |              25.82 |          53525.5 | non                         |              0.0001586 | -38.0 dB           |

<!-- NASA_END -->
