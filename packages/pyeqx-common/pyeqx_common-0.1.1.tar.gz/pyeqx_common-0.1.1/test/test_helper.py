import json
from unittest import TestCase
from unittest.mock import patch, mock_open, MagicMock
import datetime
import logging
from pyeqx.common.helper import (
    get_current_datetime_now,
    open_file,
    open_file_as_json,
    open_file_as_text,
    get_directory_name,
    get_logger_with_stdout_handler,
)


class HelperTestCase(TestCase):
    def test_get_current_datetime_now_should_success(self):
        # act
        dt = get_current_datetime_now()

        # assert
        self.assertIsInstance(dt, datetime.datetime)
        self.assertEqual(dt.tzinfo, datetime.timezone.utc)

    def test_get_current_datetime_now_with_timezone_should_success(self):
        # arrange
        custom_tz = datetime.timezone(datetime.timedelta(hours=2))

        # act
        result = get_current_datetime_now(custom_tz)

        # assert
        self.assertIsInstance(result, datetime.datetime)
        self.assertEqual(result.tzinfo, custom_tz)

    @patch("builtins.open", new_callable=mock_open, read_data="test data")
    def test_open_file_should_success(self, mock_open: MagicMock):
        # act
        result = open_file("dummy/path.txt")

        # assert
        mock_open.assert_called_once_with(
            file="dummy/path.txt", mode="r", encoding="utf-8"
        )
        self.assertEqual(result.read(), "test data")

    def test_get_directory_name_should_return_directory_name(self):
        # arrange
        path = "path/to/file.txt"

        with patch("os.path.realpath", return_value=path):
            # act
            result = get_directory_name(path)

            # assert
            self.assertEqual(result, "path/to")

    def test_get_logger_with_stdout_handler_should_return_logger(self):
        # act
        logger = get_logger_with_stdout_handler("test_logger", format="%(message)s")

        # assert
        self.assertIsInstance(logger, logging.Logger)
        self.assertEqual(logger.name, "test_logger")
        self.assertEqual(logger.level, logging.INFO)
        self.assertEqual(len(logger.handlers), 1)
        self.assertIsInstance(logger.handlers[0], logging.StreamHandler)
        self.assertEqual(logger.handlers[0].name, "stdout_handler")
        self.assertEqual(logger.handlers[0].level, logging.INFO)
        self.assertIsInstance(logger.handlers[0].formatter, logging.Formatter)
