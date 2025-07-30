import asyncio
import re
import sys
from functools import wraps
from typing import Dict, Sequence

import click
from click import Group
from dynamic_imports import import_module_attr
from taskflows import logger
from taskflows.common import get_shutdown_handler


def parse_str_kwargs(kwargs: Sequence[str]) -> Dict[str, float | str]:
    """Parses string in the form 'key=value'"""
    kwargs_dict = {}
    for pair in kwargs:
        if "=" not in pair:
            raise click.BadParameter(f"Invalid key=value pair: {pair}")
        key, value = pair.split("=", 1)
        if re.match(r"(\d+(\.\d+)?)$", value):
            value = float(value)
        kwargs_dict[key] = value
    return kwargs_dict


def async_entrypoint(blocking: bool = False, shutdown_on_exception: bool = True):
    def decorator(f):
        loop = asyncio.get_event_loop_policy().get_event_loop()
        sdh = get_shutdown_handler()
        sdh.shutdown_on_exception = shutdown_on_exception

        async def async_entrypoint_async(*args, **kwargs):
            logger.info("Running main task: %s", f)
            try:
                await f(*args, **kwargs)
                if blocking:
                    await sdh.shutdown(0)
            except Exception as err:
                logger.exception("Error running main task: %s", err)
                await sdh.shutdown(1)

        @wraps(f)
        def wrapper(*args, **kwargs):
            task = loop.create_task(async_entrypoint_async(*args, **kwargs))
            if blocking:
                loop.run_until_complete(task)
            else:
                loop.run_forever()

        return wrapper

    return decorator


class CLIGroup:
    """Combine and optionally lazy load multiple click CLIs."""
    def __init__(self):
        self.cli = Group()
        self.commands = {}

    def add_sub_cli(self, cli: Group):
        self.cli.add_command(cli)

    def add_lazy_sub_cli(self, name: str, cli_module: str, cli_variable: str):
        self.commands[name] = lambda: import_module_attr(cli_module, cli_variable)

    def run(self):
        if len(sys.argv) > 1 and (cmd_name := sys.argv[1]) in self.commands:
            # construct sub-command only as needed.
            self.cli.add_command(self.commands[cmd_name](), name=cmd_name)
        else:
            # For user can list all sub-commands.
            for cmd_name, cmd_importer in self.commands.items():
                self.cli.add_command(cmd_importer(), name=cmd_name)
        self.cli()
        

