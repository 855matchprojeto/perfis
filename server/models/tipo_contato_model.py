from sqlalchemy import Column, BigInteger, String, ForeignKey
from server.models import AuthenticatorBase
from server.configuration import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid


class TipoContato(db.Base, AuthenticatorBase):

    def __init__(self, **kwargs):
        super(TipoContato, self).__init__(**kwargs)

    __tablename__ = "tb_tipo_contato"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nome_referencia = Column(String(), unique=True, nullable=False)  # Utilizado para referenciar a tag
    nome_exibicao = Column(String(), unique=True, nullable=False)  # Utilizado para exibir a tag

    descricao = Column(String())
