from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class FilterSet:
    data: list[BaseModel]
    filters: BaseModel

    def get_filters_list(self):
        _filters_dict = self.filters.model_dump(exclude_unset=True)
        return [
            (func, v)
            for k, v in _filters_dict.items()
            if all((v, func := getattr(self, k, None)))
        ]

    def apply_filters(self):
        _filters_list = self.get_filters_list()
        return [x for x in self.data if all((
            func(x, v) for func, v in _filters_list))]

    def __call__(self):
        return self.apply_filters()
