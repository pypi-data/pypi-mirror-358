import argparse

from blueness import module
from blueness.argparse.generic import sys_exit

from bluer_algo import NAME
from bluer_algo.image_classifier.ingest.fruits_360.ingest import ingest
from bluer_algo.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="ingest",
)
parser.add_argument(
    "--object_name",
    type=str,
)
parser.add_argument(
    "--type_count",
    type=int,
    default=-1,
)
parser.add_argument(
    "--count",
    type=int,
    default=100,
)
args = parser.parse_args()

success = False
if args.task == "ingest":
    success = ingest(
        object_name=args.object_name,
        count=args.count,
        type_count=args.type_count,
    )
else:
    success = None

sys_exit(logger, NAME, args.task, success)
