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
Typings for codegen.
"""

from __future__ import annotations

from re import Pattern
from typing import Any, Union, Literal, TypeVar
from collections import OrderedDict
from collections.abc import Callable, MutableMapping
from typing_extensions import Annotated

from companies_house_codegen.argument import CLINamespace
from companies_house_codegen.constants import CHOAS, RE_REMOTE_JSON_REF_PATH, URLScheme

try:
    # optionally use pydantic
    from pydantic import StringConstraints, validate_call as _vc

    _tmp: StringConstraints | Pattern[str] = StringConstraints(
        pattern=RE_REMOTE_JSON_REF_PATH.pattern
    )
except ModuleNotFoundError:
    _tmp = RE_REMOTE_JSON_REF_PATH

AnyCallableT = TypeVar("AnyCallableT", bound=Callable[..., Any])


def validate_call(func: AnyCallableT) -> AnyCallableT:
    """
    If pydantic is installed, returns `pydantic.validate_call(func)`,
    a decorated wrapper around the function that validates the arguments.
    """
    if "_vc" in globals():
        return _vc(func)
    return func


CHOASType = Union[
    CHOAS,
    Literal[
        "https://developer-specs.company-information.service.gov.uk/companies-house-identity-service/reference",
        "https://developer-specs.company-information.service.gov.uk/companies-house-public-data-api/reference",
        "https://developer-specs.company-information.service.gov.uk/discrepancies/reference",
        "https://developer-specs.company-information.service.gov.uk/document-api/reference",
        "https://developer-specs.company-information.service.gov.uk/manipulate-company-data-api-filing/reference",
        "https://developer-specs.company-information.service.gov.uk/sandbox-test-data-generator-api/reference",
        "https://developer-specs.company-information.service.gov.uk/streaming-api/reference",
    ],
]
"""
A URL point to any 
**C**ompanies **H**ouse **O**pen**A**PI (Swagger 2.0) **S**pecfication.

See Also
--------
`CHOAS`: enum of available Swagger 2.0 specfications.
"""


RemoteJsonRefPathStr = Annotated[str, _tmp]
"""
Represents the part of a Remote JSON reference as described in 
`Using $ref | Swagger Docs <https://swagger.io/docs/specification/v3_0/using-ref>`_.
"""
del _tmp

JSONSchema = OrderedDict[str, Any]
"""Abstration of a JSON schema using."""

SchemaFolder = MutableMapping[RemoteJsonRefPathStr, JSONSchema]
"""
Abstration of a folder containing Schemas.

A dictionary mapping Remote JSON Reference file paths (as strings)
to dicts representing JSON data.
"""

URLSchemeType = Union[URLScheme, Literal["http", "https", "ftp", "ftps"]]
"""
A valid url scheme supported by codegen.
"""

__all__ = [
    "validate_call",
    "CHOASType",
    "CLINamespace",
    "RemoteJsonRefPathStr",
    "JSONSchema",
    "SchemaFolder",
    "URLSchemeType",
]
