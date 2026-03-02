from collections.abc import Awaitable, Callable, Collection
from http import HTTPMethod
from types import FunctionType
from typing import Any, Sequence

from starlette.middleware import Middleware
from starlette.routing import Request, Response, Route, Router, WebSocketRoute
from starlette.websockets import WebSocket

from .endpoint import create_endpoint
from .models import ExternalDocumentation, RequestBody, Server, Tag
from .types import ParametersTuple, ResponseDict
from .utils import (
    convert_responses_key_to_string,
    get_operation,
    get_operation_id_for_path,
    get_responses,
    parse_and_store_tags,
    parse_method,
    parse_parameters,
    parse_rule,
)


class APIRoute(Route):
    def __init__(
        self,
        path: str,
        origin_path: str,
        endpoint: Callable[..., Any],
        *,
        methods: Collection[str] | None = None,
        name: str | None = None,
        include_in_schema: bool = True,
        middleware: Sequence[Middleware] | None = None,
    ):
        super().__init__(
            path=path,
            endpoint=endpoint,
            methods=methods,
            name=name,
            include_in_schema=include_in_schema,
            middleware=middleware,
        )

        self.origin_path = origin_path


class APIWebSocketRoute(WebSocketRoute):
    def __init__(
        self,
        path: str,
        origin_path: str,
        endpoint: Callable[..., Any],
        *,
        name: str | None = None,
        middleware: Sequence[Middleware] | None = None,
    ):
        super().__init__(
            path=path,
            endpoint=endpoint,
            name=name,
            middleware=middleware,
        )

        self.origin_path = origin_path


class APIRouter(Router):
    def __init__(
        self,
        *,
        url_prefix: str = "",
        tags: list[Tag | dict[str, Any]] | None = None,
        security: list[dict[str, list[str]]] | None = None,
        operation_id_callback: Callable = get_operation_id_for_path,
        responses: ResponseDict | None = None,
        doc_ui: bool = True,
        **kwargs,
    ):
        """
        Based on Router

        Args:
            url_prefix: URL prefix that will be added before all route paths.
            tags: APIRouter tags for every API.
            security: APIRouter security for every API.
            operation_id_callback: Callback function for custom operation_id generation.
            responses: API responses should be either a subclass of BaseModel, a dictionary, or None.
            doc_ui: Enable OpenAPI document UI (Swagger UI, Redoc, etc.). Defaults to True.
            **kwargs: Starlette Router kwargs
        """
        super().__init__(**kwargs)

        self.url_prefix = url_prefix
        self.paths: dict[str, Any] = {}
        self.components_schemas: dict[str, Any] = {}
        self.tags: list[Tag] = []
        self.api_tags = tags or []
        self.tag_names: list[str] = []
        self.security = security or []
        self.operation_id_callback = operation_id_callback
        self.responses = convert_responses_key_to_string(responses or {})
        self.doc_ui = doc_ui

    def register_api(self, api: "APIRouter"):
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

        prefixed_paths = {f"{self.url_prefix.rstrip('/')}{k}": v for k, v in api.paths.items()}
        self.paths.update(**prefixed_paths)

        # Update component schemas with the APIRouter's component schemas
        self.components_schemas.update(**api.components_schemas)

        # Register the APIRouter with the current instance
        for route in api.routes:
            if isinstance(route, APIRoute):
                path_with_prefix = api.url_prefix + route.origin_path
                self._add_route(
                    path=path_with_prefix,
                    endpoint=route.endpoint,
                    methods=route.methods,
                    name=route.name,
                )
            elif isinstance(route, APIWebSocketRoute):
                path_with_prefix = api.url_prefix + route.origin_path
                self._add_websocket_route(path=path_with_prefix, endpoint=route.endpoint, name=route.name)

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
        if self.doc_ui and doc_ui:
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
                url_prefix=self.url_prefix, name=func.__name__, path=rule, method=method
            )

            # Only set `deprecated` if True, otherwise leave it as None
            if deprecated is not None:
                operation.deprecated = deprecated

            # Add security
            _security = (security or []) + self.security or None
            if _security:
                operation.security = _security

            # Add servers
            if servers:
                operation.servers = servers

            # Store tags
            tags = (tags or []) + self.api_tags
            parse_and_store_tags(tags, self.tags, self.tag_names, operation)

            # Parse rule: merge url_prefix
            uri = parse_rule(rule, url_prefix=self.url_prefix)

            # Parse method
            parse_method(uri, method, self.paths, operation)

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

    def _add_route(
        self,
        path: str,
        endpoint: Callable[[Request], Awaitable[Response] | Response],
        methods: Collection[str] | None = None,
        name: str | None = None,
        include_in_schema: bool = True,
    ) -> None:
        if not path.startswith("/"):
            origin_path = path
            path = "/" + path
        else:
            origin_path = path
        route = APIRoute(
            path=path,
            origin_path=origin_path,
            endpoint=endpoint,
            methods=methods,
            name=name,
            include_in_schema=include_in_schema,
        )
        self.routes.append(route)

    def _add_websocket_route(
        self,
        path: str,
        endpoint: Callable[[WebSocket], Awaitable[None]],
        name: str | None = None,
    ) -> None:
        if not path.startswith("/"):
            origin_path = path
            path = "/" + path
        else:
            origin_path = path
        route = APIWebSocketRoute(path=path, origin_path=origin_path, endpoint=endpoint, name=name)
        self.routes.append(route)

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
            name: The URL name string.
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
            self._add_route(rule, endpoint, methods=["GET"], name=name, include_in_schema=False)

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
            name: The URL name string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            request_body: Advanced configuration in OpenAPI.
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
            self._add_route(rule, endpoint, methods=["POST"], name=name, include_in_schema=False)

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
            name: The URL name string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            request_body: Advanced configuration in OpenAPI.
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
            self._add_route(rule, endpoint, methods=["PUT"], name=name, include_in_schema=False)

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
            name: The URL name string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            request_body: Advanced configuration in OpenAPI.
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
            self._add_route(rule, endpoint, methods=["DELETE"], name=name, include_in_schema=False)

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
            name: The URL name string.
            tags: Adds metadata to a single tag.
            summary: A short summary of what the operation does.
            description: A verbose explanation of the operation behavior.
            external_docs: Additional external documentation for this operation.
            operation_id: Unique string used to identify the operation.
            deprecated: Declares this operation to be deprecated.
            security: A declaration of which security mechanisms can be used for this operation.
            servers: An alternative server array to service this operation.
            openapi_extensions: Allows extensions to the OpenAPI Schema.
            request_body: Advanced configuration in OpenAPI.
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
            self._add_route(rule, endpoint, methods=["PATCH"], name=name, include_in_schema=False)

            return func

        return decorator

    def websocket(
        self,
        rule: str,
        *,
        name: str | None = None,
    ):
        def decorator(func) -> Callable:
            self._add_websocket_route(
                rule,
                func,
                name=name,
            )
            return func

        return decorator
