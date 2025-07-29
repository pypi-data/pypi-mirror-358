## 2. src/worldbank/__init__.py

"""
WorldBank Senegal Package
Analyse des données économiques du Sénégal avec l'API World Bank
"""

__version__ = "0.1.0"

from .api import get_export, get_import, get_pib

__all__ = ["get_export", "get_import", "get_pib"]
