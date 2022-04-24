from pydantic import BaseModel
from typing import Any, Optional


class Cursor(BaseModel):

    previous_encoded_cursor: Optional[str]
    sort_field_key: str
    sort_field_type: str
    operator: str
    value: Any
    id: int

