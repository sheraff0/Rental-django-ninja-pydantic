import json
from random import choice
from datetime import datetime, timedelta

from asgiref.sync import async_to_sync
from django.test import TestCase

from api.auth.schemas import Phone
from api.bookings.schemas import BookingVerify, BookingCustomizable, BookingRating
from apps.bookings.models import Booking, BookingStatus
from contrib.ninja.auth import authenticate
from contrib.users.models import User
from .mixins import AuthSetupMixin, ContentSetupMixin


class BookingTestCase(ContentSetupMixin, AuthSetupMixin, TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.setup_auth_data()
        cls.setup_content()
        cls.clear_redis_cache()

    @classmethod
    def tearDownClass(cls):
        cls.destroy_content()

    def get_booking_data(self):
        res = self.client.post(f"/api/v1/search", data={},
            content_type="application/json", headers=self.auth_header)
        _accomodation = choice(res.json()["accomodations"]["results"])
        _lowest_price_offer = _accomodation["lowest_price_offer"]
        return BookingVerify(
            search_id=res.json()["search"]["id"],
            property_id=_accomodation["property_info"]["id"],
            room_type_id=_accomodation["room_type_info"]["id"],
            rate_plan_id=_lowest_price_offer["rate_plan_info"]["id"],
            placements=[x["code"] for x in _lowest_price_offer["placements"]],
            checksum=_lowest_price_offer["checksum"],
        ).model_dump()

    def set_contact_data(self):
        user = User.objects.get(pk=self.user.pk)
        user.contact_phone = Phone(countryCode="7", nsn="9999999999", isoCode="RU").model_dump()
        user.first_name = "test"
        user.last_name = "tester"
        user.save()
        async_to_sync(authenticate)(self.token.key, reset_cache=True)

    def verify_booking(self, booking_data):
        return self.client.post(f"/api/v1/bookings/verify", data=booking_data,
            content_type="application/json", headers=self.auth_header)

    def pay_booking(self, booking_id):
        return self.client.post(f"/api/v1/bookings/{booking_id}/pay", headers=self.auth_header)

    def create_booking(self, booking_id):
        return self.client.post(f"/api/v1/bookings/{booking_id}/book", headers=self.auth_header)

    def modify_booking(self, booking_id):
        _comment = "Test comment XYZ"
        _data = BookingCustomizable(comment=_comment).model_dump()
        return self.client.patch(f"/api/v1/bookings/{booking_id}", data=_data,
            content_type="application/json", headers=self.auth_header)

    def cancel_booking(self, booking_id):
        return self.client.post(f"/api/v1/bookings/{booking_id}/cancel", headers=self.auth_header)

    def rate_booking(self, booking_id, rating):
        _data = BookingRating(rating=rating).model_dump()
        return self.client.post(f"/api/v1/bookings/{booking_id}/rate", data=_data,
            content_type="application/json", headers=self.auth_header)

    def test_booking(self):
        _booking_data = self.get_booking_data()
        res = self.verify_booking(_booking_data)
        assert res.status_code == 400
        self.set_contact_data()
        res = self.verify_booking(_booking_data)
        _booking_id = res.json()["id"]
        assert res.status_code == 200
        # History
        res = self.client.get(f"/api/v1/bookings", headers=self.auth_header)
        res.json()["results"][0]["id"] == _booking_id
        # Create before pay
        res = self.create_booking(_booking_id)
        assert res.status_code == 400
        # Pay
        res = self.pay_booking(_booking_id)
        assert res.json()["id"] == _booking_id
        # Create
        res = self.create_booking(_booking_id)
        assert res.json()["status"] == BookingStatus.CONFIRMED
        # Modify
        res = self.modify_booking(_booking_id)
        assert res.json()["id"] == _booking_id
        # Cancel
        res = self.cancel_booking(_booking_id)
        assert res.json()["status"] == BookingStatus.CANCELLED
        # Rate
        _rating = 5
        res = self.rate_booking(_booking_id, _rating)
        assert res.json()["rating"] == _rating
