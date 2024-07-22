from django.contrib.gis.geos import Point

from external.travelline.schemas.content import Address as AddressInfo
from apps.shared.models import Region, City, Address
from .import_data import ImportData


class AddressImport(ImportData):
    source_model = AddressInfo

    async def import_object(self, data: AddressInfo | None):
        if not data:
            return

        _region, _ = await Region.objects.aupdate_or_create(tl_id=data.regionId, defaults=dict(
            name=data.region) if data.region else {})
        _city, _ = await City.objects.aupdate_or_create(tl_id=data.cityId, defaults=dict(
            region_id=_region.id, name=data.cityName))
        _address, _  = await Address.objects.aupdate_or_create(
            region=_region, city=_city,
            address_line=data.addressLine,
            defaults=dict(
                postal_code=data.postalCode,
                coords=Point(x=data.longitude, y=data.latitude, srid=4326)  # lon, lat - this order
            )
        )
        return _address
