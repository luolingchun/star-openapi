import uvicorn
from pydantic import BaseModel
from starlette.responses import JSONResponse

from star_openapi import OpenAPI

app = OpenAPI()


class BookModel(BaseModel):
    name: str
    files: list[str]


@app.post("/book")
async def create_book(form: BookModel):
    return JSONResponse(form.model_dump())


if __name__ == "__main__":
    print(app.routes)
    uvicorn.run(app)
