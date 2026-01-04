import uvicorn
from pydantic import BaseModel
from starlette.responses import JSONResponse

from star_openapi import OpenAPI
from star_openapi.router import APIRouter

app = OpenAPI()

api1 = APIRouter(url_prefix="/api1")
api2 = APIRouter(url_prefix="/api2")


class IdModel(BaseModel):
    id: int


class BookModel(BaseModel):
    name: str
    age: int


@api1.get("/book")
async def ge_book():
    return JSONResponse({"message": "Hello World1"})


@api1.post("/book")
async def create_book(body: BookModel):
    return JSONResponse(body.model_dump())


@api1.put("/book/{id}")
async def update_book(path: IdModel, body: BookModel):
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

if __name__ == "__main__":
    print(app.routes)
    uvicorn.run(app)
