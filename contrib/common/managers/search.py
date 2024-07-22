import re

from django.db.models import Q, F
from django.db.models.functions import Concat
from django.contrib.postgres.search import TrigramDistance


class SearchMixin:
    search_fields: list = ["name"]
    simple_max_symbols = 2
    trigram_max_distance = 0.9

    def search(self, q=None):
        qs = self
        _filter = Q()
        _order_by = self.search_fields
        if q:
            if len(q) <= self.simple_max_symbols:
                # Simple search
                for field in self.search_fields:
                    lookup = f"{field}__istartswith"
                    _filter |= Q(**{lookup: q})
            else:
                # Trigram distance search
                qs = qs.trigram_distance(q)
                _filter = Q(trigram_distance__lt=self.trigram_max_distance)
                _order_by = ["trigram_distance", *self.search_fields]

        return qs.filter(_filter).order_by(*_order_by)

    def compound(self):
        return self.annotate(
            compound=Concat(*map(F, self.search_fields)) if len(self.search_fields) > 1
                else F(self.search_fields[0])
        )

    def trigram_distance(self, q: str):
        return self.compound().annotate(
            trigram_distance=TrigramDistance("compound", q)
        )
