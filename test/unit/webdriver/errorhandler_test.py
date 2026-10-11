#!/usr/bin/env python

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json

import pytest
import selenium.common.exceptions as sel_exceptions

import appium.common.exceptions as appium_exceptions
from appium.webdriver.errorhandler import MobileErrorHandler, format_stacktrace


class TestFormatStacktrace:
    def test_format_stacktrace_empty(self):
        assert format_stacktrace(None) == []
        assert format_stacktrace('') == []
        assert format_stacktrace([]) == []

    def test_format_stacktrace_str(self):
        stack = 'line1\nline2'
        assert format_stacktrace(stack) == ['line1', 'line2']

    def test_format_stacktrace_sequence(self):
        frames = [
            'not a dict frame',
            {
                'lineNumber': 10,
                'fileName': 'file.py',
                'methodName': 'my_method',
                'className': 'MyClass',
            },
            {
                'fileName': 'other.py',
            },
        ]
        formatted = format_stacktrace(frames)
        assert formatted == [
            '    at MyClass.my_method (file.py:10)',
            '    at <anonymous> (other.py)',
        ]

    def test_format_stacktrace_type_error(self):
        class BadIterable:
            def __iter__(self):
                raise TypeError('Iteration failed')

        assert format_stacktrace(BadIterable()) == []


class TestMobileErrorHandler:
    def setup_method(self):
        self.handler = MobileErrorHandler()

    def test_check_response_payload_dict(self):
        response = {
            'value': {
                'value': {
                    'error': 'no such element',
                    'message': 'Element not found',
                }
            }
        }
        with pytest.raises(sel_exceptions.NoSuchElementException) as exc_info:
            self.handler.check_response(response)
        assert 'Element not found' in str(exc_info.value)

    def test_check_response_payload_json_str(self):
        payload_data = {
            'value': {
                'error': 'no such element',
                'message': 'Element not found in json',
            }
        }
        response = {'value': json.dumps(payload_data)}
        with pytest.raises(sel_exceptions.NoSuchElementException):
            self.handler.check_response(response)

    def test_check_response_json_decode_error(self):
        response = {'value': 'invalid json {'}
        # Should return silently without exception
        self.handler.check_response(response)

    def test_check_response_type_error(self):
        response = {'value': 12345}
        # json.loads(12345) raises TypeError, caught by check_response
        self.handler.check_response(response)

    def test_check_response_non_dict_parsed_json(self):
        response = {'value': json.dumps([1, 2, 3])}
        # json.loads parses to list, not dict
        self.handler.check_response(response)

    def test_check_response_inner_value_not_dict(self):
        response = {'value': {'value': 'not a dict'}}
        self.handler.check_response(response)

        response = {'value': {}}
        self.handler.check_response(response)

    def test_check_response_no_error_key(self):
        response = {'value': {'value': {'message': 'success'}}}
        self.handler.check_response(response)

    def test_check_response_no_such_context_exception(self):
        response = {
            'value': {
                'value': {
                    'error': 'unknown error',
                    'message': 'No such context found.',
                }
            }
        }
        with pytest.raises(appium_exceptions.NoSuchContextException):
            self.handler.check_response(response)

    def test_check_response_invalid_switch_to_target_exception(self):
        response = {
            'value': {
                'value': {
                    'error': 'unknown error',
                    'message': 'That command could not be executed in the current context.',
                }
            }
        }
        with pytest.raises(appium_exceptions.InvalidSwitchToTargetException):
            self.handler.check_response(response)

    def test_check_response_unexpected_alert_present_exception(self):
        response = {
            'value': {
                'value': {
                    'error': 'unexpected alert open',
                    'message': 'Alert shown',
                    'data': 'Alert Text',
                }
            }
        }
        with pytest.raises(sel_exceptions.UnexpectedAlertPresentException) as exc_info:
            self.handler.check_response(response)
        assert exc_info.value.alert_text == 'Alert Text'
