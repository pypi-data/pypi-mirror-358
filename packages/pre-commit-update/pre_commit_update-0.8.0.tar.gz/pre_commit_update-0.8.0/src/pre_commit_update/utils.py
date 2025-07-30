import functools
import os
from typing import Optional, Union

import click
import git
import tomli


class RepoType(click.types.StringParamType):
    name: str = "repo_url_trim"


def is_git_remote(url: str) -> bool:
    return url.strip() not in ("local", "meta")


def get_git_remote_latest_hash(url: str) -> str:  # pragma: no cover
    return git.cmd.Git().ls_remote("--exit-code", url, "HEAD").split()[0]


def get_git_remote_tags_list(url: str) -> list:  # pragma: no cover
    return (
        git.cmd.Git()
        .ls_remote("--exit-code", "--tags", url, sort="v:refname")
        .split("\n")
    )


def get_color(text: str, color: str) -> str:
    return click.style(str(text), fg=color)


def get_passed_params(ctx: click.Context) -> dict:
    return {
        k: v
        for k, v in ctx.params.items()
        if ctx.get_parameter_source(k) == click.core.ParameterSource.COMMANDLINE
    }


def get_toml_config(
    defaults: Optional[dict] = None,
    toml_path: Optional[str] = None,
    key: str = "tool.pre-commit-update",
) -> dict:
    try:
        file_path: str = toml_path or os.path.join(os.getcwd(), "pyproject.toml")
        with open(file_path, "rb") as f:
            toml_dict: dict = tomli.load(f)
        toml_params: dict = functools.reduce(
            lambda c, k: c[k], key.split("."), toml_dict
        )
        return {**defaults, **toml_params} if defaults else toml_params
    except (FileNotFoundError, KeyError):
        return defaults or {}


def get_dict_diffs(d1: dict, d2: dict) -> dict:
    return {k: d2[k] for k in d2 if d2[k] != d1[k]}


def get_converted_iterable(
    iterable: Union[list, tuple], _type: type[Union[list, tuple]]
) -> Union[tuple, list]:
    return (
        _type(map(functools.partial(get_converted_iterable, _type=_type), iterable))
        if isinstance(iterable, (list, tuple))
        else iterable
    )


def get_converted_dict_values(d: dict) -> dict:
    for k, v in d.items():
        if isinstance(v, dict):
            v = get_converted_dict_values(v)
        d[k] = get_converted_iterable(v, list) if isinstance(v, tuple) else v
    return d
