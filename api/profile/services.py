from django.contrib.auth import get_user_model

from contrib.ninja.auth import authenticate
from contrib.utils.objects import update_instance
from .schemas import UserModify


async def update_profile(request,
    data: UserModify,
):
    User = get_user_model()
    user = await User.objects.select_related("auth_token").aget(pk=request.user.id)
    update_instance(user, data)
    await user.asave()
    # Reset cache
    _token = user.auth_token.key
    await authenticate(_token, reset_cache=True)
    return user
