# Contributing

Contributions are welcome and greatly appreciated. These are the instructions
you need to follow if you want to submit a pull request.

## Code of Conduct

Read and comply with this project's [Code of Conduct](CODE_OF_CONDUCT.md).

## Environment Setup

0. [Install Python](docs/developement/install-python.md) - if you have not already.
1. Fork and git clone this repository run:

    ```shell
    cd companies-house-codegen # change directory to this repository
    ```

2. (recommeded) [Create and activate virtual environment](docs/developement/virtual-environments.md)
3. Install package with `dev` extras (dependencies) by running `pip install ".[dev]"`
   or whatever equivalent your chosen package manager uses.

## Coding style

Before writting a single line of code, we recommed that you read and comply
with this project's [Coding Standards](docs/developement/coding-standards.md).

## Code Quality

Before committing you work you must perform the following code steps
to ensure code quality.

0. Change directory to root of this repository.
1. Lint and format code using [`ruff`](https://astral.sh/ruff).
    1. Run `ruff check .` to run lint check.
    2. If the check fails, try `ruff check . --fix` or `ruff format .` to reformat code,
      then run `ruff check .` again.
    3. If the check still fails, then you will have to make corrections mannually.
2. Perform static analysis using [`mypy`](https://mypy.readthedocs.io/en/stable/).
    1. Run `mypy .`.
    2. If `mypy` returns any errors you must correct them.

> [!NOTE]
> If your pull request fails the
> [`mypy`](https://github.com/MMurape/companies-house-codegen/actions/workflows/mypy.yml)
> or [`ruff`](https://github.com/MMurape/companies-house-codegen/actions/workflows/ruff.yml)
> [CI](https://en.wikipedia.org/wiki/Continuous_integration) pipelines on Github
> then it may be rejected.
