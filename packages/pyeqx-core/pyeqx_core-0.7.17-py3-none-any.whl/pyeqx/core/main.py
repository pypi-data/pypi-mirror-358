from datetime import datetime, timezone
from io import TextIOWrapper
import json
import logging
import os
from typing import Optional, TextIO

from pyeqx.core import Configuration, Operation, configuration_from_dict
from pyeqx.core.common import gen_name


def initialize_logging(
    name: str,
    prefix: str,
    stdout: TextIO,
    stdout_wrapper: TextIOWrapper,
    log_level=logging.INFO,
) -> logging.Logger:
    logger = logging.getLogger(name)

    # create formatter
    log_formatter = logging.Formatter(
        f"%(asctime)s %(levelname)s [{prefix}] %(message)s"
    )

    default_handler = logging.StreamHandler(stdout)
    default_handler.setLevel(log_level)
    default_handler.setFormatter(log_formatter)

    # create console handler and set level to debug
    console_handler = logging.StreamHandler(stdout_wrapper)
    console_handler.setLevel(log_level)

    # add console formatter to handlers
    console_handler.setFormatter(log_formatter)

    # add handlers to logger
    logger.addHandler(default_handler)
    logger.addHandler(console_handler)

    # set log level for all handlers to debug
    logger.setLevel(log_level)

    return logger


def initialize_configuration(
    config: dict,
    working_dir: str = ".",
    file_name: str = "config",
    file_path: Optional[str] = None,
):
    env = os.environ.get("ENVIRONMENT", "dev")

    if file_path is None:
        config_path = f"{working_dir}/{file_name}.{env}.json"
    else:
        config_path = f"{working_dir}/{file_path}"

    if not config:
        with open(config_path, "r", encoding="utf-8") as f:
            config = json.load(f)

    return configuration_from_dict(config)


def initialize_operation(
    name: str, config: Configuration, logger: logging.Logger
) -> Operation:
    current_datetime = datetime.now()
    current_timestamp = int(int(datetime.now(timezone.utc).timestamp() * 1000))
    execute_timestamp = current_datetime.strftime("%Y-%m-%d_%H%M%S")

    app_name_prefix = config.app.name

    app_name = gen_name(app_name_prefix, name + "_", execute_timestamp)

    operation = Operation(name=app_name, config=config, logger=logger)

    logger.debug(f"current datetime: {current_datetime}")
    logger.debug(f"current timestamp: {current_timestamp}")

    operation.print_debug_vars()

    return operation
