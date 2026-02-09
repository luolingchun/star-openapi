from enum import Enum

from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from star_openapi import OpenAPI

app = OpenAPI()

client = TestClient(app)


class TypeEnum(str, Enum):
    A = "A"
    B = "B"


class AuthorModel(BaseModel):
    name: str
    age: int


class BookCookie(BaseModel):
    name: str = Field(
        None,
        description="Name",
        deprecated=True,
        json_schema_extra={
            "example": 1,
            "examples": {"example1": {"value": 1}, "example2": {"value": 2}},
        },
    )
    authors: list[AuthorModel] | None = None
    token: str | None = None
    token_type: TypeEnum | None = None


@app.post("/cookie")
def post_cookie(cookie: BookCookie):
    return JSONResponse(cookie.model_dump(by_alias=True))


def test_cookie():
    cookies = {"token": "xxx", "token_type": "A"}
    client.cookies.update(cookies)
    r = client.post("/cookie")
    assert r.status_code == 200
    assert r.json() == {"authors": None, "name": None, "token": "xxx", "token_type": "A"}
