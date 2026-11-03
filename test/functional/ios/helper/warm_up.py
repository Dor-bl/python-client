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

"""Start and quit one Appium session so WebDriverAgent's first, slowest launch happens before the tests.

Used by CI only. Failures are reported but don't fail the step: the tests retry on their own.
"""

import sys

from appium import webdriver
from appium.webdriver.client_config import AppiumClientConfig
from test.functional.test_helper import create_session_with_wda_retry
from test.helpers.constants import SERVER_URL_BASE

from .options import make_options


def main() -> int:
    client_config = AppiumClientConfig(remote_server_addr=SERVER_URL_BASE)
    client_config.timeout = 300
    try:
        driver = create_session_with_wda_retry(lambda: webdriver.Remote(options=make_options(), client_config=client_config))
    except Exception as e:  # noqa: BLE001
        print(f'Warm-up session failed: {e}', file=sys.stderr)
        return 0
    driver.quit()
    print('Warm-up session started and quit successfully')
    return 0


if __name__ == '__main__':
    sys.exit(main())
