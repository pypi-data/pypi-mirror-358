"""
Configure a logger object

Reference: https://github.com/openai/openai-python/blob/main/src/openai/_utils/_logs.py
"""

import logging
import os

logger: logging.Logger = logging.getLogger("reverse_proxy")

def _basic_config() -> None:
    # e.g. [2023-10-05 14:12:26 - openai._base_client:818 - DEBUG] HTTP Request: POST http://127.0.0.1:4010/foo/bar "200 OK"

    # I love the green bold color in logs 😉
    GREEN_BOLD = "\033[1;92m"  # 1 = bold, 92 = light green
    RESET = "\033[0m"
    logging.basicConfig(
        format=f"{GREEN_BOLD}[%(asctime)s - %(name)s:%(lineno)d - %(levelname)s]{RESET} %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

# TODO: I should have also setup logic to filter sensitive logs so we don't leak secrets,
#       but there is not enough time.
def setup_logging() -> None:
    _basic_config()
    env = os.environ.get("OPENAI_LOG", "info").lower()
    levels = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warn": logging.WARNING,
        "warning": logging.WARNING,
        "error": logging.ERROR,
    }
    logger.setLevel(levels.get(env, logging.INFO))
