from enum import StrEnum

#from django.utils.translation import gettext_lazy as _
_ = str
from contrib.utils.dict import flatten_nested_dict


class ApiErrors(StrEnum):
    # Common
    TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    # Auth
    BAD_CREDENTIALS = "BAD_CREDENTIALS"
    EMAIL_DOESN_T_EXIST = "EMAIL_DOESN_T_EXIST"
    NO_USER_REGISTERED_WITH_THIS_EMAIL = "NO_USER_REGISTERED_WITH_THIS_EMAIL"
    USER_TYPE_NOT_SUPPORTED = "USER_TYPE_NOT_SUPPORTED"
    CODE_DOESN_T_EXIST = "CODE_DOESN_T_EXIST"
    CODES_DON_T_MATCH = "CODES_DON_T_MATCH"
    WRONG_CODE = "WRONG_CODE"
    NO_ATTEMPTS_LEFT = "NO_ATTEMPTS_LEFT"
    EMAIL_ALREADY_TAKEN = "EMAIL_ALREADY_TAKEN"
    PHONE_ALREADY_TAKEN = "PHONE_ALREADY_TAKEN"
    CANNOT_SEND_EMAIL = "CANNOT_SEND_EMAIL"
    CANNOT_SEND_SMS = "CANNOT_SEND_SMS"

    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    # Locations
    CITY_NOT_FOUND = "CITY_NOT_FOUND"

AE = ApiErrors


API_ERRORS = {
    "common": {
        AE.TOO_MANY_REQUESTS: _("Too many requests"),
        AE.VALIDATION_ERROR: _("Validation error"),
    },
    "auth": {
        AE.BAD_CREDENTIALS: _("Bad credentials"),
        AE.EMAIL_DOESN_T_EXIST: _("Email doesn't exist"),
        AE.NO_USER_REGISTERED_WITH_THIS_EMAIL: _("No user registered with this email"),
        AE.USER_TYPE_NOT_SUPPORTED: _("User type not supported yet"),
        AE.CODE_DOESN_T_EXIST: _("Code doesn't exist"),
        AE.CODES_DON_T_MATCH: _("Codes don't match"),
        AE.WRONG_CODE: _("Wrong code"),
        AE.NO_ATTEMPTS_LEFT: _("No attepmts left"),
        AE.EMAIL_ALREADY_TAKEN: _("Email already taken"),
        AE.PHONE_ALREADY_TAKEN: _("Phone already taken"),
        AE.CANNOT_SEND_EMAIL: _("Cannot send email"),
        AE.CANNOT_SEND_SMS:  _("Cannot send SMS"),
        AE.SERVICE_UNAVAILABLE: _("Service unavailable"),
    },
    "locations": {
        AE.CITY_NOT_FOUND: _("City not found"),
    }
}

API_ERRORS_FLAT = flatten_nested_dict(API_ERRORS)
