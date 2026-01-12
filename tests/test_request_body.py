from pydantic import BaseModel
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from star_openapi import OpenAPI, RequestBody
from star_openapi.utils import get_model_schema

app = OpenAPI()


client = TestClient(app)


class JsonModel(BaseModel):
    name: str
    age: int


request_body_json = RequestBody(
    description="The json request body",
    content={"application/custom+json": {"schema": get_model_schema(JsonModel)}},
)


@app.post("/json", request_body=request_body_json)
async def get_json(request: Request, body: JsonModel):
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
    return JSONResponse({"message": "Hello World"})


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
