"""
Generator for `CLINamespace`.
"""

from __future__ import annotations

import sys
import inspect
import argparse
from typing import IO, Any, Iterable, get_type_hints


def generate_namespace_typing(
    argparser: argparse.ArgumentParser,
    name: str,
    *,
    type_aliases: Iterable[tuple[type[Any], str]] | None = None,
    default_aliases: Iterable[tuple[Any, str]] | None = None,
    description: str | None = None,
) -> str:
    """
    Generates a typed namespace class for a given argparser.

    Parameters
    ----------
    argparser: argparse.ArgumentParser
        the argparser whose namespace is to be produced
    name: str
        name of newly created namespace
    type_aliases: Iterable[tuple[type, str]], optional
        aliases Action.type to one type to an arbitrary string representation
    default_aliases: Iterable[tuple[Any, str]], optional
        aliases a Action.default value to an arbitrary string representation
    description:
        description of namespace In Numpydoc style, this corresponds to the
        `short summary<https://numpydoc.readthedocs.io/en/latest/format.html#short-summary>`_,
        `deprecation warning<https://numpydoc.readthedocs.io/en/latest/format.html#short-summary>`_,
        and `extended summary<https://numpydoc.readthedocs.io/en/latest/format.html#extended-summary>`_
        sections.


    Examples
    --------
    This was used to generate the :class:`CLINamespace`

    >>> import sys
    ... from companies_house_codegen.argument import CLIArgumentParser
    ... from tests.argument_utils import generate_namespace_typing
    ... print(generate_namespace_typing(
    ...     CLIArgumentParser(), 'CLINamespace',
    ...     default_aliases=[(sys.stdout, 'sys.stdout')],
    ...     description="Typings for namespace of `companies-house-codegen` "
    ...                 "command-line interface."
    ... ))
    """
    TAB = "    "

    description = description or ""

    req_param_docstrings: list[str] = []
    req_param_annotations: list[str] = []
    opt_param_docstrings: list[str] = []
    opt_param_annotations: list[str] = []

    for a in argparser._actions:
        if a.default == "==SUPPRESS==":
            continue

        param_name = a.dest
        tmp: type | Any = a.type
        if isinstance(a.type, type):
            pass
        elif isinstance(a.type, argparse.FileType):
            tmp = IO[str]
        elif callable(a.type):
            sig = inspect.signature(obj=tmp, eval_str=True)  # type:ignore[call-arg]
            if sig.return_annotation is not sig.empty:
                tmp = sig.return_annotation
        elif a.default is not None:
            tmp = type(a.default)
        elif a.const is not None:
            tmp = type(a.const)
        elif a.type is None:
            tmp = str
        else:
            raise ValueError(f"Found an invalid action: {a}")
        if type_aliases is not None:
            for k, v in type_aliases:
                if tmp == k or isinstance(tmp, k):
                    tmp = v
                    break
        type_hint = (
            getattr(tmp, "__name__", tmp) if not hasattr(tmp, "__args__") else str(tmp)
        )  # accounts for annotated types
        default = a.default
        if default_aliases is not None:
            for k, v in default_aliases:
                if k is default or k == default:
                    default = v
                    break
        param_docstring = a.help

        if a.required:
            req_param_annotations.append(f"{TAB}{param_name}: {type_hint}")
            req_param_docstrings.append(
                f"{TAB}{param_name}: {type_hint}\n{TAB * 2}{param_docstring}"
            )
        else:
            if default is None:
                opt_param_annotations.append(
                    f"{TAB}{param_name}: {type_hint} | None = None"
                )
            else:
                opt_param_annotations.append(
                    f"{TAB}{param_name}: {type_hint} = {default}"
                )

            opt_param_docstrings.append(
                f"{TAB}{param_name}: {type_hint}, optional\n{TAB * 2}{param_docstring}"
            )
    param_docstrings = req_param_docstrings + opt_param_docstrings
    param_annotations = req_param_annotations + opt_param_annotations

    newline = "\n"
    return f'''
class {name}(Namespace):
    """
    {description.replace(newline, newline + TAB)}

    Parameters
    ----------
{newline.join(param_docstrings)}

    Notes
    -----
    Generated using `companies_house_codegen.utils.generate_namespace_typing`

    See Also
    --------
    `companies_house_codegen.utils.generate_namespace_typing`
    """
{newline.join(param_annotations)}
'''


def dump_struct_signature(cls: type) -> str:
    """
    Used for testing the signature of :class:`companies_house_codegen.argument.CLINamespace`.
    """
    NEWLINE = "\n"
    NT = "\n    "

    def format_hint(t: Any) -> str:
        """formats a type hint"""
        if not hasattr(t, "__args__"):  # if not annotated type
            return str(getattr(t, "__name__", t))
        return str(t)

    mro = inspect.getmro(cls)
    parents = tuple(
        mro[i].__name__  # assume already imported from mro[i].__module__
        for i in range(len(mro))
        # if mro[i] is not already inherited
        if not any(issubclass(m, mro[i]) for m in mro[:i])
    )
    params = NT.join(
        f"{name}: {format_hint(type_hint)} = {getattr(cls, name)}"
        if hasattr(cls, name)
        else f"{name}: {type_hint}"
        for name, type_hint in get_type_hints(cls).items()
    )
    return f'''
class {cls.__name__}{parents}:
    """
    {NT.join((cls.__doc__ or "").split(NEWLINE))}
    """
    {params}
'''


if __name__ == "__main__":
    from companies_house_codegen.argument import CLIArgumentParser

    print( # noqa: T201
        generate_namespace_typing(  # noqa: T201
            CLIArgumentParser(),
            "CLINamespace",
            default_aliases=[(sys.stdout, "sys.stdout")],
            description="Typings for namespace of `companies-house-codegen` "
            "command-line interface.",
        )
    )
