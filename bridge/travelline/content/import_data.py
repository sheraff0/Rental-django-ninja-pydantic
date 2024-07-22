import abc

from pydantic import BaseModel


class AbstractModel(abc.ABC):
    @abc.abstractmethod
    def __init__(self, *args, **kwargs):
        ...


class ImportData(abc.ABC):
    source_model = AbstractModel
    db_model = None

    def __init__(self, data, validated=False, with_images=True):
        self.data = self.source = data
        self.is_list = issubclass(type(self.data), list)
        if not validated:
            self.validate()
        self.with_images = with_images

    def validate(self):
        if self.is_list:
            self.source = [self.source_model(**x) for x in self.data]
        else:
            self.source = self.source_model(**self.data)

    async def import_object(self, data):
        assert self.db_model is not None, \
            "You should (re-)define at least one of:\n- `db_model` attr,\n- `import_object` method"
        _obj, _ = await self.db_model.objects.aget_or_create(**data.model_dump())
        return _obj

    async def __call__(self):
        if not self.source:
            return
        if self.is_list:
            return [await self.import_object(x) for x in self.source]
        else:
            return await self.import_object(self.source)
