from fastapi import HTTPException


class PaginationException(HTTPException):
    def __init__(self, detail: str | None = None):
        super().__init__(
            status_code=400,
            detail="Invalid pagintion params" if detail is None else detail,
        )
