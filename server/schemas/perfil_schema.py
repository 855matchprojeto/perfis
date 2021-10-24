from server.schemas import PerfilModelOutput, PerfilModelInput
from pydantic import Field, BaseModel, EmailStr
from datetime import datetime
from typing import List
from pydantic import BaseModel
from fastapi import Query

InterestQuery = Query(
    None,
    title="Query string para filtrar a entidade por interesses",
    description="Query string para filtrar a entidade pelas tags do tipo 'INTERESSES' relacionadas à entidade",
)

CourseQuery = Query(
    None,
    title="Query string para filtrar a entidade por cursos",
    description="Query string para filtrar a entidade pelas tags do tipo 'CURSO' relacionadas à entidade",
)

