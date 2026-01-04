# -*- coding: utf-8 -*-
# @Author  : llc
# @Time    : 2021/5/11 16:17
from typing import Any

from pydantic.json_schema import JsonSchemaValue
from pydantic_core import core_schema
from starlette.datastructures import UploadFile as _UploadFile


class UploadFile(_UploadFile):
    """
    An uploaded file included as part of the request data.
    """

    @classmethod
    def __get_pydantic_json_schema__(cls, *_args: Any, **_kwargs: Any) -> JsonSchemaValue:
        field_schema = {"format": "binary", "type": "string"}
        return field_schema

    @classmethod
    def __get_pydantic_core_schema__(cls, *_args: Any, **_kwargs: Any) -> core_schema.CoreSchema:
        return core_schema.with_info_plain_validator_function(cls.validate)

    @classmethod
    def validate(cls, value: _UploadFile, *_args: Any, **_kwargs: Any):
        return value
