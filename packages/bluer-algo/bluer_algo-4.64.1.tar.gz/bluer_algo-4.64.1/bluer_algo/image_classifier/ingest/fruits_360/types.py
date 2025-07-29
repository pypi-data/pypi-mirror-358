import os
from typing import Dict
import random

from blueness import module
from bluer_options.logger import log_list
from bluer_objects import path
from bluer_objects.env import abcli_path_git

from bluer_algo import NAME
from bluer_algo.env import BLUER_ALGO_FRUITS_360_REPO_PATH
from bluer_algo.logger import logger


NAME = module.name(__file__, NAME)


def get_types(
    type_count: int = -1,
    shuffle: bool = True,
) -> Dict[str, int]:
    logger.info(
        "{}.get_types{}".format(
            NAME,
            "" if type_count == -1 else f": {type_count} type(s)",
        )
    )

    training_path = os.path.join(BLUER_ALGO_FRUITS_360_REPO_PATH, "Training")
    logger.info(f"reading {training_path} ...")

    list_of_types = [path.name(path_) for path_ in path.list_of(training_path)]

    if shuffle:
        random.shuffle(list_of_types)

    if type_count != -1:
        list_of_types = list_of_types[:type_count]

    list_of_types = sorted(list_of_types)
    log_list(
        logger,
        "found",
        list_of_types,
        "type(s)",
        itemize=False,
    )

    return {
        fruit_type: fruit_index
        for fruit_type, fruit_index in zip(
            list_of_types,
            range(len(list_of_types)),
        )
    }
