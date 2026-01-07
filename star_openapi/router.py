from collections.abc import Callable
from http import HTTPMethod
from typing import Any

from starlette.routing import Route, Router, WebSocketRoute

from .endpoint import create_endpoint
from .models import ExternalDocumentation, Server, Tag
from .types import ParametersTuple
from .utils import (
    get_operation,
    get_operation_id_for_path,
    parse_and_store_tags,
    parse_method,
    parse_parameters,
    parse_rule,
)


class APIRouter(Router):
    def __init__(
        self,
        *,
        url_prefix: str = "",
        tags: list[Tag | dict[str, Any]] | None = None,
        security: list[dict[str, list[str]]] | None = None,
        operation_id_callback: Callable = get_operation_id_for_path,
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
            doc_ui: Enable OpenAPI document UI (Swagger UI, Redoc, etc.). Defaults to True.
            **kwargs: Starlette Router kwargs
        """
        super().__init__(**kwargs)

        self.url_prefix = url_prefix
        self.paths: dict[str, Any] = {}
        self.components_schemas: dict[str, Any] = {}
        self.tags = tags or []
        self.tag_names: list[str] = []
        self.security = security or []
        self.operation_id_callback = operation_id_callback
        self.doc_ui = doc_ui

    def register_api(self, api: "APIRouter"):
        for tag in api.tags:
            if isinstance(tag, dict):
                tag = Tag(**tag)
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
                self.add_route(
                    path=path_with_prefix,
                    endpoint=route.endpoint,
                    methods=route.methods,
                    name=route.name,
                )
            elif isinstance(route, WebSocketRoute):
                path_with_prefix = api.url_prefix + route.path
                self.add_websocket_route(path=path_with_prefix, endpoint=route.endpoint, name=route.name)

    def _collect_openapi_info(
        self,
        rule: str,
        func: Callable,
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
        doc_ui: bool = True,
        method: str = HTTPMethod.GET,
    ) -> ParametersTuple:
        if self.doc_ui and doc_ui:
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
            tags = (tags or []) + self.tags
            parse_and_store_tags(tags, self.tags, self.tag_names, operation)

            # Parse rule: merge url_prefix and format rule from /pet/<petId> to /pet/{petId}
            uri = parse_rule(rule, url_prefix=self.url_prefix)

            # Parse method
            parse_method(uri, method, self.paths, operation)

            # Parse parameters
            return parse_parameters(func, components_schemas=self.components_schemas, operation=operation)
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
        doc_ui: bool = True,
    ):
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
        doc_ui: bool = True,
    ):
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
        doc_ui: bool = True,
    ):
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
        doc_ui: bool = True,
    ):
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
        doc_ui: bool = True,
    ):
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
