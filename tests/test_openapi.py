from pydantic import BaseModel
from starlette.testclient import TestClient

from star_openapi import APIRouter, OpenAPI, ValidationErrorModel
from tests.config import JWT

servers = [{"url": "https://www.openapis.org/", "description": "openapi"}]
external_docs = {"url": "https://www.openapis.org/", "description": "Something great got better, get excited!"}
tags = [{"name": "book", "description": "book description"}]


class ErrorModel(BaseModel):
    code: int
    message: str


class NewValidationErrorModel(ValidationErrorModel):
    error: ErrorModel | None = None


app = OpenAPI(
    servers=servers,
    external_docs=external_docs,
    validation_error_model=NewValidationErrorModel,
)

api = APIRouter(url_prefix="/api", tags=[{"name": "api name"}])

client = TestClient(app)


@app.get(
    "/book1",
    doc_ui=False,
)
async def get_book1(): ...


@app.post(
    "/book2",
    summary="Book2",
    description="Book description",
    external_docs=external_docs,
    deprecated=False,
    security=JWT,
    servers=servers,
    tags=tags,
    responses={"422": ErrorModel},
)
async def get_book2(): ...


@api.get(
    "/book1",
    doc_ui=False,
)
async def get_api_book1(): ...


@api.get(
    "/book2",
    external_docs=external_docs,
    deprecated=False,
    security=JWT,
    servers=servers,
    tags=tags,
    responses={"422": ErrorModel},
)
def get_api_book2(): ...


app.register_api(api)


def test_openapi():
    response = client.get("/openapi/openapi.json")
    assert response.status_code == 200
    client.get("/openapi/openapi.json")
