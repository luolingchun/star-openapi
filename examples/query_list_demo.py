import uvicorn
from pydantic import BaseModel
from starlette.responses import JSONResponse

from star_openapi import OpenAPI
from star_openapi.router import APIRouter

app = OpenAPI()

api = APIRouter(url_prefix="/api")


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

if __name__ == "__main__":
    print(app.routes)
    uvicorn.run(app)
