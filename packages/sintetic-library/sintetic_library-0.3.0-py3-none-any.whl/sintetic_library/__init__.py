"""
Sintetic Client Library
Una libreria Python per interfacciarsi con i servizi REST di Sintetic GeoDB
"""

from .core import SinteticClient

__version__ = "0.1.0"
__author__ = "Leandro Rocchi"
__email__ = "leandro.rocchi@cnr.it"

# Rendi disponibili le classi principali a livello di pacchetto
__all__ = ["SinteticClient"]