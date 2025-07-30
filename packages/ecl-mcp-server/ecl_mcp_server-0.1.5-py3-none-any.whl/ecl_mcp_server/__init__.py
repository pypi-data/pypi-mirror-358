#  Copyright © 2025 China Mobile (SuZhou) Software Technology Co.,Ltd
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
import datetime
import logging
import os
import sys
from pathlib import Path
from typing import List, Literal, Optional

import click
import typer

from ecl_mcp_server import constants, context
from ecl_mcp_server.i18n import _

cli = typer.Typer()

_Transport_Type = Literal["stdio", "sse", "streamable-http"]


def _get_handlers(log_filepath: Optional[str] = None):
    handlers: list[logging.Handler] = [logging.StreamHandler(stream=sys.stderr)]

    def _add_file_handler():
        path = (
            Path(log_filepath)
            if log_filepath
            else Path(constants.default_server_log_filepath())
        )
        if path.exists():
            if path.is_dir():
                print(
                    f"{datetime.datetime.now()} [ecl-mcp-server] {path} is a directory. can't log to file",
                    file=sys.stderr,
                )
                return
        else:
            try:
                path.parent.mkdir(parents=True, exist_ok=True)
            except Exception as e:
                print(
                    f"{datetime.datetime.now()} [ecl-mcp-server] Failed to create {path}: {e}",
                    file=sys.stderr,
                )
                return
        handlers.append(logging.FileHandler(path))
        print(
            f"{datetime.datetime.now()} [ecl-mcp-server] log file at {path}",
            file=sys.stderr,
        )

    _add_file_handler()

    return handlers


def setup_logging(level, log_filepath: Optional[str] = None):
    """Setup logging"""
    handlers = _get_handlers(log_filepath)

    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%d-%m %I:%M:%S",
        handlers=handlers,
    )


def _validate_module(value: List[str]) -> List[str]:
    modules = set(value)
    if "all" in modules and len(modules) > 1:
        click.echo(
            _("Warning: DO NOT NEED supply other modules if 'all' provided"),
            err=True,
            color=True,
            nl=True,
        )
    return value


def _set_timezone(timezone_param: Optional[str]):
    from datetime import timedelta, timezone

    import pytz

    if timezone_param is None:
        return timezone(timedelta(hours=8))

    try:
        offset = float(timezone_param)
    except Exception as e:
        _ = e
        try:
            return pytz.timezone(timezone_param)
        except Exception as err:
            raise ValueError(f"Unknown timezone: {timezone_param}") from err
    try:
        return timezone(timedelta(hours=offset))
    except Exception as e:
        raise ValueError(f"Unknown offset: {timezone_param}") from e


@cli.command()
def _mcp_server(
    access_key: str = typer.Argument(
        ...,
        envvar=constants.ENV_JOURNAL_AK_KEY,
        help=_(
            "The AccessKey required for the China Mobile Cloud API gateway. "
            "For more information: https://ecloud.10086.cn/op-help-center/doc/article/42472 "
            "You can set the environment variable '{}' "
            "instead of manually entering this parameter."
        ).format(constants.ENV_JOURNAL_AK_KEY),
    ),
    secret_key: str = typer.Argument(
        ...,
        envvar=constants.ENV_JOURNAL_SK_KEY,
        help=_(
            "The SecretKey required for the China Mobile Cloud API gateway. "
            "For more information: https://ecloud.10086.cn/op-help-center/doc/article/42472 "
            "You can set the environment variable '{}' "
            "instead of manually entering this parameter."
        ).format(constants.ENV_JOURNAL_SK_KEY),
    ),
    port: int = typer.Option(8000, help=_("Server listening port")),
    transport: _Transport_Type = typer.Option(
        "stdio",
        help=_('Transport protocol to use ("stdio", "sse", or "streamable-http")'),
        click_type=click.Choice(["stdio", "sse", "streamable-http"]),
    ),
    log_level: Optional[str] = typer.Option(
        "INFO",
        help=_("Logging level"),
        click_type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]),
    ),
    preferred_pool_id: Optional[str] = typer.Option(
        None,
        envvar=constants.ENV_JOURNAL_PREFERRED_POOL_ID,
        help=_(
            "The default resource pool id used when accessing ecl-mcp-server. "
            "Some requests require a clear specification of the resource pool id, "
            "otherwise it will be requested to be specified in the conversation."
        ),
    ),
    module: List[str] = typer.Option(
        ["default"],
        "--module",
        "-m",
        help=_(
            "What tools should be loaded. "
            "After specifying the module, only partial tool information is loaded to ecl-mcp-server. "
            "This parameter can be entered multiple times to load multiple modules: -m default -m alarm"
        ),
        callback=_validate_module,
        click_type=click.Choice(constants.MODULES),
    ),
    timezone: Optional[str] = typer.Option(
        "8",
        "--timezone",
        "-tz",
        help=_(
            "Configure time zone. It can be a float number that represents an offset (such as 8 or -5.5) "
            "or a time zone name (such as Asia/Shanghai)"
        ),
    ),
    log_file: Optional[str] = typer.Option(
        None,
        "--log-file",
        help=_(
            "Log file to write logs to. "
            "If not specified, logs will be written to '~/.mcp/logs/ecl_mcp_server_${YYYYmmdd}.log'"
        ),
    ),
    pool_map_file: Optional[str] = typer.Option(
        None,
        "--pool-map-file",
        help=_("A file containing a json string of resource pool."),
    ),
    http_timeout: float = typer.Option(
        constants.HTTP_TIMEOUT,
        "--http-timeout",
        help=_("The timeout(seconds) for HTTP requests."),
    ),
    show_modules: bool = typer.Option(
        False,
        "--show-modules",
        help=_("Show all available modules and their tools, and exit"),
    ),
):
    """ecl mcp server command"""
    from ecl_mcp_server import core

    if show_modules:
        core.print_modules()
        return

    setup_logging(log_level, log_file)

    if pool_map_file:
        from ecl_mcp_server.pool import load_pool_map_file

        load_pool_map_file(Path(pool_map_file))

    os.environ[constants.ENV_JOURNAL_AK_KEY] = access_key
    os.environ[constants.ENV_JOURNAL_SK_KEY] = secret_key
    context.preferredPoolId = preferred_pool_id
    context.http_timeout = http_timeout

    # Configure timezone
    context.tz = _set_timezone(timezone)

    mcp = core.Module().load(module)
    mcp.settings.port = port
    mcp.settings.debug = True
    mcp.settings.log_level = log_level

    logging.debug("mcp.settings: %s", mcp.settings)

    mcp.run(transport=transport)


def main():  # pragma: no cover
    """Main entry point for ecl-mcp-server"""
    cli()
