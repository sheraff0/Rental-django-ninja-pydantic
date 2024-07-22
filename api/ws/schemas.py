from uuid import UUID

from pydantic import BaseModel


class WsClientData(BaseModel):
    client_id: UUID
