from sqlalchemy import Column, BigInteger, String, ForeignKey, DateTime
from server.models import AuthenticatorBase
from server.configuration import db
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid
from server.models.perfil_email_model import PerfilEmail
from server.models.perfil_phone_model import PerfilPhone
from server.models.vinculo_perfil_interesse_model import VinculoPerfilInteresse
from server.models.vinculo_perfil_curso_model import VinculoPerfilCurso


class Perfil(db.Base, AuthenticatorBase):

    def __init__(self, **kwargs):
        super(Perfil, self).__init__(**kwargs)

    __tablename__ = "tb_perfil"

    guid = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4)
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    guid_usuario = Column(UUID(as_uuid=True), nullable=False, unique=True)
    bio = Column(String())
    nome_exibicao = Column(String())

    profile_emails = relationship(
        "PerfilEmail",
        primaryjoin=(
            id == PerfilEmail.id_perfil
        )
    )

    profile_phones = relationship(
        "PerfilPhone",
        primaryjoin=(
            id == PerfilPhone.id_perfil
        )
    )

    vinculos_perfil_interesse = relationship(
        'VinculoPerfilInteresse',
        back_populates='perfil'
    )

    vinculos_perfil_curso = relationship(
        'VinculoPerfilCurso',
        back_populates='perfil'
    )

