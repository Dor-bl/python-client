import logging
from typing import Any

from appium.webdriver.errorhandler import format_stacktrace


def test_format_stacktrace_none() -> None:
    assert format_stacktrace(None) == []


def test_format_stacktrace_empty_string() -> None:
    assert format_stacktrace('') == []


def test_format_stacktrace_string() -> None:
    trace = 'line1\nline2\nline3'
    assert format_stacktrace(trace) == ['line1', 'line2', 'line3']


def test_format_stacktrace_list_dicts() -> None:
    frames = [
        {
            'lineNumber': 42,
            'fileName': 'app.js',
            'methodName': 'handleClick',
            'className': 'Button',
        },
        {
            'fileName': 'index.js',
            'methodName': 'main',
        },
        'not_a_dict',  # Should be skipped
    ]
    expected = [
        '    at Button.handleClick (app.js:42)',
        '    at main (index.js)',
    ]
    assert format_stacktrace(frames) == expected


def test_format_stacktrace_type_error(caplog: Any) -> None:
    with caplog.at_level(logging.DEBUG):
        result = format_stacktrace(123)  # type: ignore[arg-type]
        assert result == []
        assert 'Failed to format stacktrace frame' in caplog.text
