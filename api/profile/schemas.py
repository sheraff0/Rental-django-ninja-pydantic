from django.contrib.auth import get_user_model

from pydantic import BaseModel, constr

from ninja import ModelSchema

from contrib.common.schemas import Phone


class UserModify(ModelSchema):
    contact_phone: Phone | None = None

    class Meta:
        model = get_user_model()
        fields = ["last_name", "first_name", "middle_name", "birth_date", "contact_phone"]


class UserInfo(ModelSchema):
    phone: Phone | None
    contact_phone: Phone | None

    class Meta:
        model = get_user_model()
        fields = ["id", "email", "is_verified", "phone"] + UserModify.Meta.fields
