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
    def test_format_stacktrace_none_or_empty(self):
        assert format_stacktrace(None) == []
        assert format_stacktrace('') == []
        assert format_stacktrace([]) == []

    def test_format_stacktrace_string(self):
        stacktrace_str = 'line1\nline2\nline3'
        assert format_stacktrace(stacktrace_str) == ['line1', 'line2', 'line3']

    def test_format_stacktrace_sequence_dicts(self):
        stacktrace_seq = [
            {
                'lineNumber': 42,
                'fileName': 'test.js',
                'methodName': 'myMethod',
                'className': 'MyClass',
            },
            {
                'fileName': 'test2.js',
                'methodName': 'topLevelFunc',
            },
            'not_a_dict',
        ]
        expected = [
            '    at MyClass.myMethod (test.js:42)',
            '    at topLevelFunc (test2.js)',
        ]
        assert format_stacktrace(stacktrace_seq) == expected

    def test_format_stacktrace_type_error_exception(self):
        class NonIterable:
            def __iter__(self):
                raise TypeError('Not iterable')

        assert format_stacktrace(NonIterable()) == []


class TestMobileErrorHandler:
    def setup_method(self):
        self.handler = MobileErrorHandler()

    def test_check_response_valid_no_error(self):
        # Empty response or response without error should return None without raising
        self.handler.check_response({})
        self.handler.check_response({'value': ''})
        self.handler.check_response({'value': None})
        self.handler.check_response({'value': {}})
        self.handler.check_response({'value': {'value': {}}})
        self.handler.check_response({'value': {'value': {'error': None}}})

    def test_check_response_invalid_json_str_payload(self):
        # Invalid JSON string in value payload should be caught and return None
        self.handler.check_response({'value': 'invalid json {['})

    def test_check_response_json_decode_error_and_type_error(self):
        # Non-string/non-dict payload types (e.g. integer or list if not handled as dict)
        self.handler.check_response({'value': 12345})

    def test_check_response_json_payload_decodes_to_non_dict(self):
        # Valid JSON string decoding to int or list (not a dict)
        self.handler.check_response({'value': '123'})
        self.handler.check_response({'value': '[1, 2, 3]'})

    def test_check_response_payload_value_is_not_dict(self):
        # Response with dict payload where payload.get('value') is not a dict
        self.handler.check_response({'value': {'value': 'string_value'}})
        self.handler.check_response({'value': '{"value": 123}'})

    def test_check_response_mapped_selenium_error(self):
        # Response triggering a mapped Selenium exception
        response = {
            'value': {
                'value': {
                    'error': 'no such element',
                    'message': 'Element not found',
                    'stacktrace': 'Traceback line 1\nTraceback line 2',
                }
            }
        }
        with pytest.raises(sel_exceptions.NoSuchElementException) as exc_info:
            self.handler.check_response(response)
        assert exc_info.value.msg is not None
        assert 'Element not found' in exc_info.value.msg
        assert exc_info.value.stacktrace == ['Traceback line 1', 'Traceback line 2']

    def test_check_response_json_str_mapped_selenium_error(self):
        # Payload as a JSON string
        payload = json.dumps(
            {
                'value': {
                    'error': 'stale element reference',
                    'message': 'Element is stale',
                }
            }
        )
        with pytest.raises(sel_exceptions.StaleElementReferenceException) as exc_info:
            self.handler.check_response({'value': payload})
        assert exc_info.value.msg is not None
        assert 'Element is stale' in exc_info.value.msg

    def test_check_response_unmapped_error_defaults_to_webdriver_exception(self):
        response = {
            'value': {
                'value': {
                    'error': 'custom_unknown_error_code',
                    'message': 'Something failed',
                }
            }
        }
        with pytest.raises(sel_exceptions.WebDriverException) as exc_info:
            self.handler.check_response(response)
        assert exc_info.value.msg == 'Something failed'

    def test_check_response_no_such_context_exception(self):
        response = {
            'value': {
                'value': {
                    'error': 'unknown error',
                    'message': 'No such context found.',
                }
            }
        }
        with pytest.raises(appium_exceptions.NoSuchContextException) as exc_info:
            self.handler.check_response(response)
        assert exc_info.value.msg == 'No such context found.'

    def test_check_response_invalid_switch_to_target_exception(self):
        response = {
            'value': {
                'value': {
                    'error': 'unknown error',
                    'message': 'That command could not be executed in the current context.',
                }
            }
        }
        with pytest.raises(appium_exceptions.InvalidSwitchToTargetException) as exc_info:
            self.handler.check_response(response)
        assert exc_info.value.msg == 'That command could not be executed in the current context.'

    def test_check_response_unexpected_alert_present_exception(self):
        response = {
            'value': {
                'value': {
                    'error': 'unexpected alert open',
                    'message': 'Alert present',
                    'data': 'Alert text content',
                }
            }
        }
        with pytest.raises(sel_exceptions.UnexpectedAlertPresentException) as exc_info:
            self.handler.check_response(response)
        assert exc_info.value.msg == 'Alert present'
        assert exc_info.value.alert_text == 'Alert text content'
