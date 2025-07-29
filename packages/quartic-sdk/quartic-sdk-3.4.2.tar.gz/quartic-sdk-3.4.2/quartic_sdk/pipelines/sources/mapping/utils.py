import logging
import inspect
from typing import Type

from quartic_sdk.pipelines.sources import mapping
from quartic_sdk.pipelines.sources.mapping.base import MappingProcessor

ALL_PROCESSORS: list[Type[MappingProcessor]] = list(
    filter(
        lambda c: inspect.isclass(c)
        and c != MappingProcessor
        and issubclass(c, MappingProcessor),
        [getattr(mapping, a) for a in dir(mapping)],
    )
)
logging.info(f"Detected mapping processors: {[h.__name__ for h in ALL_PROCESSORS]}")


def get_processor(source: str) -> MappingProcessor:
    for processor_cls in ALL_PROCESSORS:
        if source in processor_cls.get_source_classes():
            return processor_cls()
    raise NotImplementedError(f"No mapping processor for for {source}")
