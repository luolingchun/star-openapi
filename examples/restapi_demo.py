import uvicorn
from pydantic import BaseModel
from starlette.responses import JSONResponse

from star_openapi import OpenAPI

app = OpenAPI()


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


@app.delete("/book/{id}")
async def delete_book(path: IdModel):
    return JSONResponse({"id": path.id})


if __name__ == "__main__":
    print(app.routes)
    uvicorn.run(app)
