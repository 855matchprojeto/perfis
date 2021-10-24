from typing import List, Optional
from server.models.curso_model import Curso


class CursoRepository:

    @staticmethod
    def get_courses_in_filter(courses: List[str]):
        return [
            Curso.nome_referencia.in_(courses)
        ]

