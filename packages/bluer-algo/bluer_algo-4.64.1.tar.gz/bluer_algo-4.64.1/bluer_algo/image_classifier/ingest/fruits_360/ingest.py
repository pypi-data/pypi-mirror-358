from blueness import module

from bluer_algo import NAME
from bluer_algo.image_classifier.ingest.fruits_360.types import get_types
from bluer_algo.logger import logger


NAME = module.name(__file__, NAME)


def ingest(
    object_name: str,
    count: int = 100,
    type_count: int = -1,
) -> bool:
    logger.info(
        "{}.ingest -{}{}> {}".format(
            NAME,
            "" if type_count == -1 else f"{type_count}-type(s)-",
            f"{count}-record(s)-",
            object_name,
        )
    )

    fruit_types = get_types(
        type_count=count if type_count == -1 else type_count,
    )
    if type_count == -1:
        type_count = len(fruit_types)

    return True
