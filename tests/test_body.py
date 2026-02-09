from pydantic import BaseModel
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from star_openapi import OpenAPI

app = OpenAPI()

client = TestClient(app)


class AuthorModel(BaseModel):
    name: str
    age: int


class BookModel(BaseModel):
    name: str
    authors: list[AuthorModel] | None = None
    files: list[str]


@app.post("/book")
async def create_book(body: BookModel):
    return JSONResponse(body.model_dump())


def test_post():
    data = {"name": "test", "files": ["file1", "file2"]}
    response = client.post("/book", json=data)
    print(response.json())
    assert response.status_code == 200
    assert response.json() == {"authors": None, "files": ["file1", "file2"], "name": "test"}


def test_post_with_error_json():
    error_json = '{"aaa:111}'.encode("utf8")
    response = client.post("/book", content=error_json)
    assert response.status_code == 422
