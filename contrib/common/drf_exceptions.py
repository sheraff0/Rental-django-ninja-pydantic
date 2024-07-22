from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.conf import settings

def core_exception_handler(exc, context):
    response = exception_handler(exc, context)
    handlers = {
        'ValidationError': _handle_generic_error
    }
    exception_class = exc.__class__.__name__

    if exception_class in handlers:
        return handlers[exception_class](exc, context, response)

    return response


def _handle_generic_error(exc, context, response):
    if response:
        response.data = {
            'errors': response.data
        }
        return response
    else:
        if settings.DEBUG:
            return response
        return Response(data=dict(errors="Some thing go wrong :/ We are working to fix it"), status=500)