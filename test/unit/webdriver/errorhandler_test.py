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

import pytest

from appium.webdriver.errorhandler import format_stacktrace


@pytest.mark.parametrize('falsy_input', [None, '', [], ()])
def test_format_stacktrace_falsy_input(falsy_input: None | str | tuple | list) -> None:
    assert format_stacktrace(falsy_input) == []


def test_format_stacktrace_single_line_str() -> None:
    assert format_stacktrace('Error: something failed') == ['Error: something failed']


def test_format_stacktrace_multi_line_str() -> None:
    trace = 'Error: something failed\n  at func1 (file1.js:10)\n  at func2 (file2.js:20)'
    expected = ['Error: something failed', '  at func1 (file1.js:10)', '  at func2 (file2.js:20)']
    assert format_stacktrace(trace) == expected


def test_format_stacktrace_sequence_full_frame() -> None:
    frames = [
        {
            'className': 'com.example.MyClass',
            'methodName': 'myMethod',
            'fileName': 'MyClass.java',
            'lineNumber': 42,
        }
    ]
    assert format_stacktrace(frames) == ['    at com.example.MyClass.myMethod (MyClass.java:42)']


def test_format_stacktrace_sequence_missing_optional_fields() -> None:
    frames = [
        # Missing className and lineNumber
        {
            'methodName': 'onClick',
            'fileName': 'app.js',
        },
        # Missing fileName and methodName, with className
        {
            'className': 'MyComponent',
            'lineNumber': 10,
        },
        # Missing all optional fields
        {},
    ]
    expected = [
        '    at onClick (app.js)',
        '    at MyComponent.<anonymous> (<anonymous>:10)',
        '    at <anonymous> (<anonymous>)',
    ]
    assert format_stacktrace(frames) == expected


def test_format_stacktrace_sequence_non_dict_elements() -> None:
    frames = [
        {'methodName': 'validFunc', 'fileName': 'valid.js', 'lineNumber': 5},
        'invalid_string_frame',
        123,
        None,
        {'methodName': 'anotherValidFunc', 'fileName': 'valid.js', 'lineNumber': 15},
    ]
    expected = [
        '    at validFunc (valid.js:5)',
        '    at anotherValidFunc (valid.js:15)',
    ]
    assert format_stacktrace(frames) == expected


def test_format_stacktrace_type_error_handling() -> None:
    # Non-iterable type passed as sequence (bypassing static typing)
    assert format_stacktrace(12345) == []  # type: ignore[arg-type]
