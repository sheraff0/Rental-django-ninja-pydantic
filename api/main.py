from ninja import NinjaAPI, Swagger
from ninja.errors import ValidationError, HttpError

from contrib.ninja.auth import AuthBearer

from contrib.ninja.errors import validation_error_handler, http_error_handler

from api.auth.routes import router as auth_router
from api.profile.routes import router as profile_router
from api.locations.routes import router as locations_router
from api.references.routes import router as references_router
from api.search.routes import router as search_router
from api.bookings.routes import bookings_router, payments_router
from api.ws.routes import router as ws_router

app = NinjaAPI(
    title="ReHo24 API",
    auth=AuthBearer(),
    urls_namespace="main_api",
    docs=Swagger(settings=dict(persistAuthorization=True))
)

app.add_router("auth", auth_router, tags=["auth"])
app.add_router("profile", profile_router, tags=["profile"])
app.add_router("locations", locations_router, tags=["locations"])
app.add_router("references", references_router, tags=["references"])
app.add_router("search", search_router, tags=["search"])
app.add_router("bookings", bookings_router, tags=["bookings"])
app.add_router("payments", payments_router, tags=["payments"])
app.add_router("ws", ws_router, tags=["ws"])

app.exception_handler(ValidationError)(validation_error_handler(app))
app.exception_handler(HttpError)(http_error_handler(app))
