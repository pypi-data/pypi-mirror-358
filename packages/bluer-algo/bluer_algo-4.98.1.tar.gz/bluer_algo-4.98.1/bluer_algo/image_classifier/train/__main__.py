import argparse

from blueness import module
from blueness.argparse.generic import sys_exit

from bluer_algo import NAME
from bluer_algo.image_classifier.train.functions import train
from bluer_algo.logger import logger

NAME = module.name(__file__, NAME)

parser = argparse.ArgumentParser(NAME)
parser.add_argument(
    "task",
    type=str,
    help="train",
)
parser.add_argument(
    "--dataset_object_name",
    type=str,
)
parser.add_argument(
    "--model_object_name",
    type=str,
)
args = parser.parse_args()

success = False
if args.task == "train":
    success = train(
        dataset_object_name=args.dataset_object_name,
        model_object_name=args.model_object_name,
    )
else:
    success = None

sys_exit(logger, NAME, args.task, success)
