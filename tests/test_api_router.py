from pydantic import BaseModel
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from star_openapi import OpenAPI
from star_openapi.router import APIRouter

app = OpenAPI()

client = TestClient(app)


api1 = APIRouter(url_prefix="/api1")
api2 = APIRouter(url_prefix="/api2")


class IdModel(BaseModel):
    id: int


class BookModel(BaseModel):
    name: str
    age: int


@api1.get("/book")
async def get_api1():
    return JSONResponse({"message": "Hello World1"})


@api1.post("/book")
async def create_book(body: BookModel):
    return JSONResponse(body.model_dump())


@api1.put("/book/{id}")
async def update_book(path: IdModel, body: BookModel):
    return JSONResponse({"id": path.id, "name": body.name, "age": body.age})


@api1.patch("/book/{id}")
async def patch_book(path: IdModel, body: BookModel):
    return JSONResponse({"id": path.id, "name": body.name, "age": body.age})


@api1.delete("/book/{id}")
async def delete_book(path: IdModel):
    return JSONResponse({"id": path.id})


@api2.get("/")
async def get_api2():
    return JSONResponse({"message": "Hello World2"})


api1.register_api(api2)

app.register_api(api1)
app.register_api(api2)


def test_get():
    response = client.get("/api1/book")
    assert response.status_code == 200


def test_post():
    data = {"name": "test", "age": 1}
    response = client.post("/api1/book", json=data)
    assert response.status_code == 200
    assert response.json() == data


def test_put():
    data = {"name": "test", "age": 1}
    response = client.put("/api1/book/1", json=data)
    assert response.status_code == 200


def test_patch():
    data = {"name": "test", "age": 1}
    response = client.patch("/api1/book/1", json=data)
    assert response.status_code == 200


def test_delete():
    response = client.delete("/api1/book/1")
    assert response.status_code == 200


def test_api2():
    response = client.get("/api2")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World2"}


def test_api1_api2():
    response = client.get("/api1/api2")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello World2"}
