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
Code formatting and generation
"""

from __future__ import annotations

import json
import logging
from string import Formatter
from typing import Any, cast
from pathlib import Path
from concurrent import futures
from collections import OrderedDict
from http.client import HTTPResponse
from urllib.parse import SplitResult, urlsplit
from urllib.request import Request, urlopen
from collections.abc import Mapping

from companies_house_codegen.types import (
    CHOASType,
    JSONSchema,
    SchemaFolder,
    URLSchemeType,
    RemoteJsonRefPathStr,
    validate_call,
)

# Local Library Imports
from companies_house_codegen.constants import (
    RE_URL,
    ALLOWED_TYPES,
    LOOPBACK_ADDR,
    COMPANIES_HOUSE_HOST,
    RE_REMOTE_JSON_REF_PATH,
    URLScheme,
)

logger = logging.getLogger(__name__)
"""
Logger for companies_house_codegen.codegen
"""
logger.setLevel(logging.DEBUG)


@validate_call
def reformat_swagger(
    swagger: JSONSchema,
    remote_path: RemoteJsonRefPathStr,
    host: str = COMPANIES_HOUSE_HOST,
    scheme: URLSchemeType = URLScheme.HTTPS,
) -> list[SplitResult]:
    """
    Reformats Companies House Swagger 2.0 specifications (in-place)
    and returns refs defined in the schema.

    Parameters
    ----------
    swagger: JsonSchema
        A Companies House Swagger schema
    remote_path: RemoteJsonRefPathStr
        Represents the part of a Remote JSON reference as described in
        `Using $ref | Swagger Docs <https://swagger.io/docs/specification/v3_0/using-ref>`_.
    host: str
        The host name that overrides the feedback adress.
        Default `'developer-specs.company-information.service.gov.uk'`.
    scheme: str
        The scheme that will be used for http request
        Default `'https'`.

    Notes
    -----
    This function acts in-place.

    Returns
    -------
    refs: SplitResult
        All references defined in the schema
    """
    if RE_REMOTE_JSON_REF_PATH.match(remote_path) is None:
        raise ValueError(
            f"Invalid remote path: '{remote_path}'.\n"
            f"Must match '{RE_REMOTE_JSON_REF_PATH.pattern}'"
        )
    if scheme not in URLScheme:
        raise ValueError(
            f"Invalid scheme: {scheme}. Must be one of the following: "
            f"{set(s.value for s in URLScheme)}"
        )

    logger.info(f"\t- Formatting/collecting refs for '{remote_path}'")

    def camel_to_snake(s: str) -> str:
        """
        Converts mixed/camel case strings to snake case.

        Credit: <https://stackoverflow.com/a/44969381>
        """
        return "".join("_" + c.lower() if c.isupper() else c for c in s).lstrip("_")

    if scheme not in URLScheme:
        raise ValueError(f"Invalid scheme: {scheme}")

    refs: list[SplitResult] = []

    def inner(
        swagger: OrderedDict[str, Any], url_path: str, *, _parent_key: str | None = None
    ) -> None:
        """
        Hide the true API from the client by putting it inside of a closure.

        NOTE: parses `swagger` using depth-first search traversal strategy
        """
        nonlocal camel_to_snake, host, refs, scheme

        # TODO: diff check reporting
        if "type" in swagger:
            tmp = swagger["type"]
            if tmp == "date":
                # NOTE: Companies House treats date as a type instead of a format
                # type<date> = type<string(format='date')>
                logger.debug('Converting `data` to `string(format="date")`')
                swagger["type"] = "string"
                swagger["format"] = "date"

            elif tmp == "list":
                # NOTE: Companies House aliases array to list
                # type<list> = type<array(item='string', collectionFormat='csv'|'multi')>
                logger.debug("Converting `list` to `array`")
                swagger["type"] = "array"
                swagger["items"] = OrderedDict({"type": "string"})
            elif tmp == "array" and "items" not in swagger:
                # ensure array has items
                swagger["items"] = OrderedDict({"type": "string"})
        if "$ref" in swagger:
            tmp = cast(str, swagger["$ref"])
            if tmp.startswith(LOOPBACK_ADDR):
                tmp = tmp[len(LOOPBACK_ADDR) :]
                if tmp.startswith(url_path):
                    # If True, converts references JSON remote references
                    # to local references whereever possible.
                    tmp = tmp[len(url_path) :]
                else:
                    i = tmp.find("#")
                    refs.append(
                        SplitResult(scheme, host, tmp if i == -1 else tmp[:i], "", "")
                    )
                    tmp = LOOPBACK_ADDR + tmp
            swagger["$ref"] = tmp
        if _parent_key == "parameters":
            if "paramType" in swagger:
                if "in" not in swagger:
                    swagger["in"] = swagger["paramType"]
                del swagger["paramType"]
            if "title" in swagger:
                # NOTE: sometimes Companies House aliases "name" to "title"
                swagger["name"] = swagger["title"]
                del swagger["title"]
            if "type" in swagger:
                # NOTE: sometimes Companies House treats booleans like strings
                tmp = swagger["type"] if swagger["type"] in ALLOWED_TYPES else "string"
                if tmp == "string" and "description" in swagger:
                    if all(i in swagger["description"] for i in ("true", "false")):
                        # infer type is boolean from description
                        tmp = "boolean"
                        if "enum" in swagger:
                            del swagger["enum"]
                swagger["type"] = tmp
        elif _parent_key == "paths":
            # NOTE: Companies House uses snake_case for its parameter names,
            #       however some path defintions use camelCase.
            logger.debug("\t\t- Formatting paths")
            for _ in range(len(swagger)):
                k, v = swagger.popitem(last=False)
                # NOTE: using string.Formatter.parse is 3x faster than using
                #       equivalent compiled regex patterns
                tmp = k
                k = "".join(
                    [
                        f"{literal_text}{
                            ''
                            if field_name is None
                            else '{' + camel_to_snake(field_name) + '}'
                        }"
                        for literal_text, field_name, _, _ in Formatter().parse(k)
                    ]
                )
                if tmp != k:
                    logger.debug(f"\t\t\t- Correcting case of path:'{tmp}' -> '{k}'")
                swagger[k] = v

        for k, v in swagger.items():
            if isinstance(v, list):
                for v_i in cast(list[Any], v):  # type:ignore[redundant-cast] # Pylance
                    if isinstance(v_i, OrderedDict):
                        inner(
                            swagger=cast(OrderedDict[str, Any], v_i),
                            url_path=url_path,
                            _parent_key=k,
                        )
            elif isinstance(v, OrderedDict):
                inner(
                    swagger=cast(OrderedDict[str, Any], v),
                    url_path=url_path,
                    _parent_key=k,
                )

    inner(swagger=swagger, url_path=remote_path)
    return refs


@validate_call
def download_folder(url: CHOASType | str, threaded: bool = True) -> SchemaFolder:
    """
    Downloads a Comapanies House Swagger specification folder.

    Parameters
    ----------
    url : str
        the URL to download the API.
    threaded : bool
        If True then will use multithreading to download the API.

        NOTE: On my machine this increased the speed of the download process by
                between 4 and 5 times.

    Returns
    -------
    folder : SchemaFolder
        A dictionary mapping Remote JSON Reference paths (as strings)
        to dictionariess representing JSON data.

    Also See
    --------
    reformat_swagger : Reformats Companies House Swagger 2.0 specifications (in-place)
        and returns refs defined in the schema.
    CHOAS: enum of available Swagger 2.0 specfications.

    Raises
    ------
    urllib.error.HTTPError
        If a bad HTTP request occurs
    """
    logger.info(f"Begin folder download for: {url}")
    if not RE_URL.match(url):
        raise ValueError(f"Invalid url: {url}")

    root = urlsplit(url)
    assert root.hostname is not None, "sanity check"
    folder: SchemaFolder = OrderedDict()

    def inner(url: SplitResult) -> None:
        nonlocal folder, threaded

        if url.path in folder:
            return
        folder[url.path] = OrderedDict()

        link = url.geturl()
        logger.info(f"\t- Fetching: {link}")
        resp: HTTPResponse = urlopen(link)
        obj: OrderedDict[str, Any] = json.loads(
            resp.read().decode(), object_pairs_hook=OrderedDict
        )
        refs = reformat_swagger(
            swagger=obj,
            remote_path=url.path,
            scheme=cast(URLSchemeType, root.scheme),
            host=cast(str, root.hostname),
        )
        folder[url.path] = obj
        refs = [ref for ref in refs if ref.path not in folder]
        if threaded:
            with futures.ThreadPoolExecutor() as executor:
                executor.map(inner, refs)
        else:
            for ref in refs:
                inner(ref)

    inner(root)
    logger.info("End folder download (success).")
    return folder


@validate_call
def zip_folder(
    folder: SchemaFolder,
    remote_path: RemoteJsonRefPathStr,
    #    keep_unused_defintions: bool = False,  # TODO: feature
) -> JSONSchema:
    """
    Zips/compresses/packages folder of Companies House Swagger specifications
    into a single Swagger specification.

    Parameters
    ----------
    folder : SchemaFolder
        A dictionary mapping Remote JSON Reference paths (as strings)
        to dictionaries reprenting JSON data.
    remote_path : RemoteJsonRefPathStr
        the path the where the main `swagger.json` file is stored with `folder`

    Returns
    -------
    swagger: JSONSchema
        A Companies House Swagger specification

    Notes
    -----
    Due to difference in parsing strategy this procedure will not yield the same result
    as what you would get by parsing the folder through version of the
    `swagger-codegen-cli <https://github.com/swagger-api/swagger-codegen>`_

    The differences are as follows
    * This procedure will cull all unused defintions
    * This procedure will not change the defintion of schemas objects
      produce the same result as if you
      - JSON schemas will be fully resolved


    See Also
    --------
    download_folder : downloads a Companies House Swagger specification folder
    swagger_converter : Converts Swagger schemas to OpenAPI
    """
    logger.info(
        f"Zipping folder:\n"
        + " \n  - ".join(
            f"'{k}' <-- root" if k == remote_path else f"'{k}'" for k in folder.keys()
        )
    )
    swagger = folder[remote_path].copy()
    swagger_defintions: OrderedDict[str, OrderedDict[str, Any]] = (
        swagger["definitions"].copy() if "defintions" in swagger else OrderedDict()
    )

    def fast_deepcopy(
        m: Mapping[str, Any], *, _scheme: OrderedDict[str, Any]
    ) -> OrderedDict[str, Any]:
        nonlocal folder, swagger_defintions

        od: OrderedDict[str, Any] = OrderedDict()
        for k, v in m.items():
            if isinstance(v, list):
                # NOTE: you will never see a list of lists
                od[k] = list()
                v = [
                    fast_deepcopy(cast(Mapping[str, Any], v_i), _scheme=_scheme)
                    if isinstance(v_i, Mapping)
                    else v_i
                    for v_i in cast(list[Any], v)  # type:ignore[redundant-cast]
                ]
            # handle JSON references
            elif k == "$ref":
                v = cast(str, v)
                ref = urlsplit(v)
                tmp = _scheme if ref.path == "" else folder[ref.path]
                _scheme = tmp
                if ref.fragment != "":
                    path_parts = ref.fragment.split("/")[1:]
                    if path_parts[0] == "definitions":
                        # update definitions
                        assert len(path_parts) == 2, "sanity check for defintions"
                        p = path_parts[1]
                        tmp = tmp["definitions"][p]
                        if p not in swagger_defintions:
                            swagger_defintions[p] = OrderedDict()  # placeholder
                            swagger_defintions[p] = fast_deepcopy(tmp, _scheme=_scheme)
                        if v.startswith(LOOPBACK_ADDR):
                            v = v[v.index("#") :]
                    else:
                        # Assumption: relates to paths
                        assert len(path_parts) == 1, "sanity check"
                        tmp = tmp[path_parts[0]]
                        v = fast_deepcopy(tmp, _scheme=_scheme)
                        od.update(v)
                        continue
                else:
                    if "definitions" in tmp:
                        tmp = tmp.copy()
                        del tmp["definitions"]
                    v = fast_deepcopy(tmp, _scheme=_scheme)
                    od.update(v)
                    continue
            elif isinstance(v, Mapping):
                od[k] = OrderedDict()
                v = fast_deepcopy(cast(Mapping[str, Any], v), _scheme=_scheme)
            od[k] = v
        return od

    ret = fast_deepcopy(swagger, _scheme=OrderedDict())
    ret["definitions"] = swagger_defintions
    return ret


@validate_call
def download_swagger(url: CHOASType, threaded: bool = True) -> JSONSchema:
    """
    Downloads a Companies House Swagger specification.

    Parameters
    ----------
    url : str
        the URL to download the API.
    threaded : bool
        If True then will use multithreading to download the API.

        NOTE: On my machine this increased the speed of the download process by
                between 4 and 5 times.

    Returns
    -------
    swagger: JSONSchema
        A Companies House Swagger specification

    Raises
    ------
    urllib.error.HTTPError
        If a bad HTTP request occurs

    See Also
    --------
    download_folder : Downloads a Comapanies House Swagger specification folder.
    zip_folder : Zips/compresses/packages a folder of Companies House Swagger
                 specifications into a single Swagger specification.

    Notes
    -----
    A composite function of `zip_folder` and `download_folder`.
    """
    return zip_folder(
        folder=download_folder(url=url, threaded=threaded),
        remote_path=urlsplit(url).path,
    )


@validate_call
def swagger_converter(swagger: JSONSchema) -> JSONSchema:
    """
    Converts a 1.x or 2.x Swagger definition to the OpenAPI 3.0.1 format.

    Parameters
    ----------
    swagger : JSONSchema
        A Companies House Swagger specification

    Returns
    -------
    openapi : JSONSchema
        A OpenAPI 3.0.1 specification.

    See Also
    --------
    zip_folder : Zips/compresses/packages folder of Companies House Swagger
                 specifications into a single Swagger specification.
    Swagger Converter : https://converter.swagger.io/api/openapi.json

    Notes
    -----
    This a wrapper for the
    `Swagger Converter<https://converter.swagger.io/api/openapi.json>`_ API

    Raises
    ------
    urllib.error.HTTPError
        If a bad HTTP request occurs
    ValueError
        if scheme is malformed
    NotImplementationError
        if attempting to pass a fragment of a scheme
    """
    logger.info("Converting Swagger definition to the OpenAPI 3.0.1 format.")
    if "swagger" not in swagger:
        # TODO: manual convesion
        # NOTE: fails due to localhost
        if "definitions" not in swagger:
            raise ValueError(f"bad scheme:\n{json.dumps(swagger, indent=2)}")
        raise NotImplementedError(
            "Denied: this method is unsafe for incomplete swagger schemes"
        )
    req = Request(
        "https://converter.swagger.io/api/convert",
        data=json.dumps(swagger).encode(),
        headers={"accept": "application/json", "Content-Type": "application/json"},
    )
    return cast(
        JSONSchema, json.loads(cast(HTTPResponse, urlopen(req)).read().decode())
    )


@validate_call
def download_openapi(url: CHOASType, threaded: bool = True) -> JSONSchema:
    """
    Convenient helper function for downloading a Companies House Swagger schema
    and converting it to

    Parameters
    ----------
    url : str
        the URL to download the API.
    threaded : bool
        If True then will use multithreading to download the API.

        NOTE: On my machine this increased the speed of the download process by
                between 4 and 5 times.

    Returns
    -------
    openapi : JSONSchema
        A OpenAPI 3.0.1 specification for a Companies House API.

    Raises
    ------
    urllib.error.HTTPError
        If a bad HTTP request occurs

    See Also
    --------
    swagger_converter : Converts a 1.x or 2.x Swagger definition
                        to the OpenAPI 3.0.1 format.
    download_swagger : Downloads a Companies House Swagger specification.

    Notes
    -----
    A composite function of `swagger_converter` and `download_swagger`.
    """
    return swagger_converter(download_swagger(url=url, threaded=threaded))


@validate_call
def save_folder(
    folder: SchemaFolder, out_dir: str | Path = ".", remote_base: str | None = None
) -> None:
    """
    Saves JSON specifications folder.

    Parameters
    ----------
    folder : SchemaFolder, Mapping[str, Schema], Mapping[str, OrderDict[str, Any]]
        A dictionary mapping Remote JSON Reference paths (as strings)
        to dicts representing JSON data.
    out_dir: StrPath
        the directory of the where the Specification is to be saved
    remote_base: str, optional
        A (HTTP/HTTPS/FTP/FTPS) uri that is defined by the folowing EBNF syntax:

        ``remote_base = scheme "://" host [ ":" port ] ["/" path]``

        where `scheme<https://datatracker.ietf.org/doc/html/rfc3986#section-3.1>`_,
        `host<https://datatracker.ietf.org/doc/html/rfc3986#section-3.2.2>`_,
        `port<https://datatracker.ietf.org/doc/html/rfc3986#section-3.2.3>`_,
        and `path<https://datatracker.ietf.org/doc/html/rfc3986#section-3.3>`_
        are syntax components defined in
        `RFC3986<https://tools.ietf.org/html/rfc3986>`_

        When specified all
        `remote references<https://swagger.io/docs/specification/v3_0/using-ref/>`
        are turned in
        `url references<https://swagger.io/docs/specification/v3_0/using-ref/>`
        using `remote_base` as the base url.

    See Also
    --------
    download_folder: Downloads a Comapanies House Swagger specification folder.

    Notes
    -----
    If a path is specified in `remote_base`, then it should match part of `out_dir`.
    This will not be validated, but it is a good practice.

    See Also
    --------
    RFC3986: https://www.rfc-editor.org/rfc/rfc3986

    Raises
    ------
    ValueError:
        * if `remote_base` does not conform to a valid RFC3986 URI.
        * if `remote_base` does not match the EBNF pattern
          ``scheme"://"host[":"path]["/"path]``
    """
    logger.info(f"Saving folder to {str(out_dir)}")
    if isinstance(out_dir, str):
        out_dir = Path(out_dir)
    if remote_base is not None:
        if not RE_URL.match(remote_base):
            raise ValueError(f"Invalid url: {remote_base}")
        tmp = urlsplit(remote_base)
        if tmp.query or tmp.fragment:
            raise ValueError(
                'Expected `scheme "://" host [ ":" port ] ["/" path]`:'
                f"got {remote_base}"
            )
    else:
        remote_base = ""
    logger.debug(f"'{LOOPBACK_ADDR}' will be substitued with '{remote_base}'")

    def ensure_directory(p: Path) -> None:
        """
        Ensures directory structure.

        Basically `mkdir -p DIR`
        """
        if not p.exists():
            ensure_directory(p.parent)
            p.mkdir(parents=False, exist_ok=False)
        elif not p.is_dir():
            raise NotADirectoryError(f"'{str(p)}' not a directory")

    if not out_dir.exists():
        raise FileNotFoundError(f"No such file or directory: '{str(out_dir)}'")
    if not out_dir.is_dir():
        raise NotADirectoryError(f"The directory name is invalid: '{str(out_dir)}'")

    for rel_path, content in folder.items():
        out_path = out_dir.joinpath(rel_path[1:])
        ensure_directory(out_path)
        with out_path.open("w") as f:
            logger.info(f"Writting to '{str(out_path)}'")
            f.write(json.dumps(content, indent=2).replace(LOOPBACK_ADDR, remote_base))


class Formatters:
    """
    List of format converters and linters for Companies House Swagger specifications.
    """

    __slots__ = ()

    reformat_swagger = reformat_swagger
    zip_folder = zip_folder
    swagger_converter = swagger_converter


class Downloaders:
    """
    List of available methods for downloading Companies House Swagger Specifications.
    """

    __slots__ = ()

    download_folder = download_folder
    download_swagger = download_openapi
    download_openapi = download_openapi


__all__ = [
    "reformat_swagger",
    "download_folder",
    "zip_folder",
    "download_swagger",
    "swagger_converter",
    "download_openapi",
    "save_folder",
    "Formatters",
    "Downloaders",
]
