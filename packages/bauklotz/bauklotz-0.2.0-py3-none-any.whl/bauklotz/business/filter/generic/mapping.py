from collections.abc import Callable
from typing import Iterable, Self

from bauklotz.business.filter import FilterConfig, Filter
from bauklotz.reporting.item import Item
from bauklotz.reporting.types import JSONType


def _identity[T](item: T) -> T:
    return item


class ItemMapper[I: Item, O: Item]:
    def __init__(self, mapper: Callable[[I], O]):
        self.mapper = mapper

    def __call__(self, item: I) -> O:
        return self.mapper(item)


class MappingConfig[I: Item, O: Item](FilterConfig):
    mapper: ItemMapper[I, O] = ItemMapper(_identity)

    @classmethod
    def deserialize(cls, data: JSONType) -> Self:
        pass



class MappingFilter[I: Item, O: Item, C: MappingConfig](Filter[I, O, MappingConfig[I, O]]):
    def __init__(self, name: str, config: MappingConfig[I, O]):
        super().__init__(name, config)

    def process(self, item: I) -> Iterable[O]:
        yield self.config.mapper(item)

