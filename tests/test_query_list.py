from pydantic import BaseModel
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from star_openapi import OpenAPI
from star_openapi.router import APIRouter

app = OpenAPI()

api = APIRouter(url_prefix="/api")

client = TestClient(app)


class BookModel(BaseModel):
    name: str
    files: list[str]


@app.get("/book")
async def get_book(query: BookModel):
    return JSONResponse(query.model_dump())


@api.get("/book")
async def get_api_book(query: BookModel):
    return JSONResponse(query.model_dump())


app.register_api(api)


def test_get_book():
    response = client.get("/book?name=s&files=1&files=2")
    assert response.status_code == 200
    assert response.json() == {"name": "s", "files": ["1", "2"]}


def test_get_api_book():
    response = client.get("/api/book?name=s&files=1&files=2")
    assert response.status_code == 200
    assert response.json() == {"name": "s", "files": ["1", "2"]}
