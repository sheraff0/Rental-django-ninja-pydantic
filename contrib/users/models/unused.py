from datetime import timedelta

from django.apps import apps
from django.conf import settings
from django.db.models import Q, OuterRef, Subquery, Max
from django.utils.timezone import localtime


class UnusedGuesAccountsMixin:
    def last_search(self):
        Search = apps.get_model("bookings", "Search")
        own_search = Search.objects.values("user_id").filter(
            user_id=OuterRef("id")
        ).annotate(
            last_search=Max("update_time")
        ).values("last_search").order_by("user_id")
        return self.get_queryset().annotate(
            last_search=Subquery(own_search)
        )

    def unused_guest_accounts(self):
        _unused_deadline = localtime() - timedelta(days=settings.AUTH_GUEST_ACCOUNT_UNUSED)
        return self.last_search().filter(
            (
                Q(last_search__isnull=True)
                | Q(last_search__lt=_unused_deadline)
            ),
            update_time__lt=_unused_deadline,
            is_verified=False,
        )
