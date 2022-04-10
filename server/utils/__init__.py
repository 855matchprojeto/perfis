"""
    Funções auxiliares
"""

from unicodedata import normalize
import base64


def normalize_string(string: str):
    return normalize('NFKD', string).encode('ASCII', 'ignore').decode('ASCII')


def decode_b64_str(b64_encoded_str) -> bytes:
    return base64.b64decode(b64_encoded_str)

