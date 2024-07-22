from enum import StrEnum
from datetime import time
from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from .common import Resource, Standard, IdInfo, CodeInfo, Currency, MessageResponse


class PropertiesInclude(StrEnum):
    All = "All"


class PropertiesRequest(BaseModel):
    since: str | None = None
    count: int | None = None
    include: PropertiesInclude | None = None


class StayUnitKind(StrEnum):
    NightRate = "NightRate"
    DailyRate = "DailyRate"


class Address(BaseModel):
    postalCode: str
    countryCode: str
    region: str | None = None
    regionId: int
    cityName: str
    cityId: int
    addressLine: str
    latitude: float | None = None
    longitude: float | None = None
    remark: str | None = None  # (Planned) Further information on how to get there


class Phone(BaseModel):
    phoneNumber: str
    techType: str | None = None
    remark: str | None = None


class ContactInfo(BaseModel):
    address: Address
    phones: list[Phone] | None = None
    emails: list[EmailStr | str] | None = None


class Policy(BaseModel):
    checkInTime: time
    checkOutTime: time


class TimeZoneType(BaseModel):
    id: str


class RatePlan(IdInfo):
    name: str
    description: str | None = None
    currency: Currency
    isStayWithChildrenOnly: bool


class Amenity(Standard):
    ...


class AmenityCategory(BaseModel):
    name: str
    amenities: list[Amenity]


class RoomSize(BaseModel):
    value: int
    unit: str


class RoomCategory(Standard):
    ...


class Occupancy(BaseModel):
    adultBed: int  # Guests with main occupancy
    extraBed: int  # Extra beds in the room
    childWithoutBed: int  # Child accommodation without bed


class RoomType(IdInfo):
    name: str
    description: str
    amenities: list[Amenity]
    images: list[Resource]
    size: RoomSize
    categoryCode: str  # RoomCategory.code
    categoryName: str  # RoomCategory.name
    address: Address | None = None
    occupancy: Occupancy
    position: int  # Order in output list


class BookingPlacementKind(StrEnum):
    # Types of accommodations:
    Adult = "Adult"  # adult with main occupancy
    ExtraAdult = "ExtraAdult"  # adult on extra bed
    Child = "Child"  # child with main occupancy
    ExtraChild = "ExtraChild"  # child on extra bed
    ChildBandWithoutBed = "ChildBandWithoutBed"  # child without bed


class Placement(CodeInfo):
    count: int
    kind: BookingPlacementKind
    minAge: int | None = None  # Minimum age in the age group, for child accomodation
    maxAge: int | None = None  # Maximum age in the age group, for child accomodation


class DetailedRoomType(IdInfo):
    placements: list[Placement]


class MealPlan(Standard):
    ...


class ServiceKind(StrEnum):
    COMMON = "Common"
    MEAL = "Meal"


class Service(IdInfo):
    name: str
    description: str | None = None
    kind: ServiceKind
    mealPlanCode: str | None = None
    mealPlanName: str | None = None


class PropertyInfo(IdInfo):
    name: str
    currency: Currency | None = None
    description: str
    images: list[Resource]
    stars: int = None  # Star rating of the property
    stayUnitKind: StayUnitKind  # Type of accommodation unit ‘nights’ or ‘days’
    contactInfo: ContactInfo
    policy: Policy
    timeZone: TimeZoneType
    ratePlans: list[RatePlan]
    roomTypes: list[RoomType]
    services: list[Service]


class PropertiesResponse(BaseModel):
    next: str | None = None
    properties: list[PropertyInfo] | None = None
    errors: list[MessageResponse] | None = None


class PropertiesBriefResponse(BaseModel):
    next: str | None = None
    properties: list[IdInfo] | None = None
    errors: list[MessageResponse] | None = None
