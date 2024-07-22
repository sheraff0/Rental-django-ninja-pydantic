from pydantic import BaseModel


class SuccessMessage(BaseModel):
    success: bool = True


class ErrorBase(BaseModel):
    code: str | None = None
    detail: str | None = None
