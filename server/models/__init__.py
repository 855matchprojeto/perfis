"""
    Módulo responsável por armazenar modelos de dados do sql-alchemy
    e esquemas de input e output do pydantic
"""

from datetime import datetime
from sqlalchemy import Column, String, DateTime


class AuthenticatorBase:
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    created_by = Column(String)
    updated_by = Column(String)

