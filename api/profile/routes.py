from ninja import Router

import api.profile.services as services
from .schemas import UserInfo, UserModify

router = Router()


@router.get("", response=UserInfo)
async def get_profile(request):
    return request.user


@router.patch("", response=UserInfo)
async def update_profile(request,
    data: UserModify,
):
    return await services.update_profile(request, data)
