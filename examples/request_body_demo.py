import uvicorn
from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse

from star_openapi import OpenAPI, RequestBody
from star_openapi.utils import get_model_schema

app = OpenAPI()


class BookModel(BaseModel):
    name: str
    age: int


request_body_json = RequestBody(
    description="The json request body",
    content={"application/custom+json": {"schema": get_model_schema(BookModel)}},
)


@app.post("/json", request_body=request_body_json)
async def get_json(request: Request, body: BookModel):
    print(request.headers.get("content-type"))
    print(body.model_json_schema())
    return JSONResponse({"message": "Hello World"})


request_body = RequestBody(
    description="The multi request body",
    content={
        "text/plain": {"schema": {"type": "string"}},
        "text/html": {"schema": {"type": "string"}},
        "image/png": {"schema": {"type": "string", "format": "binary"}},
    },
)


@app.post("/text", request_body=request_body)
async def get_csv(request: Request):
    print(request.headers.get("content-type"))
    data = await request.body()
    print(data)
    return JSONResponse({"message": "Hello World"})


if __name__ == "__main__":
    print(app.routes)
    uvicorn.run(app)
