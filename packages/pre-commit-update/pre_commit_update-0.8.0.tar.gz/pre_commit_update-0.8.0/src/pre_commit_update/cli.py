import os
import sys
from typing import Any, Literal, Optional

import click

from .managers import (
    EnvManager,
    MessageManager,
    OptionManager,
    RepoManager,
    YAMLManager,
)
from .utils import (
    RepoType,
    get_color,
    get_converted_dict_values,
    get_dict_diffs,
    get_passed_params,
    get_toml_config,
    is_git_remote,
)


def __get_config_file(config_file: Optional[str]) -> Optional[str]:
    if not config_file:
        return None

    if not config_file.endswith("pyproject.toml"):
        raise click.ClickException(
            "The configuration file must be a pyproject.toml file"
        )

    if config_file == "pyproject.toml":
        config_file = None

    return config_file


def __preview(
    *, defaults: dict, toml_params: dict, cmd_params: dict, final_params: dict
) -> None:
    click.echo(get_color("Default configuration values:", "blue"))
    click.echo("\n".join(f"{k} = {v}" for k, v in defaults.items()))
    click.echo(
        get_color("\npyproject.toml configuration values (difference):", "yellow")
    )
    click.echo(
        "\n".join(
            f"{k} = {v}" for k, v in get_dict_diffs(defaults, toml_params).items()
        )
        or "Same as the default configuration / no configuration found"
    )
    click.echo(get_color("\nCommand line configuration values (difference):", "red"))
    click.echo(
        "\n".join(
            f"{k} = {v}" for k, v in get_dict_diffs(toml_params, cmd_params).items()
        )
        or "Same as the default configuration / pyproject.toml configuration"
    )
    click.echo(get_color("\nFinal configuration values:", "green"))
    click.echo("\n".join(f"{k} = {v}" for k, v in final_params.items()))


def __run(
    *,
    config_file: Optional[str],
    dry_run: bool,
    dry_run_mode: Optional[Literal["strict", "warn"]] = None,
    all_versions: bool,
    verbose: bool,
    warnings: bool,
    jobs: Optional[int],
    exclude: tuple,
    keep: tuple,
    bleeding_edge: tuple,
    tag_prefix: tuple[tuple[str, str]],
) -> None:
    # Backup and set needed env variables
    env_manager: EnvManager = EnvManager()
    env_manager.setup()
    # Do the magic
    try:
        message_manager: MessageManager = MessageManager()
        yaml_manager: YAMLManager = YAMLManager(
            os.path.join(os.getcwd(), ".pre-commit-config.yaml"),
            config_file,
        )
        option_manager: OptionManager = OptionManager(
            dry_run,
            dry_run_mode,
            all_versions,
            warnings,
            exclude,
            keep,
            bleeding_edge,
            tag_prefix,
            set(
                repo["repo"].rsplit("/", 1)[-1].removesuffix(".git")
                for repo in yaml_manager.data["repos"]
                if is_git_remote(repo["repo"])
            ),
        )
        option_manager.validate(message_manager)
        repo_manager: RepoManager = RepoManager(
            yaml_manager.data["repos"],
            all_versions,
            jobs,
            option_manager.exclude,
            option_manager.keep,
            option_manager.bleeding_edge,
            option_manager.tag_prefix,
        )
        repo_manager.get_updates(message_manager)

        if warnings and message_manager.warning.messages:
            message_manager.output_messages(message_manager.warning)

        if verbose:
            for output in (
                message_manager.no_update,
                message_manager.exclude,
                message_manager.keep,
            ):
                if not output.messages:
                    continue
                message_manager.output_messages(output)

        if message_manager.update.messages:
            message_manager.output_messages(message_manager.update)

            if dry_run:
                dry_run_message: str = get_color("Changes detected", "red")
                if (
                    not option_manager.dry_run_mode
                    or option_manager.dry_run_mode == "strict"
                ):
                    raise click.ClickException(dry_run_message)

                click.echo(dry_run_message)
                return

            yaml_manager.data["repos"] = repo_manager.repos_data
            yaml_manager.dump()
            click.echo(get_color("Changes detected and applied", "green"))
            return

        click.echo(get_color("No changes detected", "green"))

    except Exception as ex:
        sys.exit(str(ex))

    finally:
        # Restore env variables
        env_manager.restore()


