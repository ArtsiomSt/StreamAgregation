from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field, model_validator

from .exceptions import PaginationException


class CustomModel(BaseModel):
    id: Optional[int] = None
    created_at: datetime = datetime.utcnow()


class PaginateFields(BaseModel):
    paginate_by: Optional[int] = Field(10, gt=-1, le=20)
    page_num: Optional[int] = Field(0, gt=-1)


class ResponseFromDb(PaginateFields):
    status: str
    data: Any
