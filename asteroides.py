"""
Script de suivi de l'asteroide le plus proche de la Terre via l'API NeoWs NASA.

Appele par le workflow GitHub Actions nasa_hunter.yaml pour :
  1. Interroger l'API NASA du jour
  2. Identifier l'asteroide au passage le plus proche
  3. Recuperer sa probabilite d'impact (API JPL Sentry)
  4. Sauvegarder les resultats en CSV et injecter un rapport dans le README
"""

import math
import os
from datetime import datetime

import pandas as pd
import requests

# Balises HTML dans README.md : le bot remplace le contenu entre les deux
BALISE_DEBUT = "<!-- NASA_START -->"
BALISE_FIN = "<!-- NASA_END -->"

DOSSIER_DATA = "data"
FICHIER_CSV = os.path.join(DOSSIER_DATA, "asteroide_plus_proche.csv")

# API JPL Sentry : probabilites d'impact (NeoWs ne les fournit pas)
URL_SENTRY = "https://ssd-api.jpl.nasa.gov/sentry.api"


def chasser_asteroides() -> None:
    """Point d'entree : API NASA -> asteroide le plus proche -> CSV -> README."""
    aujourdhui = datetime.now().strftime("%Y-%m-%d")
    print(f"Lancement de la chasse pour le : {aujourdhui}")

    api_key = os.environ.get("NASA_API_KEY") or "DEMO_KEY"
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

    asteroides_du_jour = (
        reponse.json().get("near_earth_objects", {}).get(aujourdhui, [])
    )
    plus_proche = trouver_asteroide_plus_proche(asteroides_du_jour, aujourdhui)

    if plus_proche is None:
        texte_rapport = (
            f"### R.A.S le {aujourdhui}\n"
            "Aucun asteroide en approche terrestre recense a cette date."
        )
        sauvegarder_csv_vide(aujourdhui)
        mettre_a_jour_readme(texte_rapport)
        return

    # Probabilite d'impact via Sentry (0 si l'objet n'est pas surveille)
    probabilite = recuperer_probabilite_impact(plus_proche["spk_id"])
    plus_proche["probabilite_impact"] = probabilite
    plus_proche["probabilite_db"] = probabilite_en_decibels(probabilite)

    sauvegarder_csv(plus_proche, aujourdhui)
    texte_rapport = generer_rapport(plus_proche, aujourdhui)
    mettre_a_jour_readme(texte_rapport)


def trouver_asteroide_plus_proche(
    asteroides: list[dict], date_jour: str
) -> dict | None:
    """Parcourt tous les NEO du jour et retourne celui au miss_distance minimal."""
    candidats: list[dict] = []

    for astro in asteroides:
        approche = approche_du_jour(astro, date_jour)
        if approche is None:
            continue

        candidats.append(
            {
                "nom": astro["name"],
                "spk_id": astro["id"],
                "dangereux": astro.get("is_potentially_hazardous_asteroid", False),
                "diametre_max_m": round(
                    astro["estimated_diameter"]["meters"]["estimated_diameter_max"],
                    2,
                ),
                "vitesse_km_h": round(
                    float(
                        approche["relative_velocity"]["kilometers_per_hour"]
                    ),
                    2,
                ),
                "distance_km": round(
                    float(approche["miss_distance"]["kilometers"]),
                    2,
                ),
            }
        )

    if not candidats:
        return None

    # min() sur la distance : l'asteroide qui frôle le plus près la Terre
    return min(candidats, key=lambda item: item["distance_km"])


def approche_du_jour(astro: dict, date_jour: str) -> dict | None:
    """Retourne les donnees d'approche pour la date cible, sinon la premiere dispo."""
    approches = astro.get("close_approach_data", [])
    for approche in approches:
        if approche.get("close_approach_date") == date_jour:
            return approche
    return approches[0] if approches else None