@click.command(context_settings=dict(help_option_names=["-h", "--help"]))
@click.option(
    "-c",
    "--config-file",
    type=click.Path(exists=True, dir_okay=False),
    required=False,
    show_default=True,
    default=None,
    help="Path to the configuration pyproject.toml file",
)
@click.option(
    "-d/-nd",
    "--dry-run/--no-dry-run",
    is_flag=True,
    show_default=True,
    default=False,
    help="Checks for the new versions without updating if enabled",
)
@click.option(
    "-dm",
    "--dry-run-mode",
    type=click.Choice(["strict", "warn"], case_sensitive=False),
    show_default=True,
    default="strict",
    help="Dry run mode: 'strict' prints the changes and exits, 'warn' only prints the changes",
)
@click.option(
    "-a/-na",
    "--all-versions/--no-all-versions",
    is_flag=True,
    show_default=True,
    default=False,
    help="Includes the alpha/beta versions when updating if enabled",
)
@click.option(
    "-v/-nv",
    "--verbose/--no-verbose",
    is_flag=True,
    show_default=True,
    default=False,
    help="Displays the complete update output if enabled",
)
@click.option(
    "-w/-nw",
    "--warnings/--no-warnings",
    is_flag=True,
    show_default=True,
    default=True,
    help="Displays warning messages if enabled",
)
@click.option(
    "-p/-np",
    "--preview/--no-preview",
    is_flag=True,
    show_default=True,
    default=False,
    help="Previews the cli option values by the overwriting order if enabled (disables the actual cli work!)",
)
@click.option(
    "-j",
    "--jobs",
    type=int,
    show_default=True,
    default=None,
    help="Maximum number of worker threads to be used for processing",
)
@click.option(
    "-e",
    "--exclude",
    multiple=True,
    type=RepoType(),
    default=(),
    help="Exclude specific repo(s) by the REPO_URL_TRIM - use '*' as a wildcard",
)
@click.option(
    "-k",
    "--keep",
    multiple=True,
    type=RepoType(),
    default=(),
    help="Keep the version of specific repo(s) by the REPO_URL_TRIM (still checks for the new versions) - use '*' as a wildcard",
)
@click.option(
    "-b",
    "--bleeding-edge",
    multiple=True,
    type=RepoType(),
    default=(),
    help="Get the latest version or commit of specific repo(s) by the REPO_URL_TRIM - use '*' as a wildcard",
)
@click.option(
    "-t",
    "--tag-prefix",
    multiple=True,
    type=(RepoType(), str),
    default=(),
    help="Set the custom tag prefix for the specific repo(s) by combining REPO_URL_TRIM with tag prefix value",
)
@click.version_option(None, "-V", "--version", package_name="pre-commit-update")
@click.pass_context
def cli(ctx: click.Context, **_: Any) -> None:
    defaults: dict = {p.name: p.default for p in ctx.command.params}

    if not defaults.get("dry_run"):
        defaults.pop("dry_run_mode", None)

    cmd_params: dict = get_passed_params(ctx)
    config_file: Optional[str] = __get_config_file(
        cmd_params.get("config_file") or defaults["config_file"]
    )
    toml_params: dict = get_toml_config(defaults, toml_path=config_file)
    toml_params.pop("config_file", None)
    toml_params.pop("yaml", None)
    final_params: dict = {**toml_params, **cmd_params, "config_file": config_file}

    if final_params.pop("preview", False):
        __preview(
            defaults=get_converted_dict_values(defaults),
            toml_params=get_converted_dict_values(toml_params),
            cmd_params=get_converted_dict_values(cmd_params),
            final_params=get_converted_dict_values(final_params),
        )
        return

    final_params.pop("version", None)
    __run(**final_params)


if __name__ == "__main__":
    cli()
