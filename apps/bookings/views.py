from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from drf_spectacular.utils import extend_schema

from external.travelline.api import travelline_sync_client


class BookingViewSet(GenericViewSet):
    @action(detail=False)
    @travelline_sync_client
    async def tl_search_room_stays(self, request, client=None):
        return Response({})
