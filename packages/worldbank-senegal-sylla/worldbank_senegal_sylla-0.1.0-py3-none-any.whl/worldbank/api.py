from .getter import fetch_data

def get_export(country_code, date_start="2000", date_end="2023"):
    """
    Récupère les données d'exportation pour un pays
    
    Args:
        country_code: Code du pays (ex: 'SN')
        date_start: Année de début
        date_end: Année de fin
    
    Returns:
        DataFrame avec les exportations
    """
    return fetch_data(country_code, "NE.EXP.GNFS.CD", date_start, date_end)

def get_import(country_code, date_start="2000", date_end="2023"):
    """
    Récupère les données d'importation pour un pays
    
    Args:
        country_code: Code du pays (ex: 'SN')
        date_start: Année de début
        date_end: Année de fin
    
    Returns:
        DataFrame avec les importations
    """
    return fetch_data(country_code, "NE.IMP.GNFS.CD", date_start, date_end)

def get_pib(country_list, date_start="2000", date_end="2023"):
    """
    Récupère le PIB pour une liste de pays
    
    Args:
        country_list: Liste des codes pays (ex: ['SN', 'FR'])
        date_start: Année de début
        date_end: Année de fin
    
    Returns:
        DataFrame avec le PIB de tous les pays
    """
    import pandas as pd
    df_list = []
    for country in country_list:
        df = fetch_data(country, "NY.GDP.MKTP.CD", date_start, date_end)
        if not df.empty:
            df["code_pays"] = country
            df_list.append(df)
    
    if df_list:
        return pd.concat(df_list, ignore_index=True)
    else:
        return pd.DataFrame()