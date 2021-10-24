from sqlalchemy import Column, BigInteger, ForeignKey, UniqueConstraint
from server.models import AuthenticatorBase
from server.configuration import db
from sqlalchemy.orm import relationship


class VinculoPerfilInteresse(db.Base, AuthenticatorBase):

    """
        Vínculos NXN de permissões com funções de usuário
    """

    def __init__(self, **kwargs):
        super(VinculoPerfilInteresse, self).__init__(**kwargs)

    __tablename__ = "tb_vinculo_perfil_interesse"

    __table_args__ = (
        UniqueConstraint('id_perfil', 'id_interesse'),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    id_perfil = Column(BigInteger, ForeignKey("tb_perfil.id"))
    id_interesse = Column(BigInteger, ForeignKey("tb_interesse.id"))

    perfil = relationship('Perfil', back_populates='vinculos_perfil_interesse')
    interesse = relationship('Interesse', back_populates='vinculos_perfil_interesse')

