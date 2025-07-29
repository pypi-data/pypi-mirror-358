import requests
import pandas as pd

def get_worldbank_data(pays, indicator, date_debut=2000, date_fin=2023):
    """
    Fonction générale pour récupérer des données de la World Bank API
    
    Args:
        pays (str ou list): Code pays (ex: 'SN') ou liste de codes
        indicator (str): Code de l'indicateur World Bank
        date_debut (int): Année de début
        date_fin (int): Année de fin
    
    Returns:
        pandas.DataFrame: DataFrame avec les données demandées
    """
    
    url = f"https://api.worldbank.org/v2/country/{pays}/indicator/{indicator}"
    params = {
        "format": "json",
        "date": f"{date_debut}:{date_fin}",
        "per_page": 1000
    }
    
    response = requests.get(url, params=params)
    
    if response.status_code != 200:
        raise Exception(f"Erreur API: {response.status_code}")
    
    data = response.json()
    
    # Vérifier que les données existent
    if len(data) < 2 or not data[1]: 
        return pd.DataFrame() 

    # Les données sont dans data[1] (liste de dictionnaires)
    donnees_utiles = []
    for item in data[1]:
        donnees_utiles.append({
            'pays': item['country']['value'],
            'code_pays': item['countryiso3code'], 
            'annee': int(item['date']),
            'valeur': item['value'],
            'indicateur': item['indicator']['value']
        })
    
    df = pd.DataFrame(donnees_utiles)
    
    # Trier par année pour avoir un ordre logique
    df = df.sort_values('annee').reset_index(drop=True)
    
    return df


def get_pib(pays, date_debut=2000, date_fin=2023):
    """
    Récupère les données du PIB pour un ou plusieurs pays
    
    Args:
        pays (str ou list): Code pays (ex: 'SN') ou liste de codes
        date_debut (int): Année de début
        date_fin (int): Année de fin
    
    Returns:
        pandas.DataFrame: DataFrame avec les données du PIB
    """
    df = get_worldbank_data(pays, "NY.GDP.MKTP.CD", date_debut, date_fin)
    if not df.empty:
        df = df.rename(columns={'valeur': 'pib'})
    return df


def get_export(pays, date_debut=2000, date_fin=2023):
    """
    Récupère les données d'exportation pour un ou plusieurs pays
    
    Args:
        pays (str ou list): Code pays (ex: 'SN') ou liste de codes
        date_debut (int): Année de début
        date_fin (int): Année de fin
    
    Returns:
        pandas.DataFrame: DataFrame avec les données d'exportation
    """
    df = get_worldbank_data(pays, "NE.EXP.GNFS.CD", date_debut, date_fin)
    print(df)
    if not df.empty:
        df = df.rename(columns={'valeur': 'exportations'})
    return df


def get_import(pays, date_debut=2000, date_fin=2023):
    """
    Récupère les données d'importation pour un ou plusieurs pays
    
    Args:
        pays (str ou list): Code pays (ex: 'SN') ou liste de codes
        date_debut (int): Année de début
        date_fin (int): Année de fin
    
    Returns:
        pandas.DataFrame: DataFrame avec les données d'importation
    """
    df = get_worldbank_data(pays, "NE.IMP.GNFS.CD", date_debut, date_fin)
    if not df.empty:
        df = df.rename(columns={'valeur': 'importations'})
    return df

