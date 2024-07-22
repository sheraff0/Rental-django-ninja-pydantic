import abc
from dataclasses import dataclass
from uuid import UUID

from asgiref.sync import sync_to_async
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from ninja.errors import HttpError

from apps.bookings.models import Booking, BookingStatus, BookingHistory
from contrib.users.models import User


@dataclass
class ProcessBookingManagerBase(abc.ABC):
    id: UUID
    user: User
    lock: bool = True
    status_on_success: BookingStatus = None
    status_on_failure: BookingStatus = None

    def set_booking(self, lock=False):
        self._booking = Booking.objects.select_for_update().filter(
            pk=self.id, user=self.user).first()

        if self.lock and lock:
            assert self._booking, _("Booking not found")
            assert not self._booking.locked, _("Booking is locked for update")
            self._booking.locked = True
            self._booking.save()

    @abc.abstractmethod
    def set(self):
        ...

    def set_all(self, lock=False):
        self.set_booking(lock=lock)
        self.set()

    @abc.abstractmethod
    async def process(self):
        ...

    @abc.abstractmethod
    def save(self):
        ...

    def post_save(self):
        ...

    @sync_to_async
    def on_success(self):
        with transaction.atomic():
            self.set_all()
            self.save()
            self._booking.locked = False
            if self.status_on_success:
                self._booking.status = self.status_on_success
                self.history_record(self.status_on_success)
            self._booking.save()
        self.post_save()

    @sync_to_async
    @transaction.atomic
    def on_failure(self):
        self.set_booking()
        if not self._booking:
            return
        self._booking.locked = False
        if self.status_on_failure:
            self._booking.status = self.status_on_failure
            self.history_record(self.status_on_failure)
        self._booking.save()

    def history_record(self, status: BookingStatus):
        BookingHistory.objects.get_or_create(booking=self._booking, status=status)

    async def __call__(self):
        try:
            await sync_to_async(transaction.atomic(self.set_all))(lock=self.lock)
            await self.process()
            await self.on_success()
        except AssertionError as e:
            await self.on_failure()
            raise HttpError(400, str(e))
        except Exception as e:
            print(e)
            await self.on_failure()
            raise HttpError(400, str(_("Process failed")))
        return self._booking

    @property
    def email(self):
        return self._booking.email or self.user.email
