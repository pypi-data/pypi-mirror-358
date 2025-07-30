from typing import Any, Optional

from ruamel.yaml import YAML

from ..utils import get_toml_config


class YAMLManager:
    def __init__(self, path: str, config_file_path: Optional[str] = None) -> None:
        self.__file: YAML = YAML()
        self.__path: str = path
        self.__data: Any = None
        self.__config: dict = get_toml_config(
            toml_path=config_file_path, key="tool.pre-commit-update.yaml"
        )
        self.__configure()
        self.__load()

    @property
    def data(self) -> Any:
        return self.__data

    @data.setter
    def data(self, value: dict) -> None:
        self.__data = value

    def __configure(self) -> None:  # pragma: no cover
        if not self.__config:
            self.__file.indent(sequence=4)
        else:
            self.__file.indent(**self.__config)
        self.__file.preserve_quotes = True

    def __load(self) -> None:
        with open(self.__path, encoding="utf-8") as f:
            self.__data = self.__file.load(f.read())

    def dump(self) -> None:
        with open(self.__path, "w", encoding="utf-8") as f:
            self.__file.dump(self.data, f, transform=self.__post_process)

    @staticmethod
    def __post_process(stream: str) -> str:
        return "".join(
            s.rstrip() + ("\n" if s.endswith("\n") else "")
            for s in stream.splitlines(keepends=True)
        )
