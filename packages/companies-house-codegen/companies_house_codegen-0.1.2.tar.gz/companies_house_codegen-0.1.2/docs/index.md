
# companies-house-codegen

[![PyPI Version](https://img.shields.io/pypi/v/companies-house-codegen)](https://pypi.org/p/comapanies-house-codegen)
[![mkdocs](https://github.com/mmurape/companies-house-codegen/workflows/mkdocs/badge.svg)](https://mmurape.github.io/companies-house-codegen/)
[![ruff](https://github.com/mmurape/companies-house-codegen/workflows/ruff/badge.svg)](https://github.com/MMurape/companies-house-codegen/actions)
[![mypy](https://github.com/mmurape/companies-house-codegen/workflows/mypy/badge.svg)](https://github.com/MMurape/companies-house-codegen/actions)

A simple but powerful toolkit for downloading, compressing and formatting
Companies House OpenAPI (Swagger 2.0) specifications.

## Introduction

[Companies House](https://companieshouse.gov.uk) is an executive agency of the [Department for Business and Trade](https://gov.uk/dbt), a department of the British Government. This official UK agency is responsible for incorperating and dissolving companies, and maintaining a register of information of limited companies (and some other companies) under the [Companies Act](https://www.legislation.gov.uk/ukpga/2006/46/contents) and related legislation to be made available for public access.

Companies House hosts a [JSON](http://www.json.org/) [REST API](https://restfulapi.net/) called the [Companies House API](https://developer.company-information.service.gov.uk/overview), which makes it possible for software developers to create application to retrieve information from Companies House's database (e.g. searching and retrieving public company data), as well as, interact with Companies House's database (e.g. manipulating company information, givem you have authority to do so). The full documentation for Companies House API can be found at the [Companies House Developer Hub](https://developer.company-information.service.gov.uk/).

Unfortunately, the Companies House API does not come with an official SDK. Fortunately, the API is documented fully defined in [OpenAPI](https://swagger.io/) (specifically [Swagger 2.0](https://swagger.io/specification/v2/)) specifications - an open source standard for defining APIs. Since OpenAPI is industry standard there are many tools that exist that produce high quality SDKs from OpenAPI definitions. For example, [Cloudflare](https://www.stainless.com/customers/cloudflare), [OpenAI](https://www.stainless.com/customers/openai), [Anthropic](https://docs.anthropic.com/claude/reference/client-sdks) and many define their SDKs in OpenAPI3 and generate them using [Stainless](https://www.stainless.com/). Unfortunately, these definitions are distributed amongst many files (i.e. the API is broken down into several smaller API products, with the [Companies House Public Data API](https://developer-specs.company-information.service.gov.uk/companies-house-public-data-api/reference) product by itself being distributed over 22 files!). Moreover, these definitions contain various errors that make them unusable.

This small, configurable and simple tool fetches the OpenAPI for Companies House API, formats them to fix errors found in them.

## Installation

[`pip`](https://pip.pypa.io/) is the default package installer for Python,
enabling easy installation and management of packages
from the [Python Package Index](https://pypi.org/) (**PyPI**)
and from Version Control System (VCS) sources
via the command line.

> [!TIP]
> The methods described work for other package manegers like
> [`uv`](https://docs.astral.sh/uv/) and [`poetry`](https://python-poetry.org/)

### Install From PyPI

To this package from PyPI, run:

```shell
pip install companies-house-codegen
```

### Install From Github (Using VCS Support)

To install from latest version of this Github repo use:

```shell
pip install git+https://github.com/MMurape/companies-house-codegen.git@main
```

> [!TIP]
> See `pip`'s documentation [VCS Support](https://pip.pypa.io/en/stable/topics/vcs-support/)
> for more infomation. Note, that most modern package managers also come with VCS support
> similar to `pip`.

### Install From A Git Clone (Using a clone of this repo)

To install this repository from a git clone, perform the following steps:

1. Clone this repository.
2. After clone this repository, the run the following command:

    ```shell
    cd companies-house-codegen # change directory to this repository
    ```

3. Install the package using package manager of your choice:

    ```shell
    pip install .
    ```

## Requirements

`companies-house-codegen` requires Python 3.8+
and [`typing-extensions`](https://github.com/python/typing_extensions).
You may also, optionally, install pydantic for additional typesafety.

## Usage

This toolkit can either be used
as a command-line interface - [`companies-house-codegen`](command-line-interface.md) -
or as a python module - [`companies_house_codegen`](api-reference/index.md).

For more information on command-line interface see: [API Reference](api-reference/index.md).

For more information on command-line interface see: [CLI Reference](command-line-interface.md).

### Example: Download Companies House Public Data API and convert it to OpenAPI 3.0.1

As a simple example of usage, here is how you could download
the OpenAPI (Swagger 2.0) specification for
[Companies House Public Data API](https://developer-specs.company-information.service.gov.uk/companies-house-public-data-api/reference)
and convert it to OpenAPI 3.0.1.

#### Using the CLI

```shell
# Download Companies House Public Data API and convert it to OpenAPI 3.0.1
companies-house-codegen -i https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/swagger.json --zip public_data_api_openapi.yml --openapi
```

#### Using the library

```python
from companies_house_codegen.codegen import download_openapi
from companies_house_codegen.utils import mapping_representer
import yaml
from yaml import CDumper

public_data_api_openapi = download_openapi('https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/swagger.json')
with open('public_data_api_openapi.yml', 'w') as f:
    # yaml does not know how to dump special an Mappings like OrderedDict.
    CDumper.add_representer(OrderedDict, mapping_representer)
    yaml.dump(m, f, indent=2, sort_keys=False, Dumper=CDumper) # save yaml
```
