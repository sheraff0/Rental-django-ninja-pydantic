from ninja import NinjaAPI, Swagger
from ninja.errors import ValidationError, HttpError

from contrib.ninja.auth import AuthBearer
from contrib.ninja.errors import validation_error_handler, http_error_handler

from .travelline.routes import router as travelline_router
from .sms_aero.routes import router as sms_aero_router
from .paykeeper.routes import router as paykeeper_router
from .references.routes import router as references_router

app = NinjaAPI(
    title="ReHo24 Developer's panel",
    #auth=AuthBearer(is_superuser=True),
    auth=AuthBearer(),
    urls_namespace="deleloper_api",
    docs=Swagger(settings=dict(persistAuthorization=True))
)

app.add_router("travelline", travelline_router)
app.add_router("sms-aero", sms_aero_router)
app.add_router("paykeeper", paykeeper_router)
app.add_router("references", references_router)

app.exception_handler(ValidationError)(validation_error_handler(app))
app.exception_handler(HttpError)(http_error_handler(app))
