import re

from contrib.common.schemas import Phone


def phone_str(phone):
    try:
        return f'+{phone["countryCode"]}{phone["nsn"]}'
    except:
        return "-"


def parse_phone(string):
    _nsn = re.sub(r"\D", "", string)[-10:]
    return Phone(nsn=_nsn)
