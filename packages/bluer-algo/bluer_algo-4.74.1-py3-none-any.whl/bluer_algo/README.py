import os

from bluer_objects import file, README

from bluer_algo import NAME, VERSION, ICON, REPO_NAME


items = README.Items(
    [
        {
            "name": "image classifier",
            "marquee": "https://github.com/kamangir/assets/raw/main/blue-plugin/marquee.png?raw=true",
            "description": "an image classifier.",
            "url": "./bluer_algo/docs/image-classifier.md",
        }
    ]
)


def build():
    return all(
        README.build(
            items=readme.get("items", []),
            path=os.path.join(file.path(__file__), readme["path"]),
            ICON=ICON,
            NAME=NAME,
            VERSION=VERSION,
            REPO_NAME=REPO_NAME,
        )
        for readme in [
            {"items": items, "path": ".."},
            {"path": "docs/image-classifier.md"},
            {"path": "docs/image-classifier-ingest.md"},
        ]
    )
