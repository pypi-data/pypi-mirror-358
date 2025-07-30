# The MIT License(MIT)
#
# Copyright(c) 2025 Munyaradzi Murape
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files(the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and / or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""
The argument parser used by __main__.py
"""

from __future__ import annotations

import sys
import typing
import argparse
from pathlib import Path
from dataclasses import dataclass
from importlib.metadata import version

from companies_house_codegen.utils import FileTypeExtension
from companies_house_codegen.constants import (
    CHOAS,
    LOCALHOST_IP,
    RE_SERVER_ADDR,
    COMPANIES_HOUSE_PORT,
)


@dataclass
class CLINamespace(argparse.Namespace):
    """
    Typings for namespace of `companies-house-codegen` command-line interface.

    Parameters
    ----------
    input: str
        URL of a Companies House Swagger Specification from the Companies House Developer's API Suite. See: companies_house_codegen.constants.CHOAS or https://developer-specs.company-information.service.gov.uk for more info.
    extract: Path, optional
        When specified, save specification files as to a directory.
    zip: typing.IO[str], optional
        Output as single file. Outputs as to stdout otherwise
    openapi: bool, optional
        Convert Swagger specification to OpenAPI.
    serve: tuple[str, int], optional
        When specified, creates a local HTTP server. By default, serves on 127.0.0.1:10000. This can be overidden by passing an argument argument <IP:PORT> is passed
    silent: bool, optional
        Stop emitting all non-critical output. Error messages will still be emitted (which can silenced by 2>/dev/null).
    threaded: bool, optional
        Download syncronously on a single thread. By default, downloads syncronously using multithreading. Useful for debugging.
    verbose: bool, optional
        Use verbose debug logging

    Notes
    -----
    Generated using `companies_house_codegen.utils.generate_namespace_typing`

    See Also
    --------
    `companies_house_codegen.utils.generate_namespace_typing`
    """

    input: str
    extract: Path | None = None
    zip: typing.IO[str] = sys.stdout
    openapi: bool = False
    serve: tuple[str, int] | None = None
    silent: bool = False
    threaded: bool = True
    verbose: bool = False


class CLIArgumentParser(argparse.ArgumentParser):
    """
    Argument parser for commandline interface.
    """

    def __init__(self) -> None:
        super().__init__(
            prog="companies-house-codegen",
            usage="companies-house-codegen [OPTIONS]",
            description="Generate, format and host OpenAPI specifications "
            "and for Companies House",
        )
        self.add_argument(
            "--version",
            "-V",
            action="version",
            version=f"%(prog)s, {version(self.prog)}",
            help="Show version and exit.",
        )
        input_options = self.add_argument_group(title="Input options")
        output_options = self.add_argument_group(title="Output and formatting options")
        debug_options = self.add_argument_group(title="Debugging options")

        input_options.add_argument(
            "--input",
            "-i",
            metavar="URL",
            choices=frozenset((spec.value for spec in CHOAS)),
            type=str,
            required=True,
            help="URL of a Companies House Swagger Specification "
            "from the Companies House Developer's API Suite. "
            "See: companies_house_codegen.constants.CHOAS "
            "or https://developer-specs.company-information.service.gov.uk "
            "for more info.",
        )

        # output options
        output_options.add_argument(
            "--extract",
            "-e",
            metavar="DIR",
            type=Path,
            help="When specified, save specification files as to a directory.",
        )
        output_options.add_argument(
            "--zip",
            "-z",
            metavar="FILE",
            help="Output as single file. Outputs as to stdout otherwise",
            type=FileTypeExtension(mode="w", extensions=["json", "yaml", "yml"]),
            default=sys.stdout,
        )
        output_options.add_argument(
            "--openapi",
            action="store_true",
            help="Convert Swagger specification to OpenAPI.",
        )

        def parse_server_addr(string: str) -> tuple[str, int]:
            if RE_SERVER_ADDR.match(string) is None:
                raise ValueError(f"Expected 'IP:PORT', got '{string}'")
            ip, port = string.split(":")
            return (ip, int(port))

        output_options.add_argument(
            "--serve",
            nargs="?",
            metavar="IP:PORT",
            type=parse_server_addr,
            const=({LOCALHOST_IP}, {COMPANIES_HOUSE_PORT}),
            help="When specified, creates a local HTTP server. By default, serves on "
            f"{LOCALHOST_IP}:{COMPANIES_HOUSE_PORT}. "
            "This can be overidden by passing an argument argument <IP:PORT> is passed",
        )

        # TODO: implement
        # output_options.add_argument(
        #    '--no-format',
        #    action="store_false",
        #    help="No formatting"
        # )

        # debug options
        debug_options.add_argument(
            "--silent",
            "-s",
            action="store_true",
            help="Stop emitting all non-critical output. Error messages will "
            "still be emitted (which can silenced by 2>/dev/null).",
        )
        debug_options.add_argument(
            "--single-threaded",
            action="store_false",
            dest="threaded",
            help="Download syncronously on a single thread. "
            "By default, downloads syncronously using multithreading. "
            "Useful for debugging.",
        )
        debug_options.add_argument(
            "--verbose", "-v", action="store_true", help="Use verbose debug logging"
        )


__all__ = ["CLINamespace", "CLIArgumentParser"]
