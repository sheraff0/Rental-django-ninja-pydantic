from enum import StrEnum
from datetime import date
from typing import Any

from pydantic import BaseModel, NaiveDatetime, AwareDatetime
from .common import IdInfo, GuestCount, StayDates, Currency, MessageResponse
from .content import DetailedRoomType


class CommonSearchCriteria(BaseModel):
    arrivalDate: date
    departureDate: date
    adults: int
    childAges: list[int] | None = None


class SpecificAccomodationSearchRequest(CommonSearchCriteria):
    property_id: str


class Tax(BaseModel):
    amount: float
    name: str
    description: str | None = None


class Total(BaseModel):
    priceBeforeTax: float
    taxAmount: float
    taxes: list[Tax]


class CancellationPolicy(BaseModel):
    freeCancellationPossible: bool
    freeCancellationDeadlineLocal: NaiveDatetime | None = None
    freeCancellationDeadlineUtc: AwareDatetime | None = None
    penaltyAmount: float | None = None


class IncludedRoomStayService(IdInfo):
    mealPlanCode: str | None = None


class AvailableRoomStayService(IdInfo):
    price: float
    mealPlanCode: str | None = None


class DetailedRoomStay(BaseModel):
    propertyId: str
    roomType: DetailedRoomType
    ratePlan: IdInfo
    guestCount: GuestCount
    stayDates: StayDates
    availability: int  # Number of accommodations available
    currencyCode: Currency
    total: Total
    cancellationPolicy: CancellationPolicy
    includedServices: list[IncludedRoomStayService] | None = None
    mealPlanCode: str
    checksum: str
    fullPlacementsName: str
    availableServices: list[AvailableRoomStayService] | None = None


class LowestPriceSearchInclude(StrEnum):
    byRoomTypes = "roomTypeShortContent"
    byRatePlans = "ratePlanShortContent"
    byBoth = "roomTypeShortContent|ratePlanShortContent"


class MealType(StrEnum):
    All = "All"  # Meal doesn't matter
    MealOnly = "MealOnly"
    MealPriority = "MealPriority"


class MealsIncluded(BaseModel):
    mealPlanCodes: list[str] | None = None  # from 


class MealPreference(BaseModel):
    mealType: MealType
    mealsIncluded: MealsIncluded | None = None


class PricePreference(BaseModel):
    currencyCode: Currency
    minPrice: float | None = None
    maxPrice: float | None = None


class LowestPriceSearchRequest(CommonSearchCriteria):
    propertyIds: list[str]
    include: LowestPriceSearchInclude | None = None
    mealPreference: MealPreference | None = None
    pricePreference: PricePreference | None = None


class ShortRoomStay(BaseModel):
    propertyId: str
    roomType: DetailedRoomType
    ratePlan: IdInfo
    currencyCode: Currency
    total: Total
    includedServices: list[IncludedRoomStayService] | None = None
    mealPlanCode: str
    fullPlacementsName: str


class SpecificAccomodationSearchResponse(BaseModel):
    roomStays: list[DetailedRoomStay] | None = None
    errors: list[MessageResponse] | None = None


class LowestPriceSearchResponse(BaseModel):
    #roomStays: list[ShortRoomStay] | None = None
    roomStays: list[DetailedRoomStay] | None = None
    errors: list[MessageResponse] | None = None
