from typing import List
from server.models.interesse_model import Interesse


class InteresseRepository:

    @staticmethod
    def get_interests_in_filter(interests: List[str]):
        return [
            Interesse.nome_referencia.in_(interests)
        ]

