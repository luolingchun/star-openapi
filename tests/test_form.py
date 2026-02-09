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
    null: None = None

    model_config = {"extra": "allow"}


@app.post("/book")
async def create_book(form: BookModel):
    return JSONResponse(form.model_dump())


def test_post():
    data = {"name": "test", "files": ["file1", "file2"], "extra": "extra"}
    response = client.post("/book", data=data)
    assert response.status_code == 200
    assert response.json() == {
        "authors": None,
        "extra": "extra",
        "files": ["file1", "file2"],
        "name": "test",
        "null": None,
    }
