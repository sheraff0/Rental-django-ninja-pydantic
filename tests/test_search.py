import json

from datetime import datetime, timedelta
from django.test import TestCase

from api.search.schemas import SearchRequest, SearchRequestDetailed, SearchFilters, SearchCoords
from apps.bookings.models import Search
from apps.properties.models import Property
from apps.shared.models import Region, City
from .mixins import AuthSetupMixin, ContentSetupMixin


class SearchTestCase(ContentSetupMixin, AuthSetupMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.setup_auth_data()
        cls.setup_content()
        cls.clear_redis_cache()

    @classmethod
    def tearDownClass(cls):
        cls.destroy_content()

    def region_search(self, region_db):
        res = self.client.get(f"/api/v1/locations/regions?q={region_db.name[:15]}",
            headers=self.auth_header)
        assert res.json()[0]["id"] == region_db.pk

    def city_search(self, city_db):
        res = self.client.get(f"/api/v1/locations/cities?q={city_db.name[:8]}",
            headers=self.auth_header)
        assert res.json()[0]["id"] == city_db.pk

    def test_locations(self):
        for region_db in Region.objects.prefetch_related("cities").all():
            self.region_search(region_db)
            for city in region_db.cities.all():
                self.city_search(city)

    def get_search_request(self, city_id, filters=None):
        today = datetime.now().date()
        t1 = today + timedelta(days=1)
        t2 = today + timedelta(days=2)
        return SearchRequest(
            params=dict(
                arrival_date=t1, departure_date=t2,
                adults=2, children=[5]
            ),
            city_id=city_id,
            filters=SearchFilters(**filters).model_dump(exclude_none=True) if filters else None,
        ).model_dump()

    def check_room_type(self, params, accomodation):
        _room_type_id = accomodation["room_type_info"]["id"]
        search_request_detailed = SearchRequestDetailed(
            params=params,
            room_type_id=_room_type_id,
        ).model_dump()
        res = self.client.post(f"/api/v1/search/detailed", data=search_request_detailed,
            content_type="application/json", headers=self.auth_header)
        _offer = res.json()["accomodation"]["offers"][0]
        _lowest_price_offer = accomodation["lowest_price_offer"]
        assert _offer["price"] == _lowest_price_offer["price"]

    def check_city(self, city_db, filters=None):
        print(f"\nSearching accomodations for {city_db.name} ({city_db.region.name})...\n")
        _city_id = city_db.id

        # Search by city
        search_request = self.get_search_request(_city_id, filters=filters)
        res = self.client.post(f"/api/v1/search?size=10", data=search_request,
            content_type="application/json", headers=self.auth_header)
        _search_id = res.json()["search"]["id"]

        for accomodation in res.json()["accomodations"]["results"]:
            _property_id = accomodation["property_info"]["id"]
            property_db = Property.objects.select_related(
                "address__city").filter(pk=_property_id).first()
            assert property_db.address.city_id == _city_id

            self.check_room_type(search_request["params"], accomodation)

        # Check history
        res = self.client.get(f"/api/v1/search/history", headers=self.auth_header)
        assert res.json()[0]["id"] == _search_id

    def test_search(self):
        filters_list = [
            None,
            {"price_min": 0, "price_max": 5000},
            {"amenities": ["tv"]},
            {"room_type_categories": ["Room"]},
        ]
        for city_db in City.objects.select_related("region").all():
            for filters in filters_list:
                self.check_city(city_db, filters=filters)

    def test_search_closest(self):
        search_request = SearchRequest(coords=SearchCoords(
            lon=37, lat=55, radius=0  # seek closest
        )).model_dump()
        res = self.client.post(f"/api/v1/search?size=10", data=search_request,
            content_type="application/json", headers=self.auth_header)
        _distances = [x["room_type_info"]["distance"] for x in res.json()["accomodations"]["results"]]
        assert _distances == sorted(_distances)
