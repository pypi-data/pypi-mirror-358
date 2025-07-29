"""
Package pour l'analyse des données économiques via l'API World Bank
"""

from .getter import get_export, get_import, get_pib

__version__ = "0.1.0"
__author__ = "Maramata DIOP"
__email__ = "maramatad@gmail.com"

__all__ = ["get_export", "get_import", "get_pib"]
