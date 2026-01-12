## responses

By default, you can pass a `BaseModel` to automatically generate the `application/json` schema.

```python
from pydantic import BaseModel

from star_openapi import OpenAPI

app = OpenAPI()


class BookModel(BaseModel):
    name: str
    age: int


@app.post("/book2", responses={200: BookModel})
def response(body: BookModel):
    ...
```

You can customize the schema:

```python
@app.post(
    "/book3",
    responses={
        "200": {
            "description": "Custom OK",
            "content": {"application/custom+json": {"schema": BookModel.model_json_schema()}},
        }
    },
)
def response(body: BookModel):
    ...
```

Other content types, such as `text/csv`

```python
from http import HTTPStatus
from starlette.requests import Request


@app.post(
    "/book3",
    responses={
        HTTPStatus.OK: {
            "description": "Custom csv OK",
            "content": {"text/csv": {"schema": {"type": "string"}}}
        }
    },
)
def response(request: Request):
    ...
```

you can use `string`, `int`, and `HTTPStatus` as response's key.