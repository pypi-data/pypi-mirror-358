# Coding Standards

## PEP 8

This project follows a superset of the
[**PEP 8 – Style Guide for Python Code**](https://peps.python.org/pep-0008/) (PEP 8).

## Strong Typing

Strong typing is prefered wherever possible. Prefer using `Duration` instead of `int`, etc.

## Explicit Types

All functions must be fully annotated with [Type Hints](https://peps.python.org/pep-0484/).

All classes must be fully annotated with [Variable Annotations](https://peps.python.org/pep-0526/).

May be used wherever `typing.cast` types are ambiguious.

## Explicity and namespace imports

Never use wildcard imports. Either import the module or the items you require from
the module.

## Compatibility

All code must be compatible with Python 3.8.

### Defered/Postponed Evaluation of Annotations

In the case that defered/postponed evaluation of annotations is required
(e.g. when using type annotations that reference type defined later in the file),
then use the
[annotations](https://docs.python.org/3/library/__future__.html)
[future statement](https://docs.python.org/3/reference/simple_stmts.html#future)

```python
from __future__ from annotations
```

> [!NOTE]
> This should be the only statement you may need to use.

### Union Types

Unions should be written using the syntax defined in
[PEP 604 – Allow writing union types as `X | Y`](https://peps.python.org/pep-0604/).

In the case the unions types are required, use the
[annotations](https://docs.python.org/3/library/__future__.html)
[future statement](https://docs.python.org/3/reference/simple_stmts.html#future)

```python
from __future__ from annotations
```

## Logging

For logging the following rules apply:

0. Use `logging` module for logging.
1. Loggers must be declared at the top of the file after imports and global constants.
2. The name of each logger must be `__name__`.
3. Log level of all named loggers must be `logging.DEBUG`.
4. Never log using the root logger.
5. Do not share loggers between modules.
6. Loggers stream must be set to `stdout`;
   they must only stream to the `stderr` (default) stream.

Here is an example of a logger in a module file.

```python
# Correct
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.debug(f"Created logger for {__name__}")
```

## Documentation

### Python Docstrings

All functions, classes and constants (class and global) must be documented
using docstrings as standardized in [PEP 287](https://www.python.org/dev/peps/pep-0287).

Docstring must follow the [numpydoc](https://numpydoc.readthedocs.io/en/latest/)
standards which uses [re-structured text (reST)](http://docutils.sourceforge.net/rst.html)
syntax.

#### Class Variables

In the [Style guide for numpydoc](https://numpydoc.readthedocs.io/en/latest/format.html)
there is an ambiguity in how static/class variables are to be documented.

For class variables, use the convention for
[Documenting constants](https://numpydoc.readthedocs.io/en/latest/format.html#documenting-constants)

### File Documentation

Documentation files must be written in the `/docs/` folder.

In Python the recommended file format for documentation is reST. However,
due to the ubiquity of the Markdown format, it makes more logical sense
to Markdown instead. Thus, all file documentation will be written in Markdown.

[MkDocs](https://www.mkdocs.org/) using the [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/) theme, and the [mkdocstrings](https://mkdocstrings.github.io/) extension.

> [!NOTE]
> I initially considered using between [Sphinx](https://www.sphinx-doc.org/en/master/)
> with the [MyST Parser](https://myst-parser.readthedocs.io/en/latest/intro.html) extension,
> and the [Furo](https://pradyunsg.me/furo/) theme; however I decided to go with MkDoc
> due to how popular and recogizable it has become.

## Static Analysis

[mypy](https://mypy.readthedocs.io/en/stable/) will be used to perform static analysis.

> [!TIP]
> If you wish, static analysis maybe performed using
> [`ty`](https://github.com/astral-sh/ty) or [`pyrefly`](https://pyrefly.org/).
> Both these tools also have come with a language server, making them convient
> to use in an editor/IDE. However, it is worth noting that these tools is still
> in Alpha and may have some bugs so rely primarily on `mypy`.

## Formatting

Use `ruff` for formatting.
