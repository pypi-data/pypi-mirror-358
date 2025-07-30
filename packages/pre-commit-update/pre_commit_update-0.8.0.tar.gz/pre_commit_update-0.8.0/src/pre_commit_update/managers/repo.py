import re
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

from packaging.version import InvalidVersion
from packaging.version import parse as parse_version

from ..repo import Repo
from ..utils import get_git_remote_latest_hash, get_git_remote_tags_list, is_git_remote
from . import MessageManager


class RepoManager:
    def __init__(
        self,
        repos_data: list[dict],
        all_versions: bool,
        jobs: Optional[int],
        exclude: tuple,
        keep: tuple,
        bleeding_edge: tuple,
        tag_prefix: tuple[tuple[str, str], ...],
    ) -> None:
        self.__all_versions: bool = all_versions
        self.__jobs: Optional[int] = jobs
        self.__exclude: tuple = exclude
        self.__keep: tuple = keep
        self.__bleeding_edge: tuple = bleeding_edge
        self.__tag_prefix: tuple[tuple[str, str], ...] = tag_prefix
        self.__repos_data: list[dict] = self.__add_trim_to_repos_data(repos_data)
        self.__repos_latest_hashes, self.__repos_tags_with_hashes = (
            self.__get_repos_tags_with_hashes_and_latest_hashes()
        )
        self.__repos_list: list[Optional[Repo]] = self.__get_repos_list()

    @property
    def repos_data(self) -> list[dict]:
        return self.__remove_trim_from_repos_data(self.__repos_data)

    @staticmethod
    def __add_trim_to_repos_data(repos_data: list[dict]) -> list[dict]:
        for i, repo in enumerate(repos_data):
            if not is_git_remote(repo["repo"]):
                continue
            repo["trim"] = repo["repo"].rsplit("/", 1)[-1].removesuffix(".git")
            repos_data[i] = repo
        return repos_data

    @staticmethod
    def __remove_trim_from_repos_data(repos_data: list[dict]) -> list[dict]:
        for i, repo in enumerate(repos_data):
            repo.pop("trim", None)
            repos_data[i] = repo
        return repos_data

    @staticmethod
    def __get_repo_fixed_tags_and_hashes(
        tag_hash: Optional[dict], tag_prefix: Optional[str]
    ) -> dict:
        # Due to various prefixes that devs choose for tags, strip them down to semantic version numbers only.
        # Take tag_prefix into consideration ("pre-commit-tag-v0.1.1")
        # Store it inside the dict ("ver1.2.3": "1.2.3") and parse the value to get the correct sort.
        # Remove invalid suffixes ("-test", "-split", ...)
        # Return the original value (key) once everything is parsed/sorted.
        if not tag_hash:
            return {}
        fixed_tags: dict = {}
        for tag in tag_hash:
            if tag_prefix and not tag.startswith(tag_prefix):
                continue
            tag_no_prefix: str = tag.removeprefix(tag_prefix) if tag_prefix else tag
            match: Optional[re.Match[str]] = re.search(
                "([a-zA-Z]*)\\d+.*", tag_no_prefix
            )
            if match:
                try:
                    fixed_tags[tag] = parse_version(match.group(0))
                except InvalidVersion:
                    continue
        return {
            key: tag_hash[key]
            for key in sorted(fixed_tags, key=lambda k: fixed_tags[k], reverse=True)
        }

    def __get_repo_tags_with_hashes_and_latest_hash(
        self, repo: dict
    ) -> tuple[Optional[str], Optional[dict]]:
        if not is_git_remote(repo["repo"]) or self.__is_repo_in_exclude(repo["trim"]):
            return None, None

        with ThreadPoolExecutor(max_workers=2) as pool:
            tasks: list = [
                pool.submit(get_git_remote_latest_hash, repo["repo"]),
                pool.submit(get_git_remote_tags_list, repo["repo"]),
            ]

        exc_latest_hash: Optional[BaseException] = tasks[0].exception()
        exc_tags: Optional[BaseException] = tasks[1].exception()

        return tasks[0].result() if not exc_latest_hash else None, (
            {
                tag.split("\t", 1)[1]
                .replace("refs/tags/", "")
                .replace("^{}", ""): tag.split("\t", 1)[0]
                for tag in tasks[1].result()
            }
            if not exc_tags
            else None
        )

    def __get_repos_tags_with_hashes_and_latest_hashes(
        self,
    ) -> tuple[list[str], list[dict]]:
        with ThreadPoolExecutor(max_workers=self.__jobs) as pool:
            tasks: list = [
                pool.submit(self.__get_repo_tags_with_hashes_and_latest_hash, repo)
                for repo in self.__repos_data
            ]
            results: list[tuple[Optional[str], Optional[dict]]] = [
                task.result() for task in tasks
            ]
            latest_hashes, tags_list = zip(*results)
            return latest_hashes, [
                self.__get_repo_fixed_tags_and_hashes(
                    tags, self.__get_repo_tag_prefix(repo.get("trim"))
                )
                for tags, repo in zip(tags_list, self.__repos_data)
            ]

    def __get_repos_list(self) -> list[Optional[Repo]]:
        return [
            (
                Repo(
                    repo=repo,
                    tags_and_hashes=tags_and_hashes,
                    tag_prefix=self.__get_repo_tag_prefix(repo["trim"]),
                    latest_hash=latest_hash,
                    all_versions=self.__all_versions,
                    bleeding_edge=self.__is_repo_in_bleeding_edge(repo["trim"]),
                )
                if is_git_remote(repo["repo"])
                else None
            )
            for repo, latest_hash, tags_and_hashes in zip(
                self.__repos_data,
                self.__repos_latest_hashes,
                self.__repos_tags_with_hashes,
            )
        ]

    def __is_repo_in_exclude(self, repo_trim: str) -> bool:
        return repo_trim in self.__exclude or self.__exclude == ("*",)

    def __is_repo_in_keep(self, repo_trim: str) -> bool:
        return repo_trim in self.__keep or self.__keep == ("*",)

    def __is_repo_in_bleeding_edge(self, repo_trim: str) -> bool:
        return repo_trim in self.__bleeding_edge or self.__bleeding_edge == ("*",)

    def __is_repo_in_tag_prefix(self, repo_trim: str) -> bool:
        return self.__get_repo_tag_prefix(repo_trim) is not None

    def __get_repo_tag_prefix(self, repo_trim: Optional[str]) -> Optional[str]:
        if not repo_trim:
            return None
        return next((t[1] for t in self.__tag_prefix if t[0] == repo_trim), None)

    def get_updates(self, messages: MessageManager) -> None:
        for repo in self.__repos_list:
            if repo is None:
                continue

            is_in_exclude: bool = self.__is_repo_in_exclude(repo.trim)
            is_in_keep: bool = self.__is_repo_in_keep(repo.trim)
            is_bleeding_edge: bool = self.__is_repo_in_bleeding_edge(repo.trim)
            is_tag_prefix: bool = self.__is_repo_in_tag_prefix(repo.trim)

            if not repo.has_tags_and_hashes and not is_in_exclude:
                messages.add_warning_message(repo.trim, "0 tagged hashes fetched")
            if is_in_exclude:
                messages.add_exclude_message(repo.trim, repo.current_version)
            elif is_in_keep:
                messages.add_keep_message(
                    repo.trim,
                    repo.current_version,
                    repo.latest_version,
                    repo.latest_is_hash,
                    is_bleeding_edge,
                    is_tag_prefix,
                )
            elif repo.current_version != repo.latest_version:
                messages.add_update_message(
                    repo.trim,
                    repo.current_version,
                    repo.latest_version,
                    repo.latest_is_hash,
                    is_bleeding_edge,
                    is_tag_prefix,
                )
                self.__repos_data[self.__repos_list.index(repo)][
                    "rev"
                ] = repo.latest_version
            else:
                messages.add_no_update_message(
                    repo.trim,
                    repo.current_version,
                    repo.latest_is_hash,
                    is_bleeding_edge,
                    is_tag_prefix,
                )
