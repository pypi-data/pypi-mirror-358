# Command-line Interface

Once you have installed `companies-house-codegen`, run the following:

```shell
companies-house-codegen --help
```

This will show you the help menu for the command;
it will show you what options are available to you and how to use them

```text
usage: companies-house-codegen [OPTIONS]

Generate, format and host OpenAPI specifications and for Companies House

options:
  -h, --help            show this help message and exit
  --version, -V         Show version and exit.

Input options:
  --input URL, -i URL   URL of a Companies House Swagger Specification from the Companies House     
                        Developer's API Suite. See: companies_house_codegen.constants.CHOAS or      
                        https://developer-specs.company-information.service.gov.uk for more info.   

Output and formatting options:
  --extract DIR, -e DIR
                        When specified, save specification files as to a directory.
  --zip FILE, -z FILE   Output as single file. Outputs as to stdout otherwise
  --openapi             Convert Swagger specification to OpenAPI.
  --serve [IP:PORT]     When specified, creates a local HTTP server. By default, serves on
                        127.0.0.1:10000. This can be overidden by passing an argument argument      
                        <IP:PORT> is passed

Debugging options:
  --silent, -s          Stop emitting all non-critical output. Error messages will still be
                        emitted (which can silenced by 2>/dev/null).
  --single-threaded     Download syncronously on a single thread. By default, downloads
                        syncronously using multithreading. Useful for debugging.
  --verbose, -v         Use verbose debug logging
```

Here is an example use case

```shell
# Download Companies House Public Data API and convert it to OpenAPI 3.0.1
companies-house-codegen -i https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/swagger.json --zip public_data_api_openapi.yml --openapi
```

> [!TIP]
> For more information, see [argument](/api-reference/argument)
> in [API Reference](docs/api-reference).
