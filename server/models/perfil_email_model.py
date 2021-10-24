from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from server.models import AuthenticatorBase
from server.configuration import db
from sqlalchemy.orm import relationship
from datetime import datetime
from sqlalchemy.dialects.postgresql import UUID
import uuid


class PerfilEmail(db.Base, AuthenticatorBase):

    def __init__(self, **kwargs):
        super(PerfilEmail, self).__init__(**kwargs)

    __tablename__ = "tb_perfil_email"

    guid = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4)
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    id_perfil = Column(BigInteger, ForeignKey("tb_perfil.id"), nullable=False)
    email = Column(String())

