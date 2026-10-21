from appium.options.common.base import AppiumOptions


def test_as_w3c():
    caps = {
        'platformName': 'Android',
        'platformVersion': '11.0',
        'deviceName': 'Android Emulator',
        'automationName': 'UiAutomator2',
        'app': '/path/to/app.apk',
        'customCap': 'customValue',
    }
    res = AppiumOptions.as_w3c(caps)
    expected = {
        'capabilities': {
            'firstMatch': [{}],
            'alwaysMatch': {
                'platformName': 'Android',
                'appium:platformVersion': '11.0',
                'appium:deviceName': 'Android Emulator',
                'appium:automationName': 'UiAutomator2',
                'appium:app': '/path/to/app.apk',
                'appium:customCap': 'customValue',
            },
        }
    }
    assert res == expected
