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
Important constants for related to codegen
"""

import re
from enum import Enum, IntEnum  # NOTE: Python 3.7 does not have StrEnum

COMPANIES_HOUSE_HOST = "developer-specs.company-information.service.gov.uk"
"""
developer-specs.company-information.service.gov.uk is the 
`host<https://www.rfc-editor.org/rfc/rfc3986#section-3.2.2>`_ name of 
companies house Developer's API suite (where Specifactions are hosted)
"""

COMPANIES_HOUSE_PORT = 10000
"""
Port 10000 is used by Companies House for transmitting web data
over the localhost network using the Hypertext Transfer Protocol (HTTP)
"""

LOCALHOST_IP = "127.0.0.1"
"""
127.0.0.1 is known as the loopback address or localhost,
which is used for testing applications on the same device
without needing an internet connection.
It allows a computer to communicate with itself for various tasks.
"""

LOOPBACK_ADDR = f"http://{LOCALHOST_IP}:{COMPANIES_HOUSE_PORT}"
"""
<http://127.0.0.1:10000> is the url (loopback address) used by Companies House
for testing API applications on the same device
without needing an internet connection.
It allows a computer to communicate with itself for various tasks.
"""

ALLOWED_TYPES = frozenset(("string", "number", "boolean", "integer", "array"))
"""
The primitive data types allowed in the 
`Swagger Specification <https://swagger.io/specification/v2/#data-types>`_
"""

# TODO: handle yml
RE_REMOTE_JSON_REF_PATH = re.compile(r"^(?:/?|[/?]\S+)\.(?:json|ya?ml)$", re.IGNORECASE)
"""
Regex pattern for Remote JSON 
"""

RE_URL = re.compile(
    r"^(?:http|ftp)s?://"  # http:// or https://
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
    r"localhost|"  # localhost...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    r"(?::\d+)?"  # optional port
    r"(?:/?|[/?]\S+)\Z",
    re.IGNORECASE,
)
"""
Regex pattern of an http/https/ftp/ftps url.

See Also
--------
https://github.com/django/django/blob/stable/1.4.x/django/core/validators.py#L47
"""

RE_SERVER_ADDR = re.compile(
    r"(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|"  # domain...
    r"localhost|"  # localhost...
    r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})"  # ...or ip
    r"(?::\d+)?",  # optional port
    re.IGNORECASE,
)
"""
Regex pattern for server address <IP:PORT>.


"""


class CHOAS(str, Enum):
    """
    Enum of available
    **C**ompanies **H**ouse **O**pen**A**PI (Swagger 2.0) **S**pecfications.

    See Also
    --------
    `Companies House Developer's API suite<https://developer-specs.company-information.service.gov.uk>`_
    """

    IDENTITY_SERVICE = "https://developer-specs.company-information.service.gov.uk/account.ch.gov.uk-specifications/swagger-2.0/identity-public.json"
    """Companies House identity and authentication service."""

    PUBLIC_DATA_API = "https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/swagger.json"
    """
    An API suite providing read only access to search and retrieve public company data
    """

    DISCREPANCIES = "https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/pscDiscrepancies.json"
    """For use only by Obliged Entities to report PSC Discrepancies"""

    DOCUMENT_API = "https://developer-specs.company-information.service.gov.uk/document.api.ch.gov.uk-specifications/swagger-2.0/spec/swagger.json"
    """
    API suite providing company filing history document metadata and downloads.
    """

    MANIPULATE_COMPANY_DATA = "https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/filings-public.json"
    """
    An API suite that allows clients to manipulate company information,
    if they have authority to do so.
    """

    SANDBOX_TEST_DATA_GENERATOR_API = "https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/testDataGenerator.json"
    """Sandbox API suite to generate test data on demand"""

    STREAMING_API = "https://developer-specs.company-information.service.gov.uk/api.ch.gov.uk-specifications/swagger-2.0/spec/streaming.json"
    """A streaming API giving access to real time data changes."""


# TODO: document
class URLScheme(str, Enum):
    """
    Enum of URL schemes supported by codegen.
    """

    FTP = "ftp"
    """
    `FTP<https://datatracker.ietf.org/doc/html/rfc114>`_
    (**F**ile **T**ransfer **P**rotocol) is a standardized way of transfering
    files between computers on a network.

    TODO: ftp support
    """

    FTPS = "ftps"
    """
    `FTPS<https://en.wikipedia.org/wiki/FTPS>`_
    (**F**ile **T**ransfer **P**rotocol (**FTP**) **S**ecure)
    is an extension of FTP
    that uses `TLS<https://en.wikipedia.org/wiki/Transport_Layer_Security>`_
    (**T**ransport **L**ayer **S**ecurity) to secure communications
    over a computer network, making it safer for transferring sensitive files. 

    TODO: Implement https://stackoverflow.com/a/73171311
    """

    HTTP = "http"
    """
    `HTTP<https://datatracker.ietf.org/doc/html/rfc9110>`_
    (**H**yper**t**ext **T**ransfer **P**rotocol) is a stateless application protocol
    in the `Internet protocol suite<https://en.wikipedia.org/wiki/Internet_protocol_suite>`_
    for distributed, collaborative, hypertext information systems.
    """

    HTTPS = "https"
    """
    `HTTPS<https://en.wikipedia.org/wiki/HTTPS>`_ 
    (**H**ypertext **T**ransfer **P**rotocol **S**ecure) is an extension of HTTP
    that uses encryption to secure communications over a computer network, 
    making it safer for transmitting sensitive data. 
    This ensures protect user privacy and data integrity
    during online transactions over the internet.
    """


class ExitCode(IntEnum):
    """
    Exit codes related to the main function.
    """

    SUCCESS = 0
    ERROR = 1
    KEYBOARD_INTERRUPT = 2


__all__ = [
    "COMPANIES_HOUSE_HOST",
    "COMPANIES_HOUSE_PORT",
    "LOCALHOST_IP",
    "LOOPBACK_ADDR",
    "RE_REMOTE_JSON_REF_PATH",
    "RE_URL",
    "CHOAS",
    "URLScheme",
    "ExitCode",
]
