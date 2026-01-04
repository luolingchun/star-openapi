import uvicorn
from pydantic import BaseModel
from starlette.responses import JSONResponse

from star_openapi import OpenAPI

info = {"title": "Star API", "version": "1.0.0"}
app = OpenAPI(info=info)

book_tag = {"name": "book", "description": "book tag"}


class TestModel(BaseModel):
    name: str
    age: int


@app.post("/book", summary="get books", tags=[book_tag])
async def create_user(body: TestModel):
    """
    get all books
    """
    print(body.model_dump_json())
    return JSONResponse({"message": "Hello World"})

if __name__ == "__main__":
    print(app.routes)
    uvicorn.run(app)
