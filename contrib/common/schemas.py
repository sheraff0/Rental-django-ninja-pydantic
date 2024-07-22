from pydantic import BaseModel, constr


class Phone(BaseModel):
    countryCode: constr(pattern=r"^\d{1,4}$") = "7"
    nsn: constr(pattern=r"^\d{7,12}$")
    isoCode: constr(pattern=r"^[A-Z]{2,4}$") = "RU"
