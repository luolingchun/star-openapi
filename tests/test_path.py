from enum import Enum

from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from star_openapi import OpenAPI

app = OpenAPI()

client = TestClient(app)


class Language(str, Enum):
    cn = "Chinese"
    en = "English"


class BookPath(BaseModel):
    name: Language = Field(
        ...,
        description="Name",
        deprecated=True,
        json_schema_extra={
            "example": 1,
            "examples": {"example1": {"value": 1}, "example2": {"value": 2}},
        },
    )


@app.get("/book/{name}")
def get_path(path: BookPath):
    return JSONResponse(path.model_dump(by_alias=True))


def test_path():
    r = client.get("/openapi/openapi.json")
    _json = r.json()
    assert r.status_code == 200
    assert _json["components"]["schemas"].get("Language") is not None

    r = client.get("/book/English")
    assert r.status_code == 200
    assert r.json() == {"name": "English"}
