from django.contrib.gis.geos import Point

from ninja import Schema, ModelSchema
from pydantic import field_validator, confloat

from apps.shared.models import Region, City, Address
from contrib.utils.gis import coords_to_list


class CityBrief(ModelSchema):
    class Meta:
        model = City
        exclude = ["tl_id"]


class RegionBrief(ModelSchema):
    class Meta:
        model = Region
        exclude = ["tl_id"]


class CityInfo(CityBrief):
    region: RegionBrief
    count: int | None = None


class RegionInfo(RegionBrief):
    cities: list[CityBrief]


class Coords(Schema):
    lat: confloat(ge=-90, le=90)
    lon: confloat(ge=-180, le=180)


class AddressInfo(Schema):
    address_line: str
    coords: Coords

    @field_validator("coords", mode="before")
    def coords_to_dict(cls, value):
        try:
            if type(value) == Point:
                coords = coords_to_list(value)
                assert len(coords) == 2
                return dict(zip(("lat", "lon"), coords))
            else:
                return value
        except:
            return {"lat": 0, "lon": 0}
