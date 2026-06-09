# github-actions-sandbox

Projet minimal pour apprendre GitHub Actions.

## Workflow 1 : Hello World

Le workflow **Mon Premier Hello World** se trouve dans [`.github/workflows/helloworld.yaml`](.github/workflows/helloworld.yaml).

Il se declenche :
- a chaque push sur `main`
- manuellement depuis l'onglet [Actions](https://github.com/dimiphoton/github-actions-sandbox/actions)

## Workflow 2 : NASA Hunter (asteroides dangereux)

Le workflow [`.github/workflows/nasa_hunter.yaml`](.github/workflows/nasa_hunter.yaml) appelle l'API NASA chaque jour et met a jour la section ci-dessous.

Donnees brutes : [`data/asteroides_dangereux.csv`](data/asteroides_dangereux.csv)

<!-- NASA_START -->

*Le robot n'a pas encore mis a jour les donnees.*

<!-- NASA_END -->
