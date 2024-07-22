"""
Project URL Configuration

"""
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path

from django.conf import settings 

from api.main import app as main_api
from developer.main import app as developer_api
from contrib.common.views import health_check_view, swagger_redirect

urlpatterns = [
    path("health", health_check_view),
    path('admin/', admin.site.urls),
    path("api/v1/", main_api.urls),
    path("developer/", developer_api.urls),
    *staticfiles_urlpatterns(),
] + static(settings.MEDIA_RELATIVE_URL, document_root=settings.MEDIA_ROOT)

# Debug toolbar
if settings.DEBUG and settings.TOOLBAR and not settings.TESTING_MODE:
    import debug_toolbar

    urlpatterns = [path("__debug__/", include(debug_toolbar.urls)), *urlpatterns]


# Silk
if settings.DEBUG and settings.SILK and not settings.TESTING_MODE:
    urlpatterns += [path('silk/', include('silk.urls', namespace='silk'))]


# DRF Spectacular
if settings.SWAGGER:

    from drf_spectacular.views import (SpectacularAPIView,
                                       SpectacularSwaggerView)

    urlpatterns += [
        #path("api/schema/", SpectacularAPIView.as_view(), name="api-schema"),
        #path("swagger/", SpectacularSwaggerView.as_view(url_name="api-schema"), name="api-docs")
        path("swagger/", swagger_redirect),
    ]
