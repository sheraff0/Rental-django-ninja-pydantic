from contrib.common.filters import FilterSet


class SearchFilterSet(FilterSet):
    price_min = staticmethod(lambda x, v: x.lowest_price_offer.price >= v)
    price_max = staticmethod(lambda x, v: x.lowest_price_offer.price <= v)
    room_type_categories = staticmethod(lambda x, v: x.room_type_info.category.code in v)
    #rooms_count: int | None = None
    beds_count = staticmethod(lambda x, v: x.room_type_info.beds in v)
    #downtown_distance: int | None = None
    #floor_min: int | None = None
    #floor_max: int | None = None
    #floor_type: FloorType | None = None

    @staticmethod
    def amenities(x, v):
        amenities = set(a.code for a in x.room_type_info.amenities)
        return set(v) == set(v) & amenities
