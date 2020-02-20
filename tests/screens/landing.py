from testui.elements.testui_element import e


class LandingScreen(object):
    #  Page Element Definitions
    def __init__(self, driver):
        self.__log_in_button = e(driver, "name", "btnK")
        self.__log_in_button_2 = e(driver, "xpath", "//button[@class='Tg7LZd']")

    #  Page Methods
    def i_am_in_landing_screen(self):
        self.__log_in_button.wait_until_visible()

    def i_am_in_mobile_landing_screen(self):
        self.__log_in_button_2.wait_until_visible()
