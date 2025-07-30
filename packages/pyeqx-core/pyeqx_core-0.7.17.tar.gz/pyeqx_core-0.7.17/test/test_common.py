import json
import logging
from unittest import TestCase
from unittest.mock import patch

from pyeqx.common.result import FunctionExecuteResult
from pyeqx.core import (
    initialize_configuration,
    initialize_logging,
    initialize_operation,
)
from pyeqx.core.configuration import Configuration
from pyeqx.core.enums.data_type import DataType
from pyeqx.core.models.app_data import AppData
from pyeqx.core.models.storage.data import Data
from pyeqx.core.models.storage.properties.s3_data_properties import S3DataProperties
from pyeqx.core.operation import Operation


class TestCommon(TestCase):
    def test_initialize_logging_should_return_logger(self):
        logger = initialize_logging(
            name="test", prefix="test", stdout=None, stdout_wrapper=None
        )

        self.assertIsNotNone(logger)
        self.assertEqual(logger.name, "test")
        self.assertEqual(logger.level, logging.INFO)
        self.assertEqual(len(logger.handlers), 2)
        self.assertIsInstance(logger.handlers[0], logging.StreamHandler)
        self.assertIsInstance(logger.handlers[1], logging.StreamHandler)
        self.assertEqual(logger.handlers[0].level, logging.INFO)
        self.assertEqual(logger.handlers[1].level, logging.INFO)
        self.assertEqual(
            logger.handlers[0].formatter._fmt,
            "%(asctime)s %(levelname)s [test] %(message)s",
        )
        self.assertEqual(
            logger.handlers[1].formatter._fmt,
            "%(asctime)s %(levelname)s [test] %(message)s",
        )

    def test_initialize_configuration_with_config_dict_should_return_configuiration_if_success(
        self,
    ):
        with open("./test/config.json", "r") as f:
            raw_config = json.load(f)

        config = initialize_configuration(config=raw_config)

        self.__assert_configuration(config=config)

    def test_initialize_configuration_with_file_path_should_return_configuration_if_success(
        self,
    ):
        config = initialize_configuration(config={}, file_path="test/config.json")

        self.__assert_configuration(config=config)

    def test_initialize_operation_should_return_operation_if_success(
        self,
    ):
        with open("./test/config.json", "r") as f:
            raw_config = json.load(f)

        logger = initialize_logging(
            name="test", prefix="test", stdout=None, stdout_wrapper=None
        )
        config = initialize_configuration(config=raw_config)

        with (
            patch("socket.gethostname", return_value="testhost"),
            patch("socket.gethostbyname", return_value="127.0.0.1"),
        ):

            operation = initialize_operation(name="test", config=config, logger=logger)

            self.assertIsNotNone(operation)
            self.assertIsInstance(operation, Operation)

    def test_function_execute_result_should_return_object_if_success(self):
        result = FunctionExecuteResult(data=None)

        self.assertIsNotNone(result)
        self.assertIsInstance(result, FunctionExecuteResult)
        self.assertIsNone(result.data)
        self.assertEqual(result.is_success, True)

    def test_function_execute_result_with_error_should_return_error_result_object(self):
        result = FunctionExecuteResult(error=Exception("test error"))

        self.assertIsNotNone(result)
        self.assertIsInstance(result, FunctionExecuteResult)
        self.assertEqual(result.is_success, False)
        self.assertIsInstance(result.error, Exception)
        self.assertEqual(str(result.error), "test error")

    def __assert_configuration(self, config: Configuration):
        self.assertIsNotNone(config)
        self.assertIsInstance(config, Configuration)
        self.assertEqual(config.engine.storage, "system")

        app_config = config.app
        self.assertIsNotNone(app_config)
        self.assertEqual(app_config.name, "app_%s%s")

        data_config = config.app.datas.get_data("system", AppData)

        self.assertIsInstance(data_config, AppData)
        storage_config = config.app.storages.get("system")
        self.assertIsInstance(storage_config, Data)

        storage_props = storage_config.get_properties(S3DataProperties)
        self.assertIsInstance(storage_props, S3DataProperties)
        self.assertEqual(storage_config.type, DataType.S3)
        self.assertEqual(storage_props.endpoint, "http://localhost:9000")
        self.assertEqual(storage_props.access_key, "user")
        self.assertEqual(storage_props.secret_key, "password123")
        self.assertEqual(storage_props.bucket_name, "datadd/data")
