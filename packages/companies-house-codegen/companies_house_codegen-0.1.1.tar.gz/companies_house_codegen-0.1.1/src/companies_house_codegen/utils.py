# The MIT License(MIT)
#
# Copyright (c) 2025 Munyaradzi Murape
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
Utilities for codegen.
"""

from __future__ import annotations

import logging
import argparse
import http.server
from typing import IO, Any, TypeVar, Iterable
from pathlib import Path
from collections.abc import Mapping

from yaml import MappingNode
from yaml.representer import SafeRepresenter

R = TypeVar("R")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class FileTypeExtension(argparse.FileType):
    """
    Extension `argparse.FileType` that adds checking for file extensions.
    """

    def __init__(
        self,
        mode: str = "r",
        bufsize: int = -1,
        encoding: str | None = None,
        errors: str | None = None,
        extensions: Iterable[str] | None = None,
    ) -> None:
        super().__init__(mode, bufsize, encoding, errors)
        self._extensions = extensions

    def __call__(self, string: str) -> IO[Any]:
        f = super().__call__(string)

        if (
            self._extensions is not None
            and Path(f.name).suffix[1:] not in self._extensions
        ):
            raise argparse.ArgumentTypeError(
                f"Expected file with extension: {{{','.join(self._extensions)}}}."
                f"Found: {f.name}"
            )
        return f


def create_server(server_address: tuple[str, int]) -> None:
    """
    Helper to create an HTTP server
    """
    web_server = http.server.HTTPServer(
        server_address, http.server.SimpleHTTPRequestHandler
    )
    try:
        logger.info(f"Starting server on {server_address[0]}:{server_address[1]}")
        web_server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt recieved, exiting.")


def mapping_representer(
    dumper: SafeRepresenter, data: Mapping[Any, Any]
) -> MappingNode:
    """
    Helper to represent any Mapping as yaml.

    Paramaters
    ----------
    dumper: SafeRepresenter
        A yaml dumper using the `yaml.representer.SafeRepresenter` mixin
    data:
        the `collections.abc.Mapping` object to be represented

    Notes
    -----
    Useful for represnting `collection.OrderedDict` objects.

    Returns
    -------
    MappingNode
        a `yaml.MappingNode` which is used by dumper to represent a mapping
    """
    return dumper.represent_dict(data.items())


__all__ = [
    "create_server",
    "mapping_representer",
]
