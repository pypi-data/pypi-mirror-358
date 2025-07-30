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

from __future__ import annotations

import sys
import json
import logging
import warnings
import traceback
from typing import IO, Any, cast
from pathlib import Path
from collections import OrderedDict
from urllib.parse import urlsplit
from collections.abc import Sequence

import yaml
from yaml.cyaml import CDumper

from companies_house_codegen.utils import create_server, mapping_representer
from companies_house_codegen.codegen import (
    zip_folder,
    save_folder,
    download_folder,
    swagger_converter,
)
from companies_house_codegen.argument import CLINamespace, CLIArgumentParser
from companies_house_codegen.constants import LOOPBACK_ADDR, ExitCode

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

warnings.warn(
    f"{__name__} is pre-release software and not ready for production use."
    " Expect to encounter bugs, missing features, and minor errors.",
    stacklevel=2,
)


def void_main(args: Sequence[str] | None = None) -> None:
    """
    The command-line interface for `companies_house_codegen` programme.

    Parameters
    ----------
    args: Sequence[str], optional
        sequence of command line arguements. If not passed, gets commandline arguments
        from `sys.argv`
    """

    def is_json(io: IO[Any]) -> bool:
        return Path(io.name).suffix == ".json"

    parser = CLIArgumentParser()
    cli_args = cast(CLINamespace, parser.parse_args(args))
    if not cli_args.silent:
        if cli_args.verbose:
            logging.basicConfig(
                level=logging.DEBUG,
                format="%(levelname)s %(asctime)s %(funcName)s line%(lineno)d: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
                stream=sys.stderr,
            )
        else:
            logging.basicConfig(
                level=logging.INFO,
                format="%(levelname)s: %(message)s",
                stream=sys.stderr,
            )
        if cli_args.threaded:
            logger.warning("multi-threading enabled")

    remote_path = urlsplit(cli_args.input).path
    folder = download_folder(cli_args.input, threaded=cli_args.threaded)
    m = zip_folder(folder=folder, remote_path=remote_path)
    if cli_args.openapi:
        m = swagger_converter(m)
    logger.info(f"Writting to {cli_args.zip.name}")
    if is_json(cli_args.zip):
        cli_args.zip.write(json.dumps(m, indent=2, sort_keys=False))
    else:
        CDumper.add_representer(OrderedDict, mapping_representer)
        yaml.dump(m, cli_args.zip, indent=2, sort_keys=False, Dumper=CDumper)
    if cli_args.extract:
        save_folder(folder, out_dir=cli_args.extract, remote_base=LOOPBACK_ADDR)
    if cli_args.serve:
        create_server(cli_args.serve)


def main(args: Sequence[str] | None = None) -> ExitCode:
    """
    The command-line interface for `companies_house_codegen` programme.

    Parameters
    ----------
    args: Sequence[str], optional
        sequence of command line arguements. If not passed, gets commandline arguments
        from `sys.argv`

    Returns
    -------
    exit_code: int
        An integer representing how the programme exited.

    See Also
    --------
    `ExitCode`: Exit code for the main function
    """
    try:
        void_main(args=args)
    except KeyboardInterrupt:
        print(traceback.format_exc(), file=sys.stderr)  # noqa: T201
        return ExitCode.KEYBOARD_INTERRUPT
    except Exception:
        print(traceback.format_exc(), file=sys.stderr)  # noqa: T201
        return ExitCode.ERROR
    return ExitCode.SUCCESS


__all__ = ["void_main", "main"]

if __name__ == "__main__":
    sys.exit(main())
