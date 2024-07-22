from enum import StrEnum


class StrEnumWithChoices(StrEnum):
    @classmethod
    def choices(cls):
        return [(x.value, x.name) for x in cls]
