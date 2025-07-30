# SPDX-FileCopyrightText: 2025-present Ofek Lev <oss@ofek.dev>
# SPDX-License-Identifier: MIT
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal

if TYPE_CHECKING:
    import re
    from collections.abc import Iterator

    from pycli_mcp.metadata.interface import CommandMetadata


class CommandQuery:
    """
    A wrapper around a root command object that influences the collection behavior. Example usage:

    ```python
    from pycli_mcp import CommandMCPServer, CommandQuery

    from mypkg.cli import cmd

    # Only expose the `foo` subcommand
    query = CommandQuery(cmd, include=r"^foo$")
    server = CommandMCPServer(commands=[query])
    server.run()
    ```

    Parameters:
        command: The command to inspect.
        aggregate: The level of aggregation to use.
        name: The expected name of the root command.
        include: A regular expression to include in the query.
        exclude: A regular expression to exclude in the query.
        strict_types: Whether to error on unknown types.
    """

    __slots__ = ("__aggregate", "__command", "__exclude", "__include", "__name", "__strict_types")

    def __init__(
        self,
        command: Any,
        *,
        aggregate: Literal["root", "group", "none"] | None = None,
        name: str | None = None,
        include: str | re.Pattern | None = None,
        exclude: str | re.Pattern | None = None,
        strict_types: bool = False,
    ) -> None:
        self.__command = command
        self.__aggregate = aggregate
        self.__name = name
        self.__include = include
        self.__exclude = exclude
        self.__strict_types = strict_types

    def __iter__(self) -> Iterator[CommandMetadata]:
        yield from walk_commands(
            self.__command,
            aggregate=self.__aggregate,
            name=self.__name,
            include=self.__include,
            exclude=self.__exclude,
            strict_types=self.__strict_types,
        )


def walk_commands(
    command: Any,
    *,
    aggregate: Literal["root", "group", "none"] | None = None,
    name: str | None = None,
    include: str | re.Pattern | None = None,
    exclude: str | re.Pattern | None = None,
    strict_types: bool = False,
) -> Iterator[CommandMetadata]:
    if aggregate is None:
        aggregate = "root"

    # Click
    if hasattr(command, "context_class"):
        from pycli_mcp.metadata.types.click import walk_commands

        yield from walk_commands(
            command,
            aggregate=aggregate,
            name=name,
            include=include,
            exclude=exclude,
            strict_types=strict_types,
        )
    else:
        msg = f"Unsupported command type: {type(command)}"
        raise NotImplementedError(msg)
