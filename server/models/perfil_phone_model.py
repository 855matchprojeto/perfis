from sqlalchemy import Column, BigInteger, String, DateTime, ForeignKey
from server.models import AuthenticatorBase
from server.configuration import db
from sqlalchemy.orm import relationship
from datetime import datetime
from server.models.tipo_contato_model import TipoContato
from sqlalchemy.dialects.postgresql import UUID
import uuid


class PerfilPhone(db.Base, AuthenticatorBase):

    def __init__(self, **kwargs):
        super(PerfilPhone, self).__init__(**kwargs)

    __tablename__ = "tb_perfil_phone"

    guid = Column(UUID(as_uuid=True), nullable=False, unique=True, default=uuid.uuid4)
    id = Column(BigInteger, primary_key=True, autoincrement=True)
    id_perfil = Column(BigInteger, ForeignKey("tb_perfil.id"), nullable=False)
    phone = Column(String())

    id_tipo_contato = Column(BigInteger, ForeignKey("tb_tipo_contato.id"))
    tipo_contato = relationship("TipoContato", foreign_keys=[id_tipo_contato])

    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String)

