from math import ceil
from pydantic import BaseModel, create_model


def Paginated(Model: BaseModel):
    return create_model(
        f"{Model.__name__}Page",
        count=(int, ...),
        last=(int, ...),
        current=(int, ...),
        results=(list[Model], ...),
    )


def get_paginated(list_, page: int, size: int, count: int = None):
    _count = count if count is not None else len(list_)
    _last = ceil(_count / size)
    _from = (page - 1) * size
    _to = _from + size
    return dict(
        count=_count,
        last=_last,
        current=page,
        results=list_[_from:_to]
    )


async def get_paginated_queryset(qs, page: int, size: int):
    count = await qs.acount()
    res = get_paginated(qs, page, size, count=count)
    _results = res.pop("results")
    return dict(
        **res,
        results=[x async for x in _results]
    )
