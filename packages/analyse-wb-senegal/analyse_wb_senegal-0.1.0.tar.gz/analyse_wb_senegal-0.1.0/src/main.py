import pandas as pd
import sys

sys.path.append("src")


dataframe=get_export("SN", "2000", "2023")

pd.set_option('display.float_format', '{:,.0f}'.format)
print(dataframe)


def get_import(code_pays="SN", debut_periode="2000", fin_periode="2023"):
    """
    Récupère les importations de marchandises (USD) pour un pays et une période donnée.
    Affiche la première ligne de données pour analyse.
    Retourne un DataFrame pandas.
    """
    url = f"https://api.worldbank.org/v2/country/{code_pays}/indicator/NE.IMP.GNFS.CD"
    parametres = {
        "format": "json",
        "date": f"{debut_periode}:{fin_periode}",
        "per_page": 1000
    }
    reponse = requests.get(url, params=parametres)
    if reponse.status_code != 200:
        raise Exception(f"Erreur lors de l'appel à l'API World Bank: {reponse.status_code}")
    donnees = reponse.json()[1]
    # Affiche la première ligne du JSON pour inspection
    print("Premier élément des données importations :")
    print(json.dumps(donnees[0], indent=2, ensure_ascii=False))

    liste_lignes = []
    for ligne in donnees:
        dictionnaire = {
            "pays": ligne["country"]["value"],
            "annee": ligne["date"],
            "importations_usd": ligne["value"]
        }
        liste_lignes.append(dictionnaire)
    tableau = pd.DataFrame(liste_lignes)
    return tableau


def get_pib(liste_pays=["SN"], debut_periode="2000", fin_periode="2023"):
    """
    Récupère le PIB (USD courants) pour une liste de pays et une période donnée.
    Affiche la première ligne de données pour chaque pays.
    Retourne un DataFrame pandas avec tous les résultats.
    """
    if isinstance(liste_pays, str):
        liste_pays = [liste_pays]
    tableaux = []
    for code_pays in liste_pays:
        url = f"https://api.worldbank.org/v2/country/{code_pays}/indicator/NY.GDP.MKTP.CD"
        parametres = {
            "format": "json",
            "date": f"{debut_periode}:{fin_periode}",
            "per_page": 1000
        }
        reponse = requests.get(url, params=parametres)
        if reponse.status_code != 200:
            raise Exception(f"Erreur lors de l'appel à l'API World Bank: {reponse.status_code}")
        donnees = reponse.json()[1]
        # Affiche la première ligne du JSON pour chaque pays
        print(f"Premier élément des données PIB pour {code_pays} :")
        print(json.dumps(donnees[0], indent=2, ensure_ascii=False))

        liste_lignes = []
        for ligne in donnees:
            dictionnaire = {
                "pays": ligne["country"]["value"],
                "annee": ligne["date"],
                "pib_usd": ligne["value"]
            }
            liste_lignes.append(dictionnaire)
        tableau = pd.DataFrame(liste_lignes)
        tableaux.append(tableau)
    # Concatène tous les tableaux pour différents pays
    return pd.concat(tableaux, ignore_index=True)


