import requests
import pandas as pd

BASE_URL = "https://api.worldbank.org/v2"

def get_data(pays, indicateur, date_debut="2000", date_fin="2023"):
    url = f"{BASE_URL}/country/{pays}/indicator/{indicateur}"
    params = {
        "format": "json",
        "date": f"{date_debut}:{date_fin}",
        "per_page": 1000
    }
    response = requests.get(url, params=params)
    data = response.json()
    
    if not data or len(data) < 2:
        raise ValueError("Données non disponibles ou erreur dans l'API.")
    
    records = data[1]
    df = pd.DataFrame([{
        "pays": r["country"]["value"],
        "date": r["date"],
        "valeur": r["value"]
    } for r in records])

    df["date"] = pd.to_datetime(df["date"], format="%Y")
    return df.sort_values("date")


def get_export(pays):
    return get_data(pays, "NE.EXP.GNFS.CD")

def get_import(pays):
    return get_data(pays, "NE.IMP.GNFS.CD")

def get_pib(pays_list):
    frames = []
    for pays in pays_list:
        df = get_data(pays, "NY.GDP.MKTP.CD")
        df["code_pays"] = pays
        frames.append(df)
    return pd.concat(frames, ignore_index=True)
