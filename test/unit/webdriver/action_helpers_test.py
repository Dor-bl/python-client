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

import httpretty
import pytest

from test.unit.helper.test_helper import android_w3c_driver, appium_command, get_httpretty_request_body


class TestActionHelpers:
    @httpretty.activate
    def test_swipe_with_tuples(self):
        driver = android_w3c_driver()
        httpretty.register_uri(
            httpretty.POST,
            appium_command('/session/1234567890/actions'),
            body=json.dumps({'value': None}),
        )

        driver.swipe((100, 200), (300, 400))

        req_body = get_httpretty_request_body(httpretty.last_request())
        actions = req_body['actions'][0]['actions']
        assert actions[0]['type'] == 'pointerMove'
        assert actions[0]['x'] == 100
        assert actions[0]['y'] == 200
        assert actions[1]['type'] == 'pointerDown'
        assert actions[2]['type'] == 'pointerMove'
        assert actions[2]['x'] == 300
        assert actions[2]['y'] == 400
        assert actions[3]['type'] == 'pointerUp'

    @httpretty.activate
    def test_swipe_with_tuples_and_duration(self):
        driver = android_w3c_driver()
        httpretty.register_uri(
            httpretty.POST,
            appium_command('/session/1234567890/actions'),
            body=json.dumps({'value': None}),
        )

        driver.swipe((100, 200), (300, 400), 500)

        req_body = get_httpretty_request_body(httpretty.last_request())
        actions = req_body['actions'][0]['actions']
        assert actions[0]['type'] == 'pointerMove'
        assert actions[0]['x'] == 100
        assert actions[0]['y'] == 200
        assert actions[1]['type'] == 'pointerDown'
        assert actions[2]['type'] == 'pointerMove'
        assert actions[2]['x'] == 300
        assert actions[2]['y'] == 400
        assert actions[2]['duration'] == 500
        assert actions[3]['type'] == 'pointerUp'

    @httpretty.activate
    def test_swipe_with_integers(self):
        driver = android_w3c_driver()
        httpretty.register_uri(
            httpretty.POST,
            appium_command('/session/1234567890/actions'),
            body=json.dumps({'value': None}),
        )

        driver.swipe(100, 200, 300, 400)

        req_body = get_httpretty_request_body(httpretty.last_request())
        actions = req_body['actions'][0]['actions']
        assert actions[0]['type'] == 'pointerMove'
        assert actions[0]['x'] == 100
        assert actions[0]['y'] == 200
        assert actions[1]['type'] == 'pointerDown'
        assert actions[2]['type'] == 'pointerMove'
        assert actions[2]['x'] == 300
        assert actions[2]['y'] == 400
        assert actions[3]['type'] == 'pointerUp'

    @httpretty.activate
    def test_swipe_with_integers_and_duration(self):
        driver = android_w3c_driver()
        httpretty.register_uri(
            httpretty.POST,
            appium_command('/session/1234567890/actions'),
            body=json.dumps({'value': None}),
        )

        driver.swipe(100, 200, 300, 400, duration=800)

        req_body = get_httpretty_request_body(httpretty.last_request())
        actions = req_body['actions'][0]['actions']
        assert actions[0]['type'] == 'pointerMove'
        assert actions[0]['x'] == 100
        assert actions[0]['y'] == 200
        assert actions[1]['type'] == 'pointerDown'
        assert actions[2]['type'] == 'pointerMove'
        assert actions[2]['x'] == 300
        assert actions[2]['y'] == 400
        assert actions[2]['duration'] == 800
        assert actions[3]['type'] == 'pointerUp'

    @httpretty.activate
    def test_swipe_invalid_args(self):
        driver = android_w3c_driver()

        with pytest.raises(ValueError):
            driver.swipe(100, 200)

        with pytest.raises(ValueError):
            driver.swipe((100, 200), 300)
