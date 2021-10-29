from typing import List, Optional
from server.configuration.environment import Environment
from server.repository.interesse_repository import InteresseRepository


class InteresseService:

    def __init__(
        self,
        interesse_repo: Optional[InteresseRepository] = None,
        environment: Optional[Environment] = None
    ):
        self.interesse_repo = interesse_repo
        self.environment = environment

    async def get_all_interests(self):
        return await self.interesse_repo.find_all_interests_by_filters([])

