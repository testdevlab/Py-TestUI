class Configuration:
    __screenshot_path: str = ""
    __save_screenshot_on_fail: bool = True
    __save_full_stacktrace: bool = True

    @property
    def screenshot_path(self) -> str:
        return self.__screenshot_path

    @screenshot_path.setter
    def screenshot_path(self, path: str) -> None:
        self.__screenshot_path = path

    @property
    def save_screenshot_on_fail(self) -> bool:
        return self.__save_screenshot_on_fail

    @save_screenshot_on_fail.setter
    def save_screenshot_on_fail(self, value: bool) -> None:
        self.__save_screenshot_on_fail = value

    @property
    def save_full_stacktrace(self) -> bool:
        return self.__save_full_stacktrace

    @save_full_stacktrace.setter
    def save_full_stacktrace(self, value: bool) -> None:
        self.__save_full_stacktrace = value
