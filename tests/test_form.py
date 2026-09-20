from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from star_openapi import OpenAPI

app = OpenAPI()

client = TestClient(app)


class BookModel(BaseModel):
    str_: str = Field(
        ...,
        description="Name",
        deprecated=True,
        json_schema_extra={
            "example": 1,
            "examples": {"example1": {"value": 1}, "example2": {"value": 2}},
        },
    )
    str_list: list[str]
    int_: int = 0
    int_list: list[int] = []
    float_: float = 0.0
    float_list: list[float] = []
    bool_: bool = True
    bool_list: list[bool] = []
    null: None = None

    model_config = {"extra": "allow"}


@app.post("/book")
async def create_book(form: BookModel):
    return JSONResponse(form.model_dump())


def test_post():
    data = {"str_": "test", "str_list": ["file1", "file2"], "extra": "extra"}
    response = client.post("/book", data=data)
    assert response.status_code == 200


def test_post_with_non_strict():
    data = {
        "str_": 123,
        "str_list": ["file1", 123],
        "int_": "123",
        "int_list": [1, 2, 3],
        "float_": "123.0",
        "float_list": [1.0, "2.0", 3.0],
        "bool_": True,
        "bool_list": [True, 0, "true"],
        "list_": [["1"], ["2"]],
        "null": None,
    }
    response = client.post("/book", data=data)  # type: ignore
    assert response.status_code == 200
