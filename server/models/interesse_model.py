from sqlalchemy import Column, BigInteger, String, ForeignKey
from server.models import AuthenticatorBase
from server.configuration import db
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid


class Interesse(db.Base, AuthenticatorBase):

    def __init__(self, **kwargs):
        super(Interesse, self).__init__(**kwargs)

    __tablename__ = "tb_interesse"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    nome_referencia = Column(String(), unique=True, nullable=False)  # Utilizado para referenciar a tag, como um ID
    nome_exibicao = Column(String(), unique=True, nullable=False)  # Utilizado para exibir a tag

    descricao = Column(String())

    vinculos_perfil_interesse = relationship(
        'VinculoPerfilInteresse',
        back_populates='interesse'
    )


