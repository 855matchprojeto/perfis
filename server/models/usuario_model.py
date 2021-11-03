import uuid
from sqlalchemy import Column, String, Boolean
from sqlalchemy.dialects.postgresql import UUID
from server.models import AuthenticatorBase
from server.configuration import db


class Usuario(db.Base, AuthenticatorBase):

    # Informações de usuário que TAMBÉM
    # serão armazenadas no serviço de PERFIS

    # Caso seja necessário capturar alguma informação
    # de usuário, teremos uma réplica nesse serviço

    def __init__(self, **kwargs):
        super(Usuario, self).__init__(**kwargs)

    __tablename__ = "tb_usuario"

    guid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome = Column(String(), nullable=False)
    username = Column(String(), unique=True, nullable=False)
    email = Column(String(), unique=True, nullable=False)
    email_verificado = Column(Boolean(), default=False)

