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
    def test_empty_or_none(self) -> None:
        assert format_stacktrace(None) == []
        assert format_stacktrace('') == []
        assert format_stacktrace([]) == []

    def test_string_stacktrace(self) -> None:
        trace = 'line1\nline2\nline3'
        assert format_stacktrace(trace) == ['line1', 'line2', 'line3']

    def test_sequence_of_frames_full(self) -> None:
        frames = [
            {
                'lineNumber': 42,
                'fileName': 'app.js',
                'methodName': 'onClick',
                'className': 'Button',
            },
            {
                'lineNumber': 100,
                'fileName': 'index.js',
                'methodName': 'main',
                'className': 'App',
            },
        ]
        expected = [
            '    at Button.onClick (app.js:42)',
            '    at App.main (index.js:100)',
        ]
        assert format_stacktrace(frames) == expected

    def test_sequence_of_frames_missing_fields(self) -> None:
        frames = [
            {
                'lineNumber': 10,
            },
            {},
        ]
        expected = [
            '    at <anonymous> (<anonymous>:10)',
            '    at <anonymous> (<anonymous>)',
        ]
        assert format_stacktrace(frames) == expected

    def test_sequence_of_frames_non_dict_elements(self) -> None:
        frames = [
            'invalid_frame',
            123,
            None,
            {
                'methodName': 'doSomething',
            },
        ]
        expected = [
            '    at doSomething (<anonymous>)',
        ]
        assert format_stacktrace(frames) == expected

    def test_type_error_handling(self) -> None:
        class NonIterable:
            def __bool__(self) -> bool:
                return True

            def __iter__(self):
                raise TypeError('Not iterable')

        assert format_stacktrace(NonIterable()) == []


class TestMobileErrorHandler:
    def setup_method(self) -> None:
        self.handler = MobileErrorHandler()

    def test_check_response_dict_payload_success_no_error(self) -> None:
        response = {'value': {'some_key': 'some_value'}}
        # Should not raise any exception
        self.handler.check_response(response)

    def test_check_response_invalid_payload(self) -> None:
        # Malformed json string
        self.handler.check_response({'value': 'not json'})
        # Payload is json string but not dict
        self.handler.check_response({'value': json.dumps([1, 2, 3])})
        # Payload dict value is not dict
        self.handler.check_response({'value': {'value': 'not a dict'}})
        # Payload dict value has no error key
        self.handler.check_response({'value': {'value': {'message': 'no error'}}})

    def test_check_response_standard_error(self) -> None:
        response = {
            'value': {
                'value': {
                    'error': 'no such element',
                    'message': 'Element was not found',
                    'stacktrace': 'trace line 1\ntrace line 2',
                }
            }
        }
        with pytest.raises(sel_exceptions.NoSuchElementException) as exc_info:
            self.handler.check_response(response)

        assert 'Element was not found' in exc_info.value.msg
        assert exc_info.value.stacktrace == ['trace line 1', 'trace line 2']

    def test_check_response_json_string_payload(self) -> None:
        inner_value = {
            'value': {
                'error': 'invalid selector',
                'message': 'The selector is invalid',
            }
        }
        response = {'value': json.dumps(inner_value)}
        with pytest.raises(sel_exceptions.InvalidSelectorException) as exc_info:
            self.handler.check_response(response)

        assert 'The selector is invalid' in exc_info.value.msg

    def test_check_response_no_such_context_message(self) -> None:
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

    def test_check_response_invalid_switch_to_target_message(self) -> None:
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

    def test_check_response_unexpected_alert_present(self) -> None:
        response = {
            'value': {
                'value': {
                    'error': 'unexpected alert open',
                    'message': 'Alert is present',
                    'data': 'Alert text content',
                }
            }
        }
        with pytest.raises(sel_exceptions.UnexpectedAlertPresentException) as exc_info:
            self.handler.check_response(response)

        assert exc_info.value.msg == 'Alert is present'
        assert exc_info.value.alert_text == 'Alert text content'

    def test_check_response_unknown_mapped_error(self) -> None:
        response = {
            'value': {
                'value': {
                    'error': 'unmapped error name',
                    'message': 'Some custom error',
                }
            }
        }
        with pytest.raises(sel_exceptions.WebDriverException) as exc_info:
            self.handler.check_response(response)

        assert exc_info.value.msg == 'Some custom error'
