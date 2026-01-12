from pydantic import BaseModel
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from star_openapi import OpenAPI

app = OpenAPI()

client = TestClient(app)


class BookModel(BaseModel):
    name: str
    files: list[str]


@app.post("/book")
async def post_book(form: BookModel):
    return JSONResponse(form.model_dump())


def test_post():
    data = {"name": "test", "files": ["file1", "file2"]}
    response = client.post("/book", data=data)
    assert response.status_code == 200
    assert response.json() == data
