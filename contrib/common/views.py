from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import redirect

from rest_framework import status
from rest_framework.decorators import action
from rest_framework.response import Response

from drf_spectacular.utils import extend_schema, OpenApiParameter

from contrib.utils.text import param_to_bool


class StandardActionMixin:
    def standard_action(self, instance=None, save=False, partial=True):
        serializer = self.get_serializer(instance=instance, data=self.request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if save:
            serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


def health_check_view(request):
    return JsonResponse({"message": "I'm alive!"})


def swagger_redirect(request):
    return redirect("/api/v1/docs")

