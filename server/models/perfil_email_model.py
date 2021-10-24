from sqlalchemy import Column, BigInteger, String, DateTime
from server.models import AuthenticatorBase
from server.configuration import db
from sqlalchemy.orm import relationship
from datetime import datetime


class PerfilEmail(db.Base, AuthenticatorBase):

    def __init__(self, **kwargs):
        super(PerfilEmail, self).__init__(**kwargs)

    __tablename__ = "tb_perfil_email"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    id_perfil = Column(BigInteger, nullable=False)
    email = Column(String())

