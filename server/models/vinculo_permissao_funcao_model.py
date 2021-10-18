from sqlalchemy import Column, BigInteger, ForeignKey, UniqueConstraint
from server.models import AuthenticatorBase
from server.configuration import db
from sqlalchemy.orm import relationship


class VinculoPermissaoFuncao(db.Base, AuthenticatorBase):

    """
        Vínculos NXN de permissões com funções de usuário
    """

    def __init__(self, **kwargs):
        super(VinculoPermissaoFuncao, self).__init__(**kwargs)

    __tablename__ = "tb_vinculo_permissao_funcao"

    __table_args__ = (
        UniqueConstraint('id_permissao', 'id_funcao'),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    id_permissao = Column(BigInteger, ForeignKey("tb_permissao.id"))
    id_funcao = Column(BigInteger, nullable=False)

    permissao = relationship('Permissao', back_populates='vinculos_permissao_funcao')

