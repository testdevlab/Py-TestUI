from testui.support.configuration import Configuration


class FakeWebElement:
    def __init__(self, attrs=None, displayed=True):
        self.attrs = attrs or {}
        self.displayed = displayed
        self.location = {"x": 10, "y": 20}
        self.size = {"width": 30, "height": 40}

    def get_attribute(self, name):
        return self.attrs.get(name)

    def is_displayed(self):
        return self.displayed


class FakeWebDriver:
    def __init__(self, elements):
        self.elements = elements
        self.find_calls = 0
        self.script_calls = []

    def find_element(self, by=None, value=None):
        self.find_calls += 1
        if not self.elements:
            raise Exception("not found")
        return self.elements[0]

    def find_elements(self, by=None, value=None):
        self.find_calls += 1
        return self.elements

    def execute_script(self, script, *args):
        self.script_calls.append((script, args))
        return args


class FakeTestUIDriver:
    def __init__(self, elements, soft_assert=False):
        self.logger_name = None
        self.soft_assert = soft_assert
        self.device_name = "Device"
        self._driver = FakeWebDriver(elements)
        self.configuration = Configuration()
        self.configuration.save_screenshot_on_fail = False
        self.errors = []

    def get_driver(self):
        return self._driver

    def set_error(self, error):
        self.errors.append(error)
