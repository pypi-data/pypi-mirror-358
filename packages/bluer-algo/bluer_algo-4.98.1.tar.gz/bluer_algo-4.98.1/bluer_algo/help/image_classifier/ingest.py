from typing import List

from bluer_options.terminal import show_usage, xtra

from bluer_algo.image_classifier.ingest import sources as ingest_sources


def help_ingest(
    tokens: List[str],
    mono: bool,
) -> str:
    options = "".join(
        [
            "clone,count=<100>,source={}".format("|".join(ingest_sources)),
            xtra(",upload", mono=mono),
        ]
    )

    args = [
        "[--class_count -1]",
        "[--test_ratio 0.1]",
        "[--train_ratio 0.8]",
    ]

    return show_usage(
        [
            "@image_classifier",
            "ingest",
            f"[{options}]",
            "[-|<object-name>]",
        ]
        + args,
        "ingest for image classifier.",
        mono=mono,
    )


help_functions = {
    "ingest": help_ingest,
}
