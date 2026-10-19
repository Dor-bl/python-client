import pytest

from appium.webdriver.errorhandler import format_stacktrace


class TestFormatStacktrace:
    @pytest.mark.parametrize(
        ('input_data', 'expected'),
        [
            (None, []),
            ('', []),
            ([], []),
            ({}, []),
        ],
    )
    def test_format_stacktrace_empty(self, input_data: None | str | list | dict, expected: list[str]) -> None:
        assert format_stacktrace(input_data) == expected

    def test_format_stacktrace_string(self) -> None:
        stack = 'Error: Something went wrong\n    at foo (file.js:10)\n    at bar (file.js:20)'
        expected = [
            'Error: Something went wrong',
            '    at foo (file.js:10)',
            '    at bar (file.js:20)',
        ]
        assert format_stacktrace(stack) == expected

    def test_format_stacktrace_sequence_dicts(self) -> None:
        frames = [
            {
                'lineNumber': 42,
                'fileName': 'index.js',
                'methodName': 'handleClick',
                'className': 'MyComponent',
            },
            {
                'fileName': 'utils.js',
                'methodName': 'helper',
            },
            {},
        ]
        expected = [
            '    at MyComponent.handleClick (index.js:42)',
            '    at helper (utils.js)',
            '    at <anonymous> (<anonymous>)',
        ]
        assert format_stacktrace(frames) == expected

    def test_format_stacktrace_sequence_with_non_dict_elements(self) -> None:
        frames = [
            'not a dict',
            123,
            None,
            {
                'lineNumber': 5,
                'fileName': 'main.py',
                'methodName': 'run',
            },
        ]
        expected = [
            '    at run (main.py:5)',
        ]
        assert format_stacktrace(frames) == expected

    def test_format_stacktrace_non_iterable_type_error(self) -> None:
        assert format_stacktrace(123) == []
        assert format_stacktrace(True) == []
