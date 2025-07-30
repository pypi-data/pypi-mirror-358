from typing import List

from bluer_options.terminal import show_usage, xtra

from bluer_algo import ALIAS


def help_train(
    tokens: List[str],
    mono: bool,
) -> str:
    options = "".join(
        [
            xtra("~download,upload", mono=mono),
        ]
    )
    args = []

    return show_usage(
        [
            "@image_classifier",
            "train",
            f"[{options}]",
            "[.|<dataset-object-name>]",
            "[-|<model-object-name>]",
        ]
        + args,
        "<dataset-object-name> -train-> <model-object-name>.",
        mono=mono,
    )


help_functions = {
    "train": help_train,
}
