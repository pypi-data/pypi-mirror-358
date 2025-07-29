from bluer_options.env import load_config, load_env, get_env

load_config(__name__)


BLUER_ALGO_CONFIG = get_env("BLUER_ALGO_CONFIG")