def recuperer_probabilite_impact(spk_id: str) -> float:
    """
    Interroge l'API JPL Sentry pour la probabilite d'impact cumulee.

    Retourne la plus haute probabilite trouvee, ou 0.0 si l'objet
    n'est pas suivi par Sentry (cas le plus frequent).
    """
    try:
        reponse = requests.get(
            URL_SENTRY, params={"spk": spk_id}, timeout=30
        )
        reponse.raise_for_status()
    except requests.RequestException as erreur:
        print(f"Sentry indisponible pour SPK {spk_id} : {erreur}")
        return 0.0

    donnees = reponse.json().get("data", [])
    if not donnees:
        return 0.0

    # Chaque entree Sentry peut lister plusieurs impacts virtuels (champ "ip")
    probabilites = []
    for entree in donnees:
        try:
            probabilites.append(float(entree.get("ip", 0)))
        except (TypeError, ValueError):
            continue

    return max(probabilites) if probabilites else 0.0


def probabilite_en_decibels(probabilite: float) -> float | None:
    """
    Convertit une probabilite p en decibels : 10 * log10(p).

    Exemple : p = 1e-6 -> -60 dB (valeur negative = evenement tres rare).
    Retourne None si p <= 0 (log10 impossible).
    """
    if probabilite <= 0:
        return None
    return round(10 * math.log10(probabilite), 2)


def formater_decibels(probabilite_db: float | None) -> str:
    """Affichage lisible de la probabilite en dB."""
    if probabilite_db is None:
        return "N/A (probabilite nulle ou non surveillee)"
    return f"{probabilite_db} dB"


def sauvegarder_csv(asteroide: dict, date_jour: str) -> None:
    """Ecrit une seule ligne CSV avec l'asteroide le plus proche du jour."""
    os.makedirs(DOSSIER_DATA, exist_ok=True)
    ligne = {
        "Date": date_jour,
        "Nom": asteroide["nom"],
        "Distance_km": asteroide["distance_km"],
        "Diametre_Max_m": asteroide["diametre_max_m"],
        "Vitesse_km_h": asteroide["vitesse_km_h"],
        "Dangereux": asteroide["dangereux"],
        "Probabilite_impact": asteroide["probabilite_impact"],
        "Probabilite_dB": asteroide["probabilite_db"],
    }
    pd.DataFrame([ligne]).to_csv(FICHIER_CSV, index=False, encoding="utf-8")
    print(f"CSV sauvegarde : {FICHIER_CSV}")


def sauvegarder_csv_vide(date_jour: str) -> None:
    """CSV avec en-tetes seulement quand aucun NEO n'est disponible."""
    os.makedirs(DOSSIER_DATA, exist_ok=True)
    pd.DataFrame(
        columns=[
            "Date",
            "Nom",
            "Distance_km",
            "Diametre_Max_m",
            "Vitesse_km_h",
            "Dangereux",
            "Probabilite_impact",
            "Probabilite_dB",
        ]
    ).to_csv(FICHIER_CSV, index=False, encoding="utf-8")
    print(f"CSV vide sauvegarde pour {date_jour}")


def generer_rapport(asteroide: dict, date_jour: str) -> str:
    """Construit le bloc Markdown injecte dans le README."""
    statut = "OUI" if asteroide["dangereux"] else "non"
    db_affichage = formater_decibels(asteroide["probabilite_db"])

    df = pd.DataFrame(
        [
            {
                "Nom": asteroide["nom"],
                "Distance (km)": asteroide["distance_km"],
                "Diametre max (m)": asteroide["diametre_max_m"],
                "Vitesse (km/h)": asteroide["vitesse_km_h"],
                "Potentiellement dangereux": statut,
                "Probabilite d'impact": asteroide["probabilite_impact"],
                "Probabilite (dB)": db_affichage,
            }
        ]
    )

    titre = f"### Asteroide le plus proche le {date_jour}\n\n"
    # to_markdown() necessite tabulate (voir requirements.txt)
    return titre + df.to_markdown(index=False)


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
