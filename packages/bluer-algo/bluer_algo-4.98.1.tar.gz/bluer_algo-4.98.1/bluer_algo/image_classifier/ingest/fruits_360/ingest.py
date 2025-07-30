import os
import random
from tqdm import trange, tqdm
import pandas as pd

from blueness import module
from bluer_objects import objects, file
from bluer_objects.metadata import post_to_object
from bluer_objects.logger.image import log_image_grid

from bluer_algo import NAME
from bluer_algo.host import signature
from bluer_algo.image_classifier.ingest.fruits_360.classes import get_classes
from bluer_algo.env import BLUER_ALGO_FRUITS_360_REPO_PATH
from bluer_algo.logger import logger


NAME = module.name(__file__, NAME)


def ingest(
    object_name: str,
    count: int = 100,
    class_count: int = -1,
    test_ratio: float = 0.1,
    train_ratio: float = 0.8,
    verbose: bool = True,
) -> bool:
    eval_ratio = 1 - test_ratio - train_ratio
    if eval_ratio < 0:
        logger.error(f"eval_ratio = {eval_ratio:.2f} < 0")
        return False

    logger.info(
        "{}.ingest -{}{}> {}".format(
            NAME,
            "" if class_count == -1 else f"{class_count}-class(es)-",
            f"{count}-record(s)-",
            object_name,
        )
    )
    ratio_log = "ratios: train={:.2f}, eval={:.2f}, test={:.2f}".format(
        train_ratio,
        eval_ratio,
        test_ratio,
    )
    logger.info(ratio_log)

    dict_of_classes = get_classes(
        class_count=count if class_count == -1 else class_count,
    )
    if class_count == -1:
        class_count = len(dict_of_classes)

    df = pd.DataFrame(
        columns=[
            "filename",
            "class_index",
            "subset",
        ]
    )

    list_of_record_subsets = ["train", "test", "eval"]
    dict_of_subsets = {record_subset: 0 for record_subset in list_of_record_subsets}

    record_count_per_class = int(count / class_count)
    for class_index in trange(class_count):
        record_class = dict_of_classes[class_index]

        logger.info(f"ingesting {record_class}")

        list_of_filenames = file.list_of(
            os.path.join(
                BLUER_ALGO_FRUITS_360_REPO_PATH,
                "Training",
                record_class,
                "*.jpg",
            )
        )
        list_of_filenames = list_of_filenames[:record_count_per_class]

        for source_filename in tqdm(list_of_filenames):
            destination_filename = "{}-{}".format(
                class_index,
                file.name_and_extension(source_filename),
            )

            if not file.copy(
                source_filename,
                objects.path_of(
                    object_name=object_name,
                    filename=destination_filename,
                ),
                log=verbose,
            ):
                return False

            record_subset = random.choices(
                population=list_of_record_subsets,
                weights=[train_ratio, test_ratio, eval_ratio],
                k=1,
            )[0]

            dict_of_subsets[record_subset] += 1

            df.loc[len(df)] = {
                "filename": file.name_and_extension(destination_filename),
                "class_index": class_index,
                "subset": record_subset,
            }

    subset_log = "{}".format(
        ", ".join(
            [
                f"{subset}: {subset_count}"
                for subset, subset_count in dict_of_subsets.items()
            ]
        )
    )
    logger.info(f"subsets: {subset_log}")

    if not file.save_csv(
        objects.path_of(
            object_name=object_name,
            filename="metadata.csv",
        ),
        df,
        log=verbose,
    ):
        return False

    if not post_to_object(
        object_name,
        "dataset",
        {
            "classes": dict_of_classes,
            "class_count": class_count,
            "count": count,
            "ratios": {
                "eval": eval_ratio,
                "test": test_ratio,
                "train": train_ratio,
            },
            "source": "fruits_360",
            "subsets": dict_of_subsets,
        },
    ):
        return False

    df["title"] = df.apply(
        lambda row: "#{}: {} @ {}".format(
            row["class_index"],
            dict_of_classes[row["class_index"]],
            row["subset"],
        ),
        axis=1,
    )

    return log_image_grid(
        df,
        objects.path_of(
            object_name=object_name,
            filename="grid.png",
        ),
        shuffle=True,
        header=[
            ratio_log,
            f"count: {count}",
            subset_log,
            "{} class(es): {}".format(
                len(dict_of_classes),
                ", ".join(dict_of_classes.values()),
            ),
        ],
        footer=signature(),
        log=verbose,
        relative_path=True,
    )
