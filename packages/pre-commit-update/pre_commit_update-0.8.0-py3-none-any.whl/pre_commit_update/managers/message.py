from dataclasses import dataclass

import click

from ..utils import get_color


@dataclass
class Icons:
    icon: str
    icon_alt: str
    text: str

    def get(self) -> tuple[str, str, str]:  # pragma: no cover
        return self.icon, self.icon_alt, self.text


@dataclass
class Config:
    color: str
    icons: Icons


@dataclass
class Message:
    text: str
    is_hash: bool = False
    is_bleeding_edge: bool = False
    is_tag_prefix: bool = False


@dataclass
class MessageQueue:
    messages: list[Message]
    config: Config


@dataclass
class MessageQueues:
    exclude: MessageQueue
    keep: MessageQueue
    no_update: MessageQueue
    update: MessageQueue
    warning: MessageQueue


class MessageManager:
    DEFAULT_VERSION: str = "/"

    def __init__(self) -> None:
        self.__bleeding_edge_icons: Icons = Icons(
            icon="↯", icon_alt="±", text="[bleeding-edge]"
        )
        self.__tag_prefix_icons: Icons = Icons(
            icon="⇉", icon_alt="»", text="[tag-prefix]"
        )
        self.__hash_icons: Icons = Icons(icon="⧣", icon_alt="≠", text="[hash]")
        self.__message_queues: MessageQueues = MessageQueues(
            exclude=MessageQueue(
                messages=[],
                config=Config(
                    color="magenta",
                    icons=Icons(icon="★", icon_alt="*", text="[exclude]"),
                ),
            ),
            keep=MessageQueue(
                messages=[],
                config=Config(
                    color="blue", icons=Icons(icon="◉", icon_alt="●", text="[keep]")
                ),
            ),
            no_update=MessageQueue(
                messages=[],
                config=Config(
                    color="green",
                    icons=Icons(icon="✔", icon_alt="√", text="[no-update]"),
                ),
            ),
            update=MessageQueue(
                messages=[],
                config=Config(
                    color="red", icons=Icons(icon="✘", icon_alt="×", text="[update]")
                ),
            ),
            warning=MessageQueue(
                messages=[],
                config=Config(
                    color="yellow",
                    icons=Icons(icon="⚠", icon_alt="▲", text="[warning]"),
                ),
            ),
        )

    @property
    def exclude(self) -> MessageQueue:
        return self.__message_queues.exclude

    @property
    def keep(self) -> MessageQueue:
        return self.__message_queues.keep

    @property
    def no_update(self) -> MessageQueue:
        return self.__message_queues.no_update

    @property
    def update(self) -> MessageQueue:
        return self.__message_queues.update

    @property
    def warning(self) -> MessageQueue:
        return self.__message_queues.warning

    def add_exclude_message(self, name: str, version: str) -> None:
        message: str = (
            f"{name} - {get_color(version or self.DEFAULT_VERSION, 'magenta')}"
        )
        self.__message_queues.exclude.messages.append(Message(text=message))

    def add_keep_message(
        self,
        name: str,
        current_version: str,
        latest_version: str,
        is_hash: bool = False,
        is_bleeding_edge: bool = False,
        is_tag_prefix: bool = False,
    ) -> None:
        current_version = current_version or self.DEFAULT_VERSION
        latest_version = latest_version or self.DEFAULT_VERSION
        text_message: str = (
            f"{current_version} -> {latest_version}"
            if current_version != latest_version
            else current_version
        )
        message: str = f"{name} - {get_color(text_message, 'blue')}"
        self.__message_queues.keep.messages.append(
            Message(
                text=message,
                is_hash=is_hash,
                is_bleeding_edge=is_bleeding_edge,
                is_tag_prefix=is_tag_prefix,
            )
        )

    def add_no_update_message(
        self,
        name: str,
        version: str,
        is_hash: bool = False,
        is_bleeding_edge: bool = False,
        is_tag_prefix: bool = False,
    ) -> None:
        message: str = f"{name} - {get_color(version or self.DEFAULT_VERSION, 'green')}"
        self.__message_queues.no_update.messages.append(
            Message(
                text=message,
                is_hash=is_hash,
                is_bleeding_edge=is_bleeding_edge,
                is_tag_prefix=is_tag_prefix,
            )
        )

    def add_update_message(
        self,
        name: str,
        current_version: str,
        latest_version: str,
        is_hash: bool = False,
        is_bleeding_edge: bool = False,
        is_tag_prefix: bool = False,
    ) -> None:
        current_version = current_version or self.DEFAULT_VERSION
        latest_version = latest_version or self.DEFAULT_VERSION
        message: str = (
            f"{name} - {get_color(current_version, 'yellow')} -> {get_color(latest_version, 'red')}"
        )
        self.__message_queues.update.messages.append(
            Message(
                text=message,
                is_hash=is_hash,
                is_bleeding_edge=is_bleeding_edge,
                is_tag_prefix=is_tag_prefix,
            )
        )

    def add_warning_message(self, name: str, reason: str) -> None:
        message: str = f"{name} - {get_color(reason, 'yellow')}"
        self.__message_queues.warning.messages.append(Message(text=message))

    def output_messages(self, message_queue: MessageQueue) -> None:  # pragma: no cover
        icons: tuple[str, str, str] = message_queue.config.icons.get()
        hash_icons: tuple[str, str, str] = self.__hash_icons.get()
        bleeding_edge_icons: tuple[str, str, str] = self.__bleeding_edge_icons.get()
        tag_prefix_icons: tuple[str, str, str] = self.__tag_prefix_icons.get()

        for message in message_queue.messages:
            additional_icons: list = []
            if message.is_hash:
                additional_icons.append(hash_icons)
            if message.is_bleeding_edge:
                additional_icons.append(bleeding_edge_icons)
            if message.is_tag_prefix:
                additional_icons.append(tag_prefix_icons)
            if additional_icons:
                additional_icons = list(zip(*additional_icons))
            else:
                additional_icons = [[""] * len(icons)]

            for icon, additional_icon in zip(icons, additional_icons):
                try:
                    icon_echo: str = get_color(
                        click.style(icon, bold=True), message_queue.config.color
                    )
                    additional_icon_echo: str = get_color(
                        click.style(" ".join(additional_icon), bold=True),
                        message_queue.config.color,
                    )
                    click.echo(f"{icon_echo} {message.text} {additional_icon_echo}")
                    break
                except UnicodeEncodeError:
                    continue
