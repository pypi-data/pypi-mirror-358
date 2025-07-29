from blueness import module

from bluer_algo import NAME
from bluer_algo.logger import logger


NAME = module.name(__file__, NAME)


def ingest(object_name: str) -> bool:
    logger.info(f"{NAME}.ingest -> {object_name}")
    return True
