from testui.elements.testui_element import e


class LandingScreen(object):
    #  Page Element Definitions
    def __init__(self, driver):
        self.__log_in_button = e(driver, "name", "btnK")
        self.__log_in_button_2 = e(driver, "xpath", "//button[@class='Tg7LZd']")
        self.__google_play_screen = e(driver, "uiautomator", "text(\"Apps\")")

    #  Page Methods
    def i_am_in_landing_screen(self):
        self.__log_in_button.wait_until_visible()

    def i_am_in_mobile_landing_screen(self):
        self.__log_in_button_2.wait_until_visible()

    def i_am_in_google_play_landing_screen(self):
        self.__google_play_screen.wait_until_visible().get_text()
