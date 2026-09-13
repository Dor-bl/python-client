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

from appium.webdriver.errorhandler import format_stacktrace


def test_format_stacktrace_empty() -> None:
    assert format_stacktrace(None) == []
    assert format_stacktrace('') == []
    assert format_stacktrace([]) == []


def test_format_stacktrace_string() -> None:
    assert format_stacktrace('line1\nline2\nline3') == ['line1', 'line2', 'line3']


def test_format_stacktrace_frames() -> None:
    frames = [
        {
            'fileName': 'App.js',
            'lineNumber': 100,
            'methodName': 'handleClick',
            'className': 'AppComponent',
        },
        {
            'fileName': 'Server.py',
            'lineNumber': 42,
            'methodName': 'process',
        },
        {
            'methodName': 'anonymous_func',
            'className': 'Util',
        },
        {
            'fileName': 'index.js',
        },
        {},
    ]

    expected = [
        '    at AppComponent.handleClick (App.js:100)',
        '    at process (Server.py:42)',
        '    at Util.anonymous_func (<anonymous>)',
        '    at <anonymous> (index.js)',
        '    at <anonymous> (<anonymous>)',
    ]

    assert format_stacktrace(frames) == expected


def test_format_stacktrace_non_dict_elements() -> None:
    frames = [
        'not a dict',
        123,
        {'fileName': 'test.py', 'lineNumber': 10, 'methodName': 'foo'},
        None,
    ]
    expected = ['    at foo (test.py:10)']
    assert format_stacktrace(frames) == expected


def test_format_stacktrace_invalid_type() -> None:
    assert format_stacktrace(123) == []
