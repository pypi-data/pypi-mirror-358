import os


class EnvManager:
    def __init__(self) -> None:
        self.__git_terminal_prompt: str = os.getenv("GIT_TERMINAL_PROMPT", "0")
        self.__python_io_encoding: str = os.getenv("PYTHONIOENCODING", "UTF-8")
        self.__python_utf_8: str = os.getenv("PYTHONUTF8", "1")

    @staticmethod
    def setup() -> None:
        os.environ["GIT_TERMINAL_PROMPT"] = "0"
        os.environ["PYTHONIOENCODING"] = "UTF-8"
        os.environ["PYTHONUTF8"] = "1"

    def restore(self) -> None:
        os.environ["GIT_TERMINAL_PROMPT"] = self.__git_terminal_prompt
        os.environ["PYTHONIOENCODING"] = self.__python_io_encoding
        os.environ["PYTHONUTF8"] = self.__python_utf_8
