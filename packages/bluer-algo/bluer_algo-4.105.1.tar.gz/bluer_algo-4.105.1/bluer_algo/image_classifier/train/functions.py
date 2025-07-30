from blueness import module

from bluer_algo import NAME
from bluer_algo.logger import logger


NAME = module.name(__file__, NAME)


def train(
    dataset_object_name: str,
    model_object_name: str,
) -> bool:
    logger.info(
        "{}.train: {} -> {}".format(
            NAME,
            dataset_object_name,
            model_object_name,
        )
    )

    logger.info("🪄")

    return True
