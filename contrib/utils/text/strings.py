import re


def param_to_bool(param):
    return {
        "true": True,
        "1": True,
        "false": False,
        "0": False
    }.get(param, False)


def clean_phone(phone: str):
    try:
        # Extract digits
        res = re.sub("\D", "", phone)
        # Replace leading 8 with 7
        res = re.sub("^8", "7", res)
        return res
    except Exception:
        ...
