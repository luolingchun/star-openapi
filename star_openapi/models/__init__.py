"""
OpenAPI v3.1.0 schema types, created according to the specification:
https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md

The type orders are according to the contents of the specification:
https://github.com/OAI/OpenAPI-Specification/blob/main/versions/3.1.0.md#table-of-contents
"""

from pydantic import BaseModel

from .callback import Callback  # noqa: F401
from .components import Components  # noqa: F401
from .contact import Contact  # noqa: F401
from .discriminator import Discriminator  # noqa: F401
from .encoding import Encoding  # noqa: F401
from .example import Example  # noqa: F401
from .external_documentation import ExternalDocumentation  # noqa: F401
from .file import UploadFile  # noqa: F401
from .header import Header  # noqa: F401
from .info import Info  # noqa: F401
from .license import License  # noqa: F401
from .link import Link  # noqa: F401
from .media_type import MediaType  # noqa: F401
from .oauth_flow import OAuthFlow  # noqa: F401
from .oauth_flows import OAuthFlows  # noqa: F401
from .operation import Operation  # noqa: F401
from .parameter import Parameter  # noqa: F401
from .parameter_in_type import ParameterInType  # noqa: F401
from .path_item import PathItem  # noqa: F401
from .paths import Paths  # noqa: F401
from .reference import Reference  # noqa: F401
from .request_body import RequestBody  # noqa: F401
from .response import Response  # noqa: F401
from .responses import Responses  # noqa: F401
from .schema import Schema  # noqa: F401
from .security_requirement import SecurityRequirement  # noqa: F401
from .security_scheme import SecurityScheme  # noqa: F401
from .server import Server  # noqa: F401
from .server_variable import ServerVariable  # noqa: F401
from .style_values import StyleValues  # noqa: F401
from .tag import Tag  # noqa: F401
from .validation_error import ValidationErrorModel  # noqa: F401
from .xml import XML  # noqa: F401

OPENAPI3_REF_PREFIX = "#/components/schemas"
OPENAPI3_REF_TEMPLATE = OPENAPI3_REF_PREFIX + "/{model}"


class OpenAPISpec(BaseModel):
    """https://spec.openapis.org/oas/v3.1.0#openapi-object"""

    openapi: str
    info: Info
    servers: list[Server] | None = None
    paths: Paths
    components: Components | None = None
    security: list[SecurityRequirement] | None = None
    tags: list[Tag] | None = None
    externalDocs: ExternalDocumentation | None = None
    webhooks: dict[str, PathItem | Reference] | None = None

    model_config = {"extra": "allow"}


class OAuthConfig(BaseModel):
    """
    https://github.com/swagger-api/swagger-ui/blob/master/docs/usage/oauth2.md#oauth-20-configuration
    """

    clientId: str | None = None
    clientSecret: str | None = None
    realm: str | None = None
    appName: str | None = None
    scopeSeparator: str | None = None
    scopes: str | None = None
    additionalQueryStringParams: dict[str, str] | None = None
    useBasicAuthenticationWithAccessCodeGrant: bool | None = False
    usePkceWithAuthorizationCodeGrant: bool | None = False


Encoding.model_rebuild()
Operation.model_rebuild()
PathItem.model_rebuild()
