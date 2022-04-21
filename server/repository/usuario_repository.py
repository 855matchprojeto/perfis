from sqlalchemy import insert, literal_column
from server.models.usuario_model import Usuario
from server.configuration.db import AsyncSession
from server.configuration.environment import Environment
from typing import Optional


class UsuarioRepository:

    def __init__(self, db_session: AsyncSession, environment: Optional[Environment] = None):
        self.db_session = db_session
        self.environment = environment

    async def insere_usuario(self, usuario_dict: dict) -> Usuario:
        stmt = (
            insert(Usuario).
            returning(literal_column('*')).
            values(**usuario_dict)
        )
        query = await self.db_session.execute(stmt)
        row_to_dict = dict(query.fetchone())
        return Usuario(**row_to_dict)

