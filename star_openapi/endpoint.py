from functools import wraps
from inspect import iscoroutinefunction
from typing import Any, Type

from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import Response

from .request import _validate_request


def create_endpoint(
    func: Any,
    header: Type[BaseModel] | None = None,
    cookie: Type[BaseModel] | None = None,
    path: Type[BaseModel] | None = None,
    query: Type[BaseModel] | None = None,
    form: Type[BaseModel] | None = None,
    body: Type[BaseModel] | None = None,
):
    @wraps(func)
    async def endpoint(request: Request) -> Response:
        kwargs = await _validate_request(
            request=request,
            header=header,
            cookie=cookie,
            path=path,
            query=query,
            form=form,
            body=body,
        )
        if "request" in func.__code__.co_varnames:
            kwargs["request"] = request
        if iscoroutinefunction(func):
            return await func(**kwargs)
        else:
            return func(**kwargs)

    return endpoint
