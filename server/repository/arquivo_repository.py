from server.configuration.db import AsyncSession
from typing import Optional
from server.configuration.environment import Environment
from server.models.arquivo_model import Arquivo
from sqlalchemy import insert, literal_column


class ArquivoRepository:

    def __init__(self, db_session: AsyncSession, environment: Optional[Environment] = None):
        self.db_session = db_session
        self.environment = environment

    async def insere_arquivo(self, arquivo_input_dict: dict) -> Arquivo:
        stmt = (
            insert(Arquivo).
            returning(literal_column('*')).
            values(**arquivo_input_dict)
        )
        query = await self.db_session.execute(stmt)
        row_to_dict = dict(query.fetchone())
        return Arquivo(**row_to_dict)

