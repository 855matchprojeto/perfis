from sqlalchemy import Column, BigInteger, String
from server.models import AuthenticatorBase
from server.configuration import db
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Arquivo(db.Base, AuthenticatorBase):

    def __init__(self, **kwargs):
        super(Arquivo, self).__init__(**kwargs)

    __tablename__ = "tb_arquivo"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guid = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4)

    url = Column(String)
    file_type = Column(String)
    file_name = Column(String)

