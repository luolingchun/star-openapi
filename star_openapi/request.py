import json
from json import JSONDecodeError
from typing import Type

from pydantic import BaseModel
from pydantic.fields import FieldInfo
from starlette.datastructures import ImmutableMultiDict
from starlette.requests import Request


def _get_list_value(
    model: Type[BaseModel], args: ImmutableMultiDict, model_field_key: str, model_field_value: FieldInfo
):
    if model_field_value.alias and model.model_config.get("populate_by_name"):
        key = model_field_value.alias
        value = args.getlist(model_field_value.alias) or args.getlist(model_field_key)
    elif model_field_value.alias:
        key = model_field_value.alias
        value = args.getlist(model_field_value.alias)
    else:
        key = model_field_key
        value = args.getlist(model_field_key)

    return key, value


def _get_value(model: Type[BaseModel], args: ImmutableMultiDict, model_field_key: str, model_field_value: FieldInfo):
    if model_field_value.alias and model.model_config.get("populate_by_name"):
        key = model_field_value.alias
        value = args.get(model_field_value.alias) or args.get(model_field_key)
    elif model_field_value.alias:
        key = model_field_value.alias
        value = args.get(model_field_value.alias)
    else:
        key = model_field_key
        value = args.get(model_field_key)

    return key, value


async def _validate_header(request: Request, header: Type[BaseModel]):
    request_headers = dict(request.headers)
    header_dict = {}
    model_properties = header.model_json_schema().get("properties", {})
    for model_field_key, model_field_value in header.model_fields.items():
        key_title = model_field_key.replace("_", "-").title()
        model_field_schema = model_properties.get(model_field_value.alias or model_field_key)
        if model_field_value.alias and header.model_config.get("populate_by_name"):
            key = model_field_value.alias
            key_alias_title = model_field_value.alias.replace("_", "-").title()
            value = request_headers.get(key_alias_title) or request_headers.get(key_title)
        elif model_field_value.alias:
            key = model_field_value.alias
            key_alias_title = model_field_value.alias.replace("_", "-").title()
            value = request_headers.get(key_alias_title)
        else:
            key = model_field_key
            value = request_headers[key_title]
        if value is not None:
            header_dict[key] = value
        if model_field_schema.get("type") == "null":
            header_dict[key] = value  # type:ignore
    # extra keys
    for key, value in request_headers.items():
        if key not in header_dict.keys():
            header_dict[key] = value
    return header.model_validate(obj=header_dict)


async def _validate_cookie(request: Request, cookie: Type[BaseModel]):
    request_cookies = dict(request.cookies)
    return cookie.model_validate(obj=request_cookies)


async def _validate_path(request: Request, path: Type[BaseModel]):
    return path.model_validate(obj=request.path_params)


async def _validate_query(request: Request, query: Type[BaseModel]):
    query_dict = {}
    query_params = request.query_params
    model_properties = query.model_json_schema().get("properties", {})
    for model_field_key, model_field_value in query.model_fields.items():
        model_field_schema = model_properties.get(model_field_value.alias or model_field_key)
        if model_field_schema.get("type") == "array":
            key, value = _get_list_value(query, query_params, model_field_key, model_field_value)
        # To handle Optional[list]
        elif any(m.get("type") == "array" for m in model_field_schema.get("anyOf", [])):
            key, value = _get_list_value(query, query_params, model_field_key, model_field_value)
        else:
            key, value = _get_value(query, query_params, model_field_key, model_field_value)
        if value is not None and value != []:
            query_dict[key] = value
        if model_field_schema.get("type") == "null":
            query_dict[key] = value
    # extra keys
    for key, value in query_params.items():
        if key not in query_dict.keys():
            query_dict[key] = value
    return query.model_validate(obj=query_dict)


async def _validate_form(request: Request, form: Type[BaseModel]):
    request_form = await request.form()
    form_dict = {}
    model_properties = form.model_json_schema().get("properties", {})
    for model_field_key, model_field_value in form.model_fields.items():
        model_field_schema = model_properties.get(model_field_value.alias or model_field_key)
        if model_field_schema.get("type") == "array":
            if model_field_schema.get("items") == {"format": "binary", "type": "string"}:
                # list[FileStorage]
                key, value = _get_list_value(form, request_form, model_field_key, model_field_value)
            else:
                value = []
                key, value_list = _get_list_value(form, request_form, model_field_key, model_field_value)
                for _value in value_list:
                    try:
                        value.append(json.loads(_value))
                    except (JSONDecodeError, TypeError):
                        value.append(_value)
        elif model_field_schema.get("type") == "string" and model_field_schema.get("format") == "binary":
            # FileStorage
            key, value = _get_value(form, request_form, model_field_key, model_field_value)
        else:
            key, _value = _get_value(form, request_form, model_field_key, model_field_value)
            try:
                value = json.loads(_value)
            except (JSONDecodeError, TypeError):
                value = _value
        if value is not None and value != []:
            form_dict[key] = value
        if model_field_schema.get("type") == "null":
            form_dict[key] = value
    # extra keys
    for key, value in {**dict(request_form), **dict(request_form)}.items():
        if key not in form_dict.keys():
            form_dict[key] = value
    return form.model_validate(obj=form_dict)


async def _validate_body(request: Request, body: Type[BaseModel]):
    try:
        _json = await request.json()
        return body.model_validate(obj=_json)
    except JSONDecodeError:
        _json = await request.body()
        return body.model_validate_json(json_data=_json)


async def _validate_request(
    request: Request,
    header: Type[BaseModel] | None = None,
    cookie: Type[BaseModel] | None = None,
    path: Type[BaseModel] | None = None,
    query: Type[BaseModel] | None = None,
    form: Type[BaseModel] | None = None,
    body: Type[BaseModel] | None = None,
) -> dict:
    """
    Validate requests and responses.

    Args:
        header: Header model.
        cookie: Cookie model.
        path: Path model.
        query: Query model.
        form: Form model.
        body: Body model.

    Returns:
        dict: func kwargs.
    """

    # Dictionary to store func kwargs
    kwargs = dict()

    # Validate header, cookie, path, and query parameters
    if header:
        kwargs["header"] = await _validate_header(request, header)
    if cookie:
        kwargs["cookie"] = await _validate_cookie(request, cookie)
    if path:
        kwargs["path"] = await _validate_path(request, path)
    if query:
        kwargs["query"] = await _validate_query(request, query)
    if form:
        kwargs["form"] = await _validate_form(request, form)
    if body:
        kwargs["body"] = await _validate_body(request, body)

    return kwargs
