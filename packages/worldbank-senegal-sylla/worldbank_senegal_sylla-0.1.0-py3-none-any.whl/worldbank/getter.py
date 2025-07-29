import requests
import pandas as pd

BASE_URL = "https://api.worldbank.org/v2/country/{}/indicator/{}"

def fetch_data(country_code, indicator_code, date_start="2000", date_end="2023"):
    """
    Récupère les données depuis l'API World Bank
    
    Args:
        country_code: Code du pays (ex: 'SN')
        indicator_code: Code de l'indicateur
        date_start: Année de début (défaut: "2000")
        date_end: Année de fin (défaut: "2023")
    
    Returns:
        DataFrame avec les données
    """
    url = BASE_URL.format(country_code, indicator_code)
    params = {
        "format": "json",
        "date": f"{date_start}:{date_end}",
        "per_page": 1000
    }

    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception(f"Erreur API {response.status_code}")

    data = response.json()
    if not data or len(data) < 2 or not data[1]:
        return pd.DataFrame()

    records = []
    for item in data[1]:
        records.append({
            "pays": item["country"]["value"],
            "code": item["country"]["id"],
            "date": item["date"],
            "valeur": item["value"]
        })
    
    df = pd.DataFrame(records)
    # Conversion des types
    df["date"] = pd.to_numeric(df["date"], errors="coerce")
    df["valeur"] = pd.to_numeric(df["valeur"], errors="coerce")
    
    return df.sort_values("date").reset_index(drop=True)