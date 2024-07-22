from django.db.models import Q

from external.travelline.schemas.content import (
    PropertyInfo,
    RoomType as RoomTypeInfo,
    RatePlan as RatePlanInfo,
    Service as ServiceInfo,
)
from apps.properties.models import Property, RoomType, RatePlan, Service
from apps.shared.models import Amenity, MealPlan, PropertyOwner, PropertyOwnerContacts
from contrib.common.cached import acached
from contrib.utils.text import clean_phone
from .import_data import ImportData
from .address import AddressImport
from .amenity import get_amenity, AMENITIES_TO_FIELD
from .room_category import get_room_type_category
from .images import ImageSetter
from .meal_plan import get_meal_plan


class PropertyImport(ImportData):
    source_model = PropertyInfo

    async def import_object(self, data: PropertyInfo):
        _address = await AddressImport(data.contactInfo.address, validated=True)()
        _owner = await self.get_owner(data)
        _property, _ = await Property.objects.aupdate_or_create(
            tl_id=data.id,
            defaults=dict(
                tl_linked=True,
                name=data.name,
                description=data.description,
                address=_address,
                check_in_time=data.policy.checkInTime,
                check_out_time=data.policy.checkOutTime,
                time_zone=data.timeZone.id,
                stay_unit=data.stayUnitKind,
                owner=_owner,
            )
        )

        # Property images
        if self.with_images:
            await self.write_images(_property, data)

        # Room types
        for sort_order, room_type_data in enumerate(data.roomTypes):
            await self.import_room_type(room_type_data, _property, sort_order)

        # Rate plans
        for rate_plan_data in data.ratePlans:
            await self.import_rate_plan(rate_plan_data, _property)

        # Services
        for service_data in data.services:
            await self.import_service(service_data, _property)

        return _property

    async def import_room_type(self, data: RoomTypeInfo, parent: Property, sort_order: int):
        _address = await AddressImport(data.address, validated=True)()
        _category_id = await get_room_type_category(data.categoryCode)
        _beds = data.occupancy.adultBed + data.occupancy.extraBed
        _room_type, _ = await RoomType.objects.aupdate_or_create(
            tl_id=data.id,
            defaults=dict(
                property_obj=parent,
                category_id=_category_id,
                name=data.name,
                description=data.description,
                address=_address,
                beds=_beds,
                rooms=None,
                non_smoking=None,
                area=data.size.value,
                sort_order=sort_order,
            ),
        )

        # Property images
        if self.with_images:
            await self.write_images(_room_type, data)

        # Room type amenities
        _amenities = []
        for x in data.amenities:
            _code = x.code
            if _kv := AMENITIES_TO_FIELD.get(_code):
                k, v = _kv
                setattr(_room_type, k, v)
            else:
                _amenities.append(await get_amenity(_code))

        await _room_type.amenities.aset(_amenities)
        await _room_type.asave()

    @staticmethod
    async def import_rate_plan(data: RatePlanInfo, parent: Property):
        _rate_plan, _ = await RatePlan.objects.aupdate_or_create(
            tl_id=data.id,
            defaults=dict(
                property_obj=parent,
                name=data.name,
                description=data.description,
                currency=data.currency,
                with_children_only=data.isStayWithChildrenOnly,
            )
        )
        return _rate_plan

    @staticmethod
    async def import_service(data: ServiceInfo, parent: Property):
        _meal_plan_id = await get_meal_plan(data.mealPlanCode)
        _service, _ = await Service.objects.aupdate_or_create(
            tl_id=data.id,
            defaults=dict(
                property_obj=parent,
                name=data.name,
                description=data.description,
                meal_plan_id=_meal_plan_id,
            )
        )
        return _service

    @staticmethod
    async def write_images(parent, data):
        _images = []
        for sort_order, image in enumerate(data.images):
            _image = await ImageSetter(parent, image.url, sort_order)()
            _images.append(_image)
        await parent.images.filter(~Q(id__in=_images)).adelete()

    @acached(ttl=300)
    @staticmethod
    async def get_property_owner_contacts():
        return [
            (x.owner, clean_phone(x.phone), x.email and x.email.lower())
            async for x in PropertyOwnerContacts.objects.all()
        ]

    @classmethod
    async def get_owner(cls, data: PropertyInfo):
        _property_owner_contacts = await cls.get_property_owner_contacts()
        _contact_info = data.contactInfo
        _phones = [clean_phone(x.phoneNumber) for x in _contact_info.phones]
        _email = [x.lower() for x in _contact_info.emails]
        try:
            return next(owner for owner, phone, email in _property_owner_contacts if any((
                phone in _phones,
                email in _email,
            )))
        except Exception:
            ...
