from pydantic import BaseModel


def get_instance_attrs_path(instance, attr):
    try:
        res = instance
        for key in attr.split("."):
            res = getattr(res, key)
        return res
    except: ...


def update_instance(instance, attrs: BaseModel | dict):
    if isinstance(attrs, BaseModel):
        attrs = attrs.model_dump(exclude_unset=True)
    for k, v in attrs.items():
        setattr(instance, k, v)
    return instance
