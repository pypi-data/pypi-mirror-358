from typing import List

from bluer_options.terminal import show_usage


def help_ingest(
    tokens: List[str],
    mono: bool,
) -> str:
    options = "clone"

    return show_usage(
        [
            "@image_classifier",
            "ingest",
            f"[{options}]",
            "[-|<object-name>]",
        ],
        "ingest for image classifier.",
        mono=mono,
    )


help_functions = {
    "ingest": help_ingest,
}
