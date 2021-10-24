from sqlalchemy import Column, BigInteger, ForeignKey, UniqueConstraint
from server.models import AuthenticatorBase
from server.configuration import db
from sqlalchemy.orm import relationship


class VinculoPerfilCurso(db.Base, AuthenticatorBase):

    """
        Vínculos NXN de permissões com funções de usuário
    """

    def __init__(self, **kwargs):
        super(VinculoPerfilCurso, self).__init__(**kwargs)

    __tablename__ = "tb_vinculo_perfil_curso"

    __table_args__ = (
        UniqueConstraint('id_perfil', 'id_curso'),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    id_perfil = Column(BigInteger, ForeignKey("tb_perfil.id"))
    id_curso = Column(BigInteger, ForeignKey("tb_curso.id"))

    perfil = relationship('Perfil', back_populates='vinculos_perfil_curso')
    curso = relationship('Curso', back_populates='vinculos_perfil_curso')

