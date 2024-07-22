from datetime import date, timedelta

from ninja import Schema, Field
from pydantic import model_validator, conint


def get_days(obj) -> int:
    try:
        return max(1, (obj.departure_date - obj.arrival_date).days)
    except: ...


class SearchParams(Schema):
    arrival_date: date = Field(default_factory=date.today)
    departure_date: date = Field(default_factory=lambda: date.today() + timedelta(days=1))
    adults: conint(ge=1, le=100) = Field(default=1)
    children: list[conint(ge=0, le=17)] = Field(default_factory=list)

    @model_validator(mode="after")
    def dates_check(cls, obj):
        assert obj.arrival_date >= date.today() - timedelta(days=1), "Arrival should not be in the past"
        assert obj.arrival_date < obj.departure_date, "Arrival should be before departure"
        return obj

    @property
    def days(self) -> int:
        return get_days(self)
