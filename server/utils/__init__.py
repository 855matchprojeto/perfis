"""
    Funções auxiliares
"""

from unicodedata import normalize


def normalize_string(string: str):
    return normalize('NFKD', string).encode('ASCII', 'ignore').decode('ASCII')

