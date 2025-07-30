from collections import Counter
from typing import Literal, Optional

from ..utils import get_converted_iterable
from . import MessageManager


class OptionManager:
    def __init__(
        self,
        dry_run: bool,
        dry_run_mode: Optional[Literal["strict", "warn"]],
        all_versions: bool,
        warnings: bool,
        exclude: tuple,
        keep: tuple,
        bleeding_edge: tuple,
        tag_prefix: tuple[tuple[str, str]],
        repo_trims: set,
    ) -> None:
        self.__dry_run: bool = dry_run
        self.__dry_run_mode: Optional[Literal["strict", "warn"]] = dry_run_mode
        self.__all_versions: bool = all_versions
        self.__warnings: bool = warnings
        self.__exclude: list = list(sorted(exclude))
        self.__keep: list = list(sorted(keep))
        self.__bleeding_edge: list = list(sorted(bleeding_edge))
        self.__tag_prefix: list[list[str]] = get_converted_iterable(sorted(tag_prefix, key=lambda x: x[0]), list)  # type: ignore
        self.__repo_trims: set = repo_trims

    @property
    def dry_run_mode(self) -> Optional[Literal["strict", "warn"]]:
        return self.__dry_run_mode

    @property
    def exclude(self) -> tuple:
        return tuple(self.__exclude)

    @property
    def keep(self) -> tuple:
        return tuple(self.__keep)

    @property
    def bleeding_edge(self) -> tuple:
        return tuple(self.__bleeding_edge)

    @property
    def tag_prefix(self) -> tuple[tuple[str, str], ...]:
        return get_converted_iterable(self.__tag_prefix, tuple)  # type: ignore

    @staticmethod
    def __get_list_element_indexes(lst: list, element: str) -> list:
        return [
            i
            for i, item in enumerate(lst)
            if (isinstance(item, str) and item == element)
            or (isinstance(item, list) and item[0] == element)
        ]

    def __remove_list_elements(
        self, lst: list, element: str, preserve_first: bool = False
    ) -> None:
        indexes: list = self.__get_list_element_indexes(lst, element)
        for index in sorted(indexes[1:] if preserve_first else indexes, reverse=True):
            del lst[index]

    def __validate_dry_run(self, message_manager: MessageManager) -> None:
        if not self.__dry_run and self.__dry_run_mode:
            message_manager.add_warning_message(
                "*", "--dry-run-mode option ignored (--dry-run not enabled)"
            )
            self.__dry_run_mode = None
            return
        if self.dry_run_mode and self.__dry_run_mode not in ("strict", "warn"):
            message_manager.add_warning_message(
                "*",
                f"--dry-run-mode option ignored ({self.__dry_run_mode} - not supported)",
            )
            self.__dry_run_mode = None

    def __validate_invalid_repo_trims(self, message_manager: MessageManager) -> None:
        lists_to_update: tuple = (
            self.__exclude,
            self.__keep,
            self.__bleeding_edge,
            self.__tag_prefix,
        )
        for trim in (
            set(
                self.__exclude
                + self.__keep
                + self.__bleeding_edge
                + [trim[0] for trim in self.__tag_prefix]
            )
            - self.__repo_trims
        ):
            if trim == "*":
                continue
            for lst in lists_to_update:
                self.__remove_list_elements(lst, trim)
            message_manager.add_warning_message(trim, "invalid repo trim (ignored)")

    def __validate_wildcards(self, message_manager: MessageManager) -> None:
        for option, flag, other_options in [
            (
                self.__exclude,
                "--exclude",
                [(self.__keep, "--keep"), (self.__bleeding_edge, "--bleeding-edge")],
            ),
            (
                self.__keep,
                "--keep",
                [
                    (self.__exclude, "--exclude"),
                ],
            ),
            (self.__bleeding_edge, "--bleeding-edge", [(self.__exclude, "--exclude")]),
        ]:
            if "*" in option:
                for trim in [t for t in option if t != "*"]:
                    message_manager.add_warning_message(
                        trim,
                        f"{flag} option obsolete ({flag} *)",
                    )
                option.clear()
                option.append("*")
                for other_option, other_flag in other_options:
                    for trim in other_option[:]:
                        message_manager.add_warning_message(
                            trim,
                            f"{other_flag} option ignored ({flag} *)",
                        )
                        other_option.remove(trim)
                return

    def __validate_exclusive_repo_trims(self, message_manager: MessageManager) -> None:
        options: list[tuple] = [
            (
                self.__exclude,
                "--exclude",
                [(self.__keep, "--keep"), (self.__bleeding_edge, "--bleeding-edge")],
            ),
        ]

        for option, flag, other_options in options:
            for trim in option:
                for other_option, other_flag in other_options:
                    if trim not in other_option:
                        continue
                    self.__remove_list_elements(other_option, trim)
                    if trim == "*":
                        continue
                    message_manager.add_warning_message(
                        trim, f"{other_flag} option ignored ({flag})"
                    )

    def __validate_bleeding_edge(self, message_manager: MessageManager) -> None:
        if self.__all_versions:
            return
        for trim in [t for t in self.__bleeding_edge if t != "*"]:
            message_manager.add_warning_message(
                trim, "--all-versions option ignored (--bleeding-edge)"
            )

    def __validate_duplicate_repo_trims(self, message_manager: MessageManager) -> None:
        options: list[tuple] = [
            (self.__exclude, "--exclude", lambda x: x),
            (self.__keep, "--keep", lambda x: x),
            (self.__bleeding_edge, "--bleeding-edge", lambda x: x),
            (self.__tag_prefix, "--tag-prefix", lambda x: [item[0] for item in x]),
        ]

        for option, flag, extract_func in options:
            for trim, count in Counter(extract_func(option)).items():
                if count <= 1:
                    continue
                self.__remove_list_elements(
                    option,
                    trim,
                    True,
                )
                message_manager.add_warning_message(
                    trim, f"{flag} duplicate(s) detected (ignored duplicate(s))"
                )

    def validate(self, message_manager: MessageManager) -> None:
        self.__validate_dry_run(message_manager)
        self.__validate_invalid_repo_trims(message_manager)
        self.__validate_duplicate_repo_trims(message_manager)
        self.__validate_exclusive_repo_trims(message_manager)
        self.__validate_wildcards(message_manager)
        self.__validate_bleeding_edge(message_manager)
