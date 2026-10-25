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

from appium.common.helper import extract_const_attributes


class DummyConstants:
    VAL1 = 100
    VAL2 = 'test_value'
    _PRIVATE = 'private_const'
    lower_case = 'ignored'

    @classmethod
    def CLASS_METHOD(cls):
        pass

    @staticmethod
    def STATIC_METHOD():
        pass

    def instance_method(self):
        pass


def test_extract_const_attributes():
    constants = extract_const_attributes(DummyConstants)
    assert constants == {
        'VAL1': 100,
        'VAL2': 'test_value',
        '_PRIVATE': 'private_const',
    }
