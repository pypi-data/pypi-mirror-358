"""
Module principal pour récupérer les données économiques depuis l'API World Bank
"""

import requests
import pandas as pd
from typing import Optional, List, Union
import logging

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URL de base de l'API World Bank
BASE_URL = "https://api.worldbank.org/v2"

# Indicateurs économiques
INDICATORS = {
    "PIB": "NY.GDP.MKTP.CD",
    "POPULATION": "SP.POP.TOTL",
    "EXPORTATIONS": "NE.EXP.GNFS.CD",
    "IMPORTATIONS": "NE.IMP.GNFS.CD",
    "DEPENSES_PUBLIQUES": "GC.XPN.TOTL.GD.ZS"
}

def _fetch_data(pays: str, indicateur: str, date_debut: int = 2000, 
                date_fin: int = 2023) -> pd.DataFrame:
    """
    Fonction privée pour récupérer les données depuis l'API World Bank
    
    Parameters:
    -----------
    pays : str
        Code ISO du pays (ex: 'SN' pour Sénégal)
    indicateur : str
        Code de l'indicateur World Bank
    date_debut : int
        Année de début (défaut: 2000)
    date_fin : int
        Année de fin (défaut: 2023)
    
    Returns:
    --------
    pd.DataFrame
        DataFrame contenant les données
    """
    url = f"{BASE_URL}/country/{pays}/indicator/{indicateur}"
    params = {
        "format": "json",
        "date": f"{date_debut}:{date_fin}",
        "per_page": 1000
    }
    
    try:
        logger.info(f"Récupération des données pour {pays} - {indicateur}")
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        
        # L'API retourne deux éléments : [metadata, data]
        if len(data) < 2:
            logger.warning("Format de réponse inattendu")
            return pd.DataFrame()
        
        # Extraction des données
        records = data[1]
        if not records:
            logger.warning("Aucune donnée trouvée")
            return pd.DataFrame()
        
        # Création du DataFrame
        df = pd.DataFrame(records)
        
        # Sélection et renommage des colonnes importantes
        df = df[['country', 'date', 'value']].copy()
        df.columns = ['pays', 'annee', 'valeur']
        
        # Conversion des types
        df['annee'] = pd.to_numeric(df['annee'], errors='coerce')
        df['valeur'] = pd.to_numeric(df['valeur'], errors='coerce')
        
        # Ajout du nom du pays
        df['nom_pays'] = df['pays'].apply(lambda x: x['value'] if isinstance(x, dict) else x)
        df['code_pays'] = pays
        
        # Tri par année
        df = df.sort_values('annee').reset_index(drop=True)
        
        return df[['code_pays', 'nom_pays', 'annee', 'valeur']]
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de la requête API: {e}")
        return pd.DataFrame()
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        return pd.DataFrame()


def get_export(pays: str = "SN", date_debut: int = 2000, 
               date_fin: int = 2023) -> pd.DataFrame:
    """
    Détermine l'ensemble des Exportations marchandises d'un pays
    
    Parameters:
    -----------
    pays : str
        Code ISO du pays (défaut: 'SN' pour Sénégal)
    date_debut : int
        Année de début (défaut: 2000)
    date_fin : int
        Année de fin (défaut: 2023)
    
    Returns:
    --------
    pd.DataFrame
        DataFrame contenant les exportations par année
    """
    df = _fetch_data(pays, INDICATORS["EXPORTATIONS"], date_debut, date_fin)
    if not df.empty:
        df.rename(columns={'valeur': 'exportations_usd'}, inplace=True)
    return df


def get_import(pays: str = "SN", date_debut: int = 2000, 
               date_fin: int = 2023) -> pd.DataFrame:
    """
    Détermine l'ensemble des Importations marchandises d'un pays
    
    Parameters:
    -----------
    pays : str
        Code ISO du pays (défaut: 'SN' pour Sénégal)
    date_debut : int
        Année de début (défaut: 2000)
    date_fin : int
        Année de fin (défaut: 2023)
    
    Returns:
    --------
    pd.DataFrame
        DataFrame contenant les importations par année
    """
    df = _fetch_data(pays, INDICATORS["IMPORTATIONS"], date_debut, date_fin)
    if not df.empty:
        df.rename(columns={'valeur': 'importations_usd'}, inplace=True)
    return df


def get_pib(pays: Union[str, List[str]] = "SN", date_debut: int = 2000, 
            date_fin: int = 2023) -> pd.DataFrame:
    """
    Détermine le PIB (USD courants) d'une liste de pays
    
    Parameters:
    -----------
    pays : str ou List[str]
        Code ISO du pays ou liste de codes (défaut: 'SN' pour Sénégal)
    date_debut : int
        Année de début (défaut: 2000)
    date_fin : int
        Année de fin (défaut: 2023)
    
    Returns:
    --------
    pd.DataFrame
        DataFrame contenant le PIB par pays et par année
    """
    # Convertir en liste si c'est une chaîne
    if isinstance(pays, str):
        pays_list = [pays]
    else:
        pays_list = pays
    
    all_data = []
    
    for p in pays_list:
        df = _fetch_data(p, INDICATORS["PIB"], date_debut, date_fin)
        if not df.empty:
            df.rename(columns={'valeur': 'pib_usd'}, inplace=True)
            all_data.append(df)
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()


# Fonction utilitaire supplémentaire
def get_all_indicators(pays: str = "SN", date_debut: int = 2000, 
                      date_fin: int = 2023) -> pd.DataFrame:
    """
    Récupère tous les indicateurs disponibles pour un pays
    
    Parameters:
    -----------
    pays : str
        Code ISO du pays (défaut: 'SN' pour Sénégal)
    date_debut : int
        Année de début (défaut: 2000)
    date_fin : int
        Année de fin (défaut: 2023)
    
    Returns:
    --------
    pd.DataFrame
        DataFrame contenant tous les indicateurs
    """
    all_data = []
    
    for name, code in INDICATORS.items():
        df = _fetch_data(pays, code, date_debut, date_fin)
        if not df.empty:
            df['indicateur'] = name
            all_data.append(df)
    
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()
