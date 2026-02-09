from pydantic import BaseModel
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from star_openapi import OpenAPI

app = OpenAPI()

client = TestClient(app)


class IdModel(BaseModel):
    id: int


class BookModel(BaseModel):
    name: str
    age: int


@app.get("/book")
async def get_book(query: BookModel):
    return JSONResponse(query.model_dump())


@app.post("/book")
async def create_book(body: BookModel):
    return JSONResponse(body.model_dump())


@app.put("/book/{id}")
async def update_book(path: IdModel, body: BookModel):
    return JSONResponse({"id": path.id, "name": body.name, "age": body.age})


@app.patch("/book/{id}")
async def patch_book(path: IdModel, body: BookModel):
    return JSONResponse({"id": path.id, "name": body.name, "age": body.age})


@app.delete("/book/{id}")
async def delete_book(path: IdModel):
    return JSONResponse({"id": path.id})


def test_get():
    response = client.get("/book?name=s&age=3")
    assert response.status_code == 200


def test_post():
    data = {"name": "test", "age": 1}
    response = client.post("/book", json=data)
    assert response.status_code == 200
    assert response.json() == data


def test_put():
    data = {"name": "test", "age": 1}
    response = client.put("/book/1", json=data)
    assert response.status_code == 200


def test_patch():
    data = {"name": "test", "age": 1}
    response = client.patch("/book/1", json=data)
    assert response.status_code == 200


def test_delete():
    response = client.delete("/book/1")
    assert response.status_code == 200
