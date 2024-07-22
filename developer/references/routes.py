from ninja import Router

from config.settings.api_errors import API_ERRORS
from .schemas import ApiErrorsClassifier

router = Router(tags=["references"])


@router.get("/errors", auth=None, response=ApiErrorsClassifier)
async def errors(request):
    return {section: [dict(zip(("code", "detail"), x)) for x in mapper.items()]
        for section, mapper in API_ERRORS.items()}
