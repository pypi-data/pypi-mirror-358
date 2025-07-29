import requests
import pandas as pd

BASE_URL = "https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"

def fetch_data(country, indicator, start_year=2000, end_year=2023):
    url = BASE_URL.format(country=country, indicator=indicator)
    params = {
        "format": "json",
        "date": f"{start_year}:{end_year}",
        "per_page": 1000
    }

    response = requests.get(url, params=params)
    data = response.json()

    if isinstance(data, list) and len(data) == 2:
        records = data[1]
        return pd.DataFrame.from_records([
            {
                "country": rec["country"]["value"],
                "year": int(rec["date"]),
                "value": rec["value"]
            } for rec in records if rec["value"] is not None
        ])
    else:
        raise ValueError("Erreur dans la récupération des données")

def get_export(country, start_year=2000, end_year=2023):
    return fetch_data(country, "NE.EXP.GNFS.CD", start_year, end_year)

def get_import(country, start_year=2000, end_year=2023):
    return fetch_data(country, "NE.IMP.GNFS.CD", start_year, end_year)

def get_pib(countries, start_year=2000, end_year=2023):
    all_data = []
    for country in countries:
        df = fetch_data(country, "NY.GDP.MKTP.CD", start_year, end_year)
        all_data.append(df)
    return pd.concat(all_data, ignore_index=True)
