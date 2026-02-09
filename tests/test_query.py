from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from star_openapi import OpenAPI

app = OpenAPI()

client = TestClient(app)


class AuthorModel(BaseModel):
    name: str
    age: int


class BookModel(BaseModel):
    name: str = Field(
        ...,
        description="Name",
        deprecated=True,
        json_schema_extra={
            "example": 1,
            "examples": {"example1": {"value": 1}, "example2": {"value": 2}},
        },
    )
    authors: list[AuthorModel] | None = None
    files: list[str]
    optional_list: list[str] | None = None
    null: None = None
    alias_name: str = Field(None, alias="alias")
    alias_list: list[str] = Field(None, alias="alias_list")

    model_config = {"extra": "allow"}


class BookPopulateByName(BookModel):
    model_config = {"populate_by_name": True}


@app.get("/book")
async def get_book(query: BookModel):
    return JSONResponse(query.model_dump())


@app.get("/book/populate_by_name")
async def get_book_populate_by_name(query: BookPopulateByName):
    return JSONResponse(query.model_dump())


def test_get():
    params = {"name": "test", "files": ["file1", "file2"], "alias": "alias", "alias_list": ["a", "b"], "extra": "extra"}
    response = client.get("/book", params=params)
    assert response.status_code == 200
    assert response.json() == {
        "alias_list": ["a", "b"],
        "alias_name": "alias",
        "authors": None,
        "extra": "extra",
        "files": ["file1", "file2"],
        "name": "test",
        "null": None,
        "optional_list": None,
    }


def test_get_populate_by_name():
    params = {"name": "test", "files": ["file1", "file2"], "alias": "alias", "alias_list": ["a", "b"], "extra": "extra"}
    response = client.get("/book/populate_by_name", params=params)
    assert response.status_code == 200
    assert response.json() == {
        "alias_list": ["a", "b"],
        "alias_name": "alias",
        "authors": None,
        "extra": "extra",
        "files": ["file1", "file2"],
        "name": "test",
        "null": None,
        "optional_list": None,
    }
