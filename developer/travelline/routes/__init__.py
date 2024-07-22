from ninja import Router

from .content import router as content_router
from .search import router as search_router
from .reservation import router as reservation_router

router = Router()

router.add_router("content", content_router, tags=["TL: content"])
router.add_router("search", search_router, tags=["TL: search"])
router.add_router("reservation", reservation_router, tags=["TL: reservation"])
