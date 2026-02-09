from collections.abc import Callable
from http import HTTPMethod
from importlib import import_module
from importlib.metadata import entry_points
from types import FunctionType
from typing import Any, Type

from jinja2 import Template
from pydantic import BaseModel, ValidationError
from starlette.applications import Starlette
from starlette.responses import HTMLResponse, JSONResponse
from starlette.routing import Mount, Route, WebSocketRoute

from .cli import cli
from .config import Config
from .endpoint import create_endpoint
from .models import (
    OPENAPI3_REF_PREFIX,
    Components,
    ExternalDocumentation,
    Info,
    OpenAPISpec,
    RequestBody,
    Schema,
    SecurityScheme,
    Server,
    Tag,
    ValidationErrorModel,
)
from .router import APIRouter
from .templates import openapi_html_string
from .types import ParametersTuple, ResponseDict
from .utils import (
    HTTP_STATUS,
    convert_responses_key_to_string,
    get_model_schema,
    get_operation,
    get_operation_id_for_path,
    get_responses,
    make_validation_error_response,
    parse_and_store_tags,
    parse_method,
    parse_parameters,
)


class OpenAPI(Starlette):
    def __init__(
        self,
        *,
        info: Info | dict[str, Any] | None = None,
        security_schemes: dict[str, SecurityScheme | dict[str, Any]] | None = None,
        servers: list[Server | dict[str, Any]] | None = None,
        external_docs: ExternalDocumentation | dict[str, Any] | None = None,
        operation_id_callback: Callable = get_operation_id_for_path,
        openapi_extensions: dict[str, Any] | None = None,
        validation_error_status: str | int = 422,
        validation_error_model: Type[BaseModel] = ValidationErrorModel,
        validation_error_callback: Callable = make_validation_error_response,
        responses: ResponseDict | None = None,
        doc_ui: bool = True,
        doc_prefix: str = "/openapi",
        doc_url: str = "/openapi.json",
        **kwargs,
    ):
        """
        OpenAPI class that provides REST API functionality along with Swagger UI and Redoc, etc.

        Args:
            info: Information about the API (title, version, etc.).
                See https://spec.openapis.org/oas/v3.1.0#info-object.
            security_schemes: Security schemes for the API.
                See https://spec.openapis.org/oas/v3.1.0#security-scheme-object.
            servers: An array of Server objects providing connectivity information to a target server.
            external_docs: External documentation for the API.
                See: https://spec.openapis.org/oas/v3.1.0#external-documentation-object.
            operation_id_callback: Callback function for custom operation ID generation.
                Receives name (str), path (str), and method (str) parameters.
                Defaults to `get_operation_id_for_path` from utils.
            openapi_extensions: Extensions to the OpenAPI Schema.
                See https://spec.openapis.org/oas/v3.1.0#specification-extensions.
            validation_error_status:
                HTTP Status of the response given when a validation error is detected by pydantic.
                Defaults to 422.
            validation_error_model: Validation error response model for OpenAPI Specification.
            validation_error_callback: Validation error response callback, the return format corresponds to
                the validation_error_model.
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            doc_ui: Enable OpenAPI document UI (Swagger UI and Redoc).
                Defaults to True.
            doc_prefix: URL prefix used for OpenAPI document and UI.
                Defaults to "/openapi".
            doc_url: URL for accessing the OpenAPI specification document in JSON format.
                Defaults to "/openapi.json".
            **kwargs: Additional kwargs to be passed to Starlette.
        """
        super().__init__(**kwargs)

        self.config = Config()

        # Set OpenAPI version and API information
        self.openapi_version = "3.1.0"
        self.info = info or {"title": "OpenAPI", "version": "1.0.0"}

        # Set security schemes, responses, paths and components
        self.security_schemes = security_schemes

        # Initialize instance variables
        self.paths: dict[str, Any] = {}
        self.components_schemas: dict[str, Any] = {}
        self.components = Components()

        # Initialize lists for tags and tag names
        self.tags: list[Tag] = []
        self.tag_names: list[str] = []

        # Set URL prefixes and endpoints
        self.doc_prefix = doc_prefix
        self.doc_url = doc_url

        # Set servers and external documentation
        self.severs = servers
        self.external_docs = external_docs

        # Set the operation ID callback function
        self.operation_id_callback: Callable = operation_id_callback

        # Set OpenAPI extensions
        self.openapi_extensions = openapi_extensions or {}

        # Set HTTP Response of validation errors within OpenAPI
        self.validation_error_status = str(validation_error_status)
        self.validation_error_model = validation_error_model
        self.add_exception_handler(ValidationError, validation_error_callback)

        # Convert responses key to string
        self.responses = convert_responses_key_to_string(responses or {})

        # Initialize the OpenAPI documentation UI
        if doc_ui:
            self._init_doc()

        # Initialize specification JSON
        self.spec_json: dict[str, Any] = {}

        self.cli = cli

    def _init_doc(self) -> None:
        template = Template(openapi_html_string)

        routes = []
        ui_templates = []
        for entry_point in entry_points(group="star_openapi.plugins"):
            try:
                module_path = entry_point.value
                module_name, class_name = module_path.rsplit(".", 1)
                module = import_module(module_name)
                plugin = getattr(module, class_name)()
                plugin_register = plugin.register
                plugin_name = plugin.name
                plugin_display_name = plugin.display_name
                route = plugin_register(doc_url=self.doc_url.lstrip("/"))
                routes.extend(route)
                ui_templates.append({"name": plugin_name, "display_name": plugin_display_name})
            except (ModuleNotFoundError, AttributeError):  # pragma: no cover
                import traceback

                print(f"Warning: plugin '{entry_point.value}' registration failed.")
                traceback.print_exc()

        routes.append(
            Route(
                "/",
                endpoint=lambda request: HTMLResponse(content=template.render({"ui_templates": ui_templates})),
                methods=["GET"],
                name="index",
            )
        )
        routes.append(
            Route(
                self.doc_url,
                endpoint=lambda request: JSONResponse(self.api_doc),
                methods=["GET"],
                name="openapi",
            )
        )

        self.router.routes.append(Mount(self.doc_prefix, routes=routes, name="openapi"))

    @property
    def api_doc(self) -> dict:
        if self.spec_json:
            return self.spec_json

        self.generate_spec_json()

        return self.spec_json

    def generate_spec_json(self):
        if isinstance(self.info, dict):
            self.info = Info.model_validate(self.info)
        spec = OpenAPISpec(openapi=self.openapi_version, info=self.info, paths=self.paths)

        if self.severs:
            spec.servers = [Server(**server) if isinstance(server, dict) else server for server in self.severs]

        if self.external_docs:
            if isinstance(self.external_docs, dict):
                self.external_docs = ExternalDocumentation.model_validate(self.external_docs)
            spec.externalDocs = self.external_docs

        # Set tags
        if self.tags:
            spec.tags = self.tags

        # Add ValidationErrorModel to components schemas
        schema = get_model_schema(self.validation_error_model)
        self.components_schemas[self.validation_error_model.__name__] = Schema(**schema)

        # Parse definitions
        definitions = schema.get("$defs", {})
        for name, value in definitions.items():
            self.components_schemas[name] = Schema(**value)

        # Set components
        self.components.schemas = self.components_schemas
        self.components.securitySchemes = self.security_schemes
        spec.components = self.components

        # Convert spec to JSON
        self.spec_json = spec.model_dump(mode="json", by_alias=True, exclude_unset=True, warnings=False)

        # Update with OpenAPI extensions
        self.spec_json.update(**self.openapi_extensions)

        # Handle validation error response
        for rule, path_item in self.spec_json["paths"].items():
            for http_method, operation in path_item.items():
                if operation["responses"].get(self.validation_error_status):
                    continue
                operation["responses"][self.validation_error_status] = {
                    "description": HTTP_STATUS[self.validation_error_status],
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "array",
                                "items": {"$ref": f"{OPENAPI3_REF_PREFIX}/{self.validation_error_model.__name__}"},
                            }
                        }
                    },
                }

    def register_api(self, api: APIRouter):
        """
        Register an APIRouter.

        Args:
            api: The APIBlueprint instance to register.
        """
        for tag in api.tags:
            if tag.name not in self.tag_names:
                # Append tag to the list of tags
                self.tags.append(tag)

                # Append tag name to the list of tag names
                self.tag_names.append(tag.name)

        self.paths.update(**api.paths)

        # Update component schemas with the APIRouter's component schemas
        self.components_schemas.update(**api.components_schemas)

        # Register the APIRouter with the current instance
        for route in api.routes:
            if isinstance(route, Route):
                path_with_prefix = api.url_prefix + route.path
                self.router.add_route(
                    path=path_with_prefix,
                    endpoint=route.endpoint,
                    methods=route.methods,
                    name=route.name,
                )
            elif isinstance(route, WebSocketRoute):
                path_with_prefix = api.url_prefix + route.path
                self.router.add_websocket_route(path=path_with_prefix, endpoint=route.endpoint, name=route.name)

    def _collect_openapi_info(
        self,
        rule: str,
        func: FunctionType,
        *,
        tags: list[Tag | dict[str, Any]] | None = None,
        summary: str | None = None,
        description: str | None = None,
        external_docs: ExternalDocumentation | dict[str, Any] | None = None,
        operation_id: str | None = None,
        deprecated: bool | None = None,
        security: list[dict[str, list[Any]]] | None = None,
        servers: list[Server | dict[str, Any]] | None = None,
        openapi_extensions: dict[str, Any] | None = None,
        request_body: RequestBody | dict[str, Any] | None = None,
        responses: ResponseDict | None = None,
        doc_ui: bool = True,
        method: str = HTTPMethod.GET,
    ) -> ParametersTuple:
        if doc_ui:
            # Convert key to string
            endpoint_responses = convert_responses_key_to_string(responses or {})

            # Global response: combine API responses
            combine_responses = {**self.responses, **endpoint_responses}

            # Create operation
            operation = get_operation(
                func,
                summary=summary,
                description=description,
                openapi_extensions=openapi_extensions,
            )
            # Set external docs
            if external_docs:
                operation.externalDocs = external_docs

            # Unique string used to identify the operation.
            operation.operationId = operation_id or self.operation_id_callback(
                name=func.__name__, path=rule, method=method
            )

            # Only set `deprecated` if True, otherwise leave it as None
            if deprecated is not None:
                operation.deprecated = deprecated

            # Add security
            if security:
                operation.security = security

            # Add servers
            if servers:
                operation.servers = servers

            # Store tags
            parse_and_store_tags(tags or [], self.tags, self.tag_names, operation)

            # Parse method
            parse_method(rule, method, self.paths, operation)

            if isinstance(request_body, dict):
                request_body = RequestBody(**request_body)

            # Parse response
            get_responses(combine_responses, self.components_schemas, operation)

            # Parse parameters
            return parse_parameters(
                func,
                components_schemas=self.components_schemas,
                operation=operation,
                request_body=request_body,
            )
        else:
            return parse_parameters(func, doc_ui=False)

    def get(
        self,
        rule: str,
        *,
        name: str | None = None,
        tags: list[Tag | dict[str, Any]] | None = None,
        summary: str | None = None,
        description: str | None = None,
        external_docs: ExternalDocumentation | dict[str, Any] | None = None,
        operation_id: str | None = None,
        deprecated: bool | None = None,
        security: list[dict[str, list[Any]]] | None = None,
        servers: list[Server | dict[str, Any]] | None = None,
        openapi_extensions: dict[str, Any] | None = None,
        responses: ResponseDict | None = None,
        doc_ui: bool = True,
    ):
        """
        Decorator for defining a REST API endpoint with the HTTP GET method.
        More information goto https://spec.openapis.org/oas/v3.1.0#operation-object

        Args:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            doc_ui: Declares this operation to be shown. Default to True.
        """

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body = self._collect_openapi_info(
                rule,
                func,
                tags=tags,
                summary=summary,
                description=description,
                external_docs=external_docs,
                operation_id=operation_id,
                deprecated=deprecated,
                security=security,
                servers=servers,
                openapi_extensions=openapi_extensions,
                responses=responses,
                doc_ui=doc_ui,
                method=HTTPMethod.GET,
            )
            endpoint = create_endpoint(func, header, cookie, path, query, form, body)
            self.add_route(rule, endpoint, methods=["GET"], name=name, include_in_schema=False)

            return func

        return decorator

    def post(
        self,
        rule: str,
        *,
        name: str | None = None,
        tags: list[Tag | dict[str, Any]] | None = None,
        summary: str | None = None,
        description: str | None = None,
        external_docs: ExternalDocumentation | dict[str, Any] | None = None,
        operation_id: str | None = None,
        deprecated: bool | None = None,
        security: list[dict[str, list[Any]]] | None = None,
        servers: list[Server | dict[str, Any]] | None = None,
        openapi_extensions: dict[str, Any] | None = None,
        request_body: RequestBody | dict[str, Any] | None = None,
        responses: ResponseDict | None = None,
        doc_ui: bool = True,
    ):
        """
        Decorator for defining a REST API endpoint with the HTTP POST method.
        More information goto https://spec.openapis.org/oas/v3.1.0#operation-object

        Args:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            doc_ui: Declares this operation to be shown. Default to True.
        """

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body = self._collect_openapi_info(
                rule,
                func,
                tags=tags,
                summary=summary,
                description=description,
                external_docs=external_docs,
                operation_id=operation_id,
                deprecated=deprecated,
                security=security,
                servers=servers,
                openapi_extensions=openapi_extensions,
                request_body=request_body,
                responses=responses,
                doc_ui=doc_ui,
                method=HTTPMethod.POST,
            )
            endpoint = create_endpoint(func, header, cookie, path, query, form, body)
            self.add_route(rule, endpoint, methods=["POST"], name=name, include_in_schema=False)

            return func

        return decorator

    def put(
        self,
        rule: str,
        *,
        name: str | None = None,
        tags: list[Tag | dict[str, Any]] | None = None,
        summary: str | None = None,
        description: str | None = None,
        external_docs: ExternalDocumentation | dict[str, Any] | None = None,
        operation_id: str | None = None,
        deprecated: bool | None = None,
        security: list[dict[str, list[Any]]] | None = None,
        servers: list[Server | dict[str, Any]] | None = None,
        openapi_extensions: dict[str, Any] | None = None,
        request_body: RequestBody | dict[str, Any] | None = None,
        responses: ResponseDict | None = None,
        doc_ui: bool = True,
    ):
        """
        Decorator for defining a REST API endpoint with the HTTP PUT method.
        More information goto https://spec.openapis.org/oas/v3.1.0#operation-object

        Args:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            doc_ui: Declares this operation to be shown. Default to True.
        """

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body = self._collect_openapi_info(
                rule,
                func,
                tags=tags,
                summary=summary,
                description=description,
                external_docs=external_docs,
                operation_id=operation_id,
                deprecated=deprecated,
                security=security,
                servers=servers,
                openapi_extensions=openapi_extensions,
                request_body=request_body,
                responses=responses,
                doc_ui=doc_ui,
                method=HTTPMethod.PUT,
            )
            endpoint = create_endpoint(func, header, cookie, path, query, form, body)
            self.add_route(rule, endpoint, methods=["PUT"], name=name, include_in_schema=False)

            return func

        return decorator

    def delete(
        self,
        rule: str,
        *,
        name: str | None = None,
        tags: list[Tag | dict[str, Any]] | None = None,
        summary: str | None = None,
        description: str | None = None,
        external_docs: ExternalDocumentation | dict[str, Any] | None = None,
        operation_id: str | None = None,
        deprecated: bool | None = None,
        security: list[dict[str, list[Any]]] | None = None,
        servers: list[Server | dict[str, Any]] | None = None,
        openapi_extensions: dict[str, Any] | None = None,
        request_body: RequestBody | dict[str, Any] | None = None,
        responses: ResponseDict | None = None,
        doc_ui: bool = True,
    ):
        """
        Decorator for defining a REST API endpoint with the HTTP DELETE method.
        More information goto https://spec.openapis.org/oas/v3.1.0#operation-object

        Args:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            doc_ui: Declares this operation to be shown. Default to True.
        """

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body = self._collect_openapi_info(
                rule,
                func,
                tags=tags,
                summary=summary,
                description=description,
                external_docs=external_docs,
                operation_id=operation_id,
                deprecated=deprecated,
                security=security,
                servers=servers,
                openapi_extensions=openapi_extensions,
                request_body=request_body,
                responses=responses,
                doc_ui=doc_ui,
                method=HTTPMethod.DELETE,
            )
            endpoint = create_endpoint(func, header, cookie, path, query, form, body)
            self.add_route(rule, endpoint, methods=["DELETE"], name=name, include_in_schema=False)

            return func

        return decorator

    def patch(
        self,
        rule: str,
        *,
        name: str | None = None,
        tags: list[Tag | dict[str, Any]] | None = None,
        summary: str | None = None,
        description: str | None = None,
        external_docs: ExternalDocumentation | dict[str, Any] | None = None,
        operation_id: str | None = None,
        deprecated: bool | None = None,
        security: list[dict[str, list[Any]]] | None = None,
        servers: list[Server | dict[str, Any]] | None = None,
        openapi_extensions: dict[str, Any] | None = None,
        request_body: RequestBody | dict[str, Any] | None = None,
        responses: ResponseDict | None = None,
        doc_ui: bool = True,
    ):
        """
        Decorator for defining a REST API endpoint with the HTTP PATCH method.
        More information goto https://spec.openapis.org/oas/v3.1.0#operation-object

        Args:
            rule: The URL rule string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            doc_ui: Declares this operation to be shown. Default to True.
        """

        def decorator(func) -> Callable:
            header, cookie, path, query, form, body = self._collect_openapi_info(
                rule,
                func,
                tags=tags,
                summary=summary,
                description=description,
                external_docs=external_docs,
                operation_id=operation_id,
                deprecated=deprecated,
                security=security,
                servers=servers,
                openapi_extensions=openapi_extensions,
                request_body=request_body,
                responses=responses,
                doc_ui=doc_ui,
                method=HTTPMethod.PATCH,
            )
            endpoint = create_endpoint(func, header, cookie, path, query, form, body)
            self.add_route(rule, endpoint, methods=["PATCH"], name=name, include_in_schema=False)

            return func

        return decorator

    def websocket(
        self,
        rule: str,
        *,
        name: str | None = None,
    ):
        def decorator(func) -> Callable:
            self.add_websocket_route(
                rule,
                func,
                name=name,
            )
            return func

        return decorator
