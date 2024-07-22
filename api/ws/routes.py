from ninja import Router

from contrib.ws_client import WSClient
from .schemas import WsClientData

router = Router()


@router.get("client", response=WsClientData)
async def get_ws_client(request):
    client_id = WSClient.get_client_id(request.user)
    return {"client_id": client_id}
