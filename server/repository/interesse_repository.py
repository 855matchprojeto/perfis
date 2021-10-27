from typing import List, Optional
from server.models.interesse_model import Interesse
from server.configuration.db import AsyncSession
from server.configuration.environment import Environment
from server.models.interesse_model import Interesse
from sqlalchemy import select


class InteresseRepository:

    @staticmethod
    def get_interests_in_filter(interests: List[str]):
        return [
            Interesse.nome_referencia.in_(interests)
        ]

    def __init__(self, db_session: AsyncSession, environment: Optional[Environment] = None):
        self.db_session = db_session
        self.environment = environment

    async def find_all_interests_by_filters(self, filters) -> List[Interesse]:

        stmt = (
            select(Interesse).
            where(
                *filters
            )
        )

        # Executando a query
        query = await self.db_session.execute(stmt)
        cursos = query.scalars().unique().all()

        return cursos

