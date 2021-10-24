from pydantic import BaseModel
from typing import Any


class Cursor(BaseModel):

    sort_field_key: str
    sort_field_type: str
    value: Any

