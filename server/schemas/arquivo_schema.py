from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class FileUploaderInput(BaseModel):

    target: str  # Upload target como S3 bucket
    region: str  # Região do target

    key: str  # File unique key
    type: str  # File type
    content: bytes  # File content
    acl: Optional[str]  # Permissions


class FileUploaderOutput(BaseModel):

    url: str
    additional_data: dict


class ArquivoInput(BaseModel):

    file_name: str = Field(example="Nome do arquivo (com extensão)")
    file_type: str = Field(example="Extensão do arquivo")
    b64_content: str = Field(example="Conteúdo do arquivo codificado em base 64")


class ArquivoOutput(BaseModel):

    id: int
    url: str
    file_type: Optional[str]
    file_name: Optional[str]

    created_at: Optional[datetime] = Field(None)
    updated_at: Optional[datetime] = Field(None)
    created_by: Optional[str] = Field(None)
    updated_by: Optional[str] = Field(None)

    class Config:
        orm_mode = True
        arbitrary_types_allowed = True

