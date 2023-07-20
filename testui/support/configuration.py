class Configuration:
    """
    Configuration class for TestUI
    """

    __screenshot_path: str = ""
    __save_screenshot_on_fail: bool = True
    __save_full_stacktrace: bool = True

    @property
    def screenshot_path(self) -> str:
        """
        Path to save screenshots
        :return: String
        """
        return self.__screenshot_path

    @screenshot_path.setter
    def screenshot_path(self, path: str) -> None:
        """
        Path to save screenshots
        :param path: String
        """
        self.__screenshot_path = path

    @property
    def save_screenshot_on_fail(self) -> bool:
        """
        Save screenshot on fail
        :return: Boolean
        """
        return self.__save_screenshot_on_fail

    @save_screenshot_on_fail.setter
    def save_screenshot_on_fail(self, value: bool) -> None:
        """
        Save screenshot on fail
        :param value: Boolean
        """
        self.__save_screenshot_on_fail = value

    @property
    def save_full_stacktrace(self) -> bool:
        """
        Save full stacktrace on fail
        :return: Boolean
        """
        return self.__save_full_stacktrace

    @save_full_stacktrace.setter
    def save_full_stacktrace(self, value: bool) -> None:
        """
        Save full stacktrace on fail
        :param value: Boolean
        """
        self.__save_full_stacktrace = value
