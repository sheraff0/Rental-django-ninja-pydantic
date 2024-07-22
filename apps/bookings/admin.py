from django.contrib import admin
from .models import Booking, BookingDailyRate, BookingHistory, Payment


class BookingDailyRateInline(admin.StackedInline):
    model = BookingDailyRate
    extra = 0


class BookingHistoryInline(admin.StackedInline):
    model = BookingHistory
    fields = ["status", "create_time"]
    readonly_fields = ["create_time"]
    extra = 0


class PaymentInline(admin.StackedInline):
    model = Payment
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    inlines = [BookingDailyRateInline, BookingHistoryInline, PaymentInline]
    list_display = ["user", "property_obj", "guests", "status", "create_time"]
    ordering = ["-create_time"]
    list_filter = ["status"]

    def get_queryset(self, request):
        return self.model.objects.select_related("user", "property_obj")