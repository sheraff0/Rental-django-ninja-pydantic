from django.contrib import admin
from apps.properties.models import (
    Property, PropertyImage,
    RoomType, RoomTypeImage,
    RatePlan, Service,
)


class RoomTypeImageInline(admin.StackedInline):
    model = RoomTypeImage
    extra = 0
    fields = ["image", "image_tag"]
    readonly_fields = ["image_tag"]


class RoomTypeInline(admin.StackedInline):
    model = RoomType
    extra = 0
    inlines = [RoomTypeImageInline]
    show_change_link = True


class PropertyImageInline(admin.StackedInline):
    model = PropertyImage
    extra = 0
    fields = ["image", "image_tag"]
    readonly_fields = ["image_tag"]


class RatePlanInline(admin.StackedInline):
    model = RatePlan
    extra = 0


class ServiceInline(admin.StackedInline):
    model = Service
    extra = 0


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    inlines = [RoomTypeInline, PropertyImageInline, RatePlanInline, ServiceInline]
    ordering = ("name", )
    list_display = ("name", "address")
    search_fields = ("name", "address__address_line")

    def get_queryset(self, request):
        return self.model.objects.select_related("address").all()


@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    inlines = [RoomTypeImageInline]
    list_display = ["property_name", "name"]
    search_fields = ["property_obj__name", "name"]
    ordering = ["property_obj__name", "sort_order"]
