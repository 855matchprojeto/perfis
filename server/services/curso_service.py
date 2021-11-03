from typing import List, Optional
from server.configuration.environment import Environment
from server.repository.curso_repository import CursoRepository


class CursoService:

    def __init__(self, curso_repo: Optional[CursoRepository] = None, environment: Optional[Environment] = None):
        self.curso_repo = curso_repo
        self.environment = environment

    async def get_all_courses(self):
        return await self.curso_repo.find_all_courses_by_filters([])

