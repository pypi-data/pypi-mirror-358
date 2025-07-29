import requests
import pandas as pd

def get_worldbank_data(country, indicator, start_year, end_year):
    """
    Récupère les données de la Banque Mondiale pour un pays et un indicateur donné
    
    Args:
        country (str): Code pays (ex: 'SN' pour Sénégal)
        indicator (str): Code indicateur (ex: 'NY.GDP.MKTP.CD' pour PIB)
        start_year (int): Année de début
        end_year (int): Année de fin
    
    Returns:
        pd.DataFrame: DataFrame contenant les données
    """
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator}"
    params = {
        "format": "json",
        "date": f"{start_year}:{end_year}",
        "per_page": 1000
    }
    
    response = requests.get(url, params=params)
    data = response.json()[1]
    
    records = []
    for entry in data:
        records.append({
            'country': entry['country']['value'],
            'country_code': entry['countryiso3code'],
            'indicator': entry['indicator']['value'],
            'indicator_code': entry['indicator']['id'],
            'year': entry['date'],
            'value': entry['value']
        })
    
    return pd.DataFrame(records)

def get_export(country, start_year, end_year):
    """
    Récupère les données d'exportations de marchandises (USD) pour un pays
    
    Args:
        country (str): Code pays (ex: 'SN')
        start_year (int): Année de début
        end_year (int): Année de fin
    
    Returns:
        pd.DataFrame: DataFrame contenant les données d'exportations
    """
    return get_worldbank_data(country, 'NE.EXP.GNFS.CD', start_year, end_year)

def get_import(country, start_year, end_year):
    """
    Récupère les données d'importations de marchandises (USD) pour un pays
    
    Args:
        country (str): Code pays (ex: 'SN')
        start_year (int): Année de début
        end_year (int): Année de fin
    
    Returns:
        pd.DataFrame: DataFrame contenant les données d'importations
    """
    return get_worldbank_data(country, 'NE.IMP.GNFS.CD', start_year, end_year)

def get_pib(countries, start_year, end_year):
    """
    Récupère les données de PIB (USD courants) pour une liste de pays
    
    Args:
        countries (list): Liste de codes pays (ex: ['SN', 'FR'])
        start_year (int): Année de début
        end_year (int): Année de fin
    
    Returns:
        pd.DataFrame: DataFrame contenant les données de PIB
    """
    dfs = []
    for country in countries:
        df = get_worldbank_data(country, 'NY.GDP.MKTP.CD', start_year, end_year)
        dfs.append(df)
    return pd.concat(dfs)