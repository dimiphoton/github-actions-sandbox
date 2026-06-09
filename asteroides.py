"""
Script de chasse aux astéroïdes dangereux via l'API NeoWs de la NASA.

Appelé par le workflow GitHub Actions nasa_hunter.yaml pour :
  1. Interroger l'API NASA du jour
  2. Sauvegarder les résultats en CSV
  3. Injecter un rapport Markdown dans le README
"""

import os
from datetime import datetime

import pandas as pd
import requests

# Balises HTML dans README.md : le bot remplace le contenu entre les deux
BALISE_DEBUT = "<!-- NASA_START -->"
BALISE_FIN = "<!-- NASA_END -->"

# Chemin du fichier CSV généré (commité par le workflow)
DOSSIER_DATA = "data"
FICHIER_CSV = os.path.join(DOSSIER_DATA, "asteroides_dangereux.csv")


def chasser_asteroides() -> None:
    """Point d'entrée principal : API NASA → CSV → README."""
    aujourdhui = datetime.now().strftime("%Y-%m-%d")
    print(f"Lancement de la chasse pour le : {aujourdhui}")

    # Clé API : variable d'environnement (secret GitHub) ou DEMO_KEY gratuite
    api_key = os.environ.get("NASA_API_KEY", "DEMO_KEY")
    url = (
        "https://api.nasa.gov/neo/rest/v1/feed"
        f"?start_date={aujourdhui}&end_date={aujourdhui}&api_key={api_key}"
    )

    try:
        reponse = requests.get(url, timeout=30)
        reponse.raise_for_status()
    except requests.RequestException as erreur:
        print(f"Erreur API NASA : {erreur}")
        return

    data = reponse.json()
    asteroides_du_jour = data.get("near_earth_objects", {}).get(aujourdhui, [])
    liste_filtree = []

    # On ne garde que les astéroïdes marqués "potentiellement dangereux"
    for astro in asteroides_du_jour:
        if astro.get("is_potentially_hazardous_asteroid") is True:
            liste_filtree.append(
                {
                    "Date": aujourdhui,
                    "Nom": astro["name"],
                    "Diametre_Max_m": round(
                        astro["estimated_diameter"]["meters"]["estimated_diameter_max"],
                        2,
                    ),
                    "Vitesse_km_h": round(
                        float(
                            astro["close_approach_data"][0]["relative_velocity"][
                                "kilometers_per_hour"
                            ]
                        ),
                        2,
                    ),
                    "Distance_km": round(
                        float(
                            astro["close_approach_data"][0]["miss_distance"]["kilometers"]
                        ),
                        2,
                    ),
                }
            )

    # --- Export CSV (historique des détections) ---
    os.makedirs(DOSSIER_DATA, exist_ok=True)
    df = pd.DataFrame(liste_filtree)

    if df.empty:
        # CSV vide mais avec les colonnes attendues
        df = pd.DataFrame(
            columns=[
                "Date",
                "Nom",
                "Diametre_Max_m",
                "Vitesse_km_h",
                "Distance_km",
            ]
        )

    df.to_csv(FICHIER_CSV, index=False, encoding="utf-8")
    print(f"CSV sauvegarde : {FICHIER_CSV} ({len(liste_filtree)} asteroide(s))")

    # --- Génération du texte dynamique pour le README ---
    if liste_filtree:
        df_affichage = df.rename(
            columns={
                "Diametre_Max_m": "Diametre Max (m)",
                "Vitesse_km_h": "Vitesse (km/h)",
                "Distance_km": "Distance (km)",
            }
        )
        texte_rapport = (
            f"### Alerte : {len(liste_filtree)} asteroide(s) detecte(s) le {aujourdhui}\n\n"
        )
        # to_markdown() necessite le package tabulate (voir requirements.txt)
        texte_rapport += df_affichage[["Nom", "Diametre Max (m)", "Vitesse (km/h)", "Distance (km)"]].to_markdown(
            index=False
        )
    else:
        texte_rapport = (
            f"### R.A.S le {aujourdhui}\n"
            "Aucun asteroide dangereux ne frole la Terre aujourd'hui. L'espace est calme."
        )

    mettre_a_jour_readme(texte_rapport)


def mettre_a_jour_readme(texte_rapport: str) -> None:
    """Remplace le contenu entre BALISE_DEBUT et BALISE_FIN dans README.md."""
    if not os.path.exists("README.md"):
        print("README.md introuvable, injection ignoree.")
        return

    with open("README.md", encoding="utf-8") as fichier:
        contenu = fichier.read()

    if BALISE_DEBUT not in contenu or BALISE_FIN not in contenu:
        print(
            f"Balises {BALISE_DEBUT} / {BALISE_FIN} manquantes dans README.md."
        )
        return

    # split()[0] = texte avant la balise ouvrante
    # split()[1] = texte apres la balise fermante
    partie_haute = contenu.split(BALISE_DEBUT)[0]
    partie_basse = contenu.split(BALISE_FIN)[1]

    nouveau_readme = (
        f"{partie_haute}{BALISE_DEBUT}\n\n{texte_rapport}\n\n{BALISE_FIN}{partie_basse}"
    )

    with open("README.md", "w", encoding="utf-8") as fichier:
        fichier.write(nouveau_readme)

    print("README.md mis a jour dynamiquement !")


if __name__ == "__main__":
    chasser_asteroides()
