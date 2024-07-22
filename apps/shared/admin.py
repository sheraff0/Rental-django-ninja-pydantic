from django.contrib import admin

from .models import (
    AmenityCategory, Amenity, 
    MealPlan,
    RoomTypeCategory,
    Address,
    PropertyOwnerContacts
)


class AmenityInline(admin.TabularInline):
    model = Amenity
    extra = 0


@admin.register(AmenityCategory)
class AmenityCategoryAdmin(admin.ModelAdmin):
    inlines = [AmenityInline]


@admin.register(MealPlan)
class MealPlanAdmin(admin.ModelAdmin):
    ...


@admin.register(RoomTypeCategory)
class RoomTypeCategoryAdmin(admin.ModelAdmin):
    ...


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    ...


@admin.register(PropertyOwnerContacts)
class PropertyOwnerContactsAdmin(admin.ModelAdmin):
    list_display = ("owner", "email", "phone")
