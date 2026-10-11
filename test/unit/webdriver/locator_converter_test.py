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
from selenium.webdriver.remote.locator_converter import LocatorConverter

from appium.webdriver.common.appiumby import AppiumBy
from appium.webdriver.locator_converter import AppiumLocatorConverter


class TestAppiumLocatorConverter:
    def test_subclass_locator_converter(self) -> None:
        converter = AppiumLocatorConverter()
        assert isinstance(converter, LocatorConverter)

    @pytest.mark.parametrize(
        'by, value',
        [
            ('id', 'my_element_id'),
            ('xpath', '//button[@name="submit"]'),
            ('css selector', '.my-class'),
            (AppiumBy.ACCESSIBILITY_ID, 'accessibility_identifier'),
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("Cancel")'),
            (AppiumBy.IOS_PREDICATE, 'label == "Confirm"'),
            (AppiumBy.IOS_CLASS_CHAIN, '**/XCUIElementTypeCell'),
            ('', ''),
            ('custom_strategy', 'custom_value'),
        ],
    )
    def test_convert_returns_unmodified_tuple(self, by: str, value: str) -> None:
        converter = AppiumLocatorConverter()
        result = converter.convert(by, value)
        assert result == (by, value)
        assert isinstance(result, tuple)
