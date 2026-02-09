from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from star_openapi import APIRouter, OpenAPI, RequestBody
from star_openapi.utils import get_model_schema

app = OpenAPI()
api = APIRouter(url_prefix="/api")

client = TestClient(app)


class JsonModel(BaseModel):
    name: str
    age: int


request_body_json = {
    "description": "The json request body",
    "content": {"application/custom+json": {"schema": get_model_schema(JsonModel)}},
}

request_body = RequestBody(
    description="The multi request body",
    content={
        "text/plain": {"schema": {"type": "string"}},
        "text/html": {"schema": {"type": "string"}},
        "image/png": {"schema": {"type": "string", "format": "binary"}},
    },
)


@app.post("/json", request_body=request_body_json)
async def post_json(request: Request, body: JsonModel):
    print(request.headers.get("content-type"))
    print(body.model_json_schema())
    return JSONResponse({"message": "Hello World"})


@app.post("/text", request_body=request_body)
async def post_csv(request: Request):
    print(request.headers.get("content-type"))
    return JSONResponse({"message": "Hello World"})


@api.post("/json", request_body=request_body_json)
async def post_api_json():
    return JSONResponse({"message": "Hello World1"})


@api.post("/text", request_body=request_body)
async def post_api_csv(request: Request):
    print(request.headers.get("content-type"))
    return JSONResponse({"message": "Hello World"})


app.register_api(api)


def test_get_api_book():
    response = client.get("/openapi/openapi.json")
    assert response.status_code == 200
    data = response.json()
    assert list(data["paths"]["/json"]["post"]["requestBody"]["content"].keys()) == ["application/custom+json"]
    assert list(data["paths"]["/text"]["post"]["requestBody"]["content"].keys()) == [
        "text/plain",
        "text/html",
        "image/png",
    ]


def test():
    assert client.post("/json", json={"name": "bob", "age": 3}).status_code == 200
    assert client.post("/text").status_code == 200
    assert client.post("/api/json", json={"name": "bob", "age": 3}).status_code == 200
    assert client.post("/api/text").status_code == 200
