from pydantic import BaseModel

from api.common.schemas import ErrorBase


class ApiErrorsClassifier(BaseModel):
    common: list[ErrorBase]
    auth: list[ErrorBase]
    locations: list[ErrorBase]
