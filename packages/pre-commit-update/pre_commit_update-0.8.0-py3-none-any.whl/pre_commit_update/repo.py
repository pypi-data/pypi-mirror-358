import string
from typing import Optional

from packaging.version import InvalidVersion, Version
from packaging.version import parse as parse_version


class Repo:
    def __init__(
        self,
        repo: dict,
        tags_and_hashes: dict,
        tag_prefix: Optional[str] = None,
        latest_hash: Optional[str] = None,
        all_versions: bool = False,
        bleeding_edge: bool = False,
    ) -> None:
        self.__trim: str = repo["trim"]
        self.__tags_and_hashes: dict = tags_and_hashes
        self.__latest_hash: Optional[str] = latest_hash
        self.__current_is_hash: bool = self.__is_version_a_hash(repo["rev"])
        self.__current_version: str = repo["rev"]
        self.__latest_version: str = self.__get_latest_version(
            all_versions, bleeding_edge, tag_prefix
        )

    @property
    def has_tags_and_hashes(self) -> bool:
        return bool(self.__tags_and_hashes)

    @property
    def trim(self) -> str:
        return self.__trim

    @property
    def current_version(self) -> str:
        return self.__current_version

    @property
    def latest_version(self) -> str:
        return self.__latest_version

    @property
    def latest_is_hash(self) -> bool:
        return self.__is_version_a_hash(self.__latest_version)

    @staticmethod
    def __is_version_a_hash(version: str) -> bool:
        # The minimum length for an abbreviated hash is 4:
        # <https://git-scm.com/docs/git-config#Documentation/git-config.txt-coreabbrev>.
        # Credit goes to Levon (https://stackoverflow.com/users/1209279/levon)
        # for this idea: <https://stackoverflow.com/a/11592279/7593853>.
        return len(version) >= 4 and set(version).issubset(string.hexdigits)

    def __get_latest_tag(self, all_versions: bool, tag_prefix: Optional[str]) -> str:
        if not self.has_tags_and_hashes:
            return self.__current_version
        if all_versions:
            return next(iter(self.__tags_and_hashes))
        for tag in self.__tags_and_hashes:
            try:
                version: Version = parse_version(
                    tag if not tag_prefix else tag.replace(tag_prefix, "")
                )
                if version.is_prerelease:
                    continue
                return tag
            except InvalidVersion:
                continue
        return self.__current_version

    def __get_latest_version(
        self, all_versions: bool, bleeding_edge: bool, tag_prefix: Optional[str] = None
    ) -> str:
        latest_tag: str = self.__get_latest_tag(
            all_versions or bleeding_edge, tag_prefix
        )
        latest_tag_hash: Optional[str] = self.__tags_and_hashes.get(latest_tag)
        try:
            parse_version(
                self.__current_version
                if not tag_prefix
                else self.__current_version.replace(tag_prefix, "")
            )
            if (
                bleeding_edge
                and self.__latest_hash
                and latest_tag_hash
                and latest_tag_hash != self.__latest_hash
            ):
                return self.__latest_hash
            return latest_tag
        except (InvalidVersion, IndexError):
            pass
        if self.__current_is_hash:
            if bleeding_edge and self.__latest_hash and latest_tag_hash:
                return (
                    self.__latest_hash
                    if self.__latest_hash != latest_tag_hash
                    else latest_tag
                )
            if latest_tag_hash and latest_tag_hash != self.__current_version:
                return latest_tag_hash
        if not self.has_tags_and_hashes and self.__latest_hash:
            return self.__latest_hash
        return self.__current_version
