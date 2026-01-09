## Request declaration

First, you need to import `BaseModel` from `pydantic`:

```python
from pydantic import BaseModel
```

### path

Request parameter in rules，**`@app.get('/book/{id}')`**.

You have to declare **path** model as a class that inherits from  **`BaseModel`**:

```python hl_lines="6"
class BookPath(BaseModel):
    id: int = Field(..., description="book id")


@app.get("/book/{id}", tags=[book_tag], security=security)
async def get_book(path: BookPath):
    ...
```

### query

Receive request query parameters.

like [path](#path), you need pass **`query`** to view function.

```python hl_lines="7"
class BookQuery(BaseModel):
    age: int | None = Field(..., ge=2, le=4, description="Age")
    author: str = Field(None, min_length=2, max_length=4, description="Author")


@app.get('/book/{id}', tags=[book_tag], security=security)
async def get_book(path: BookPath, query: BookQuery):
    ...
```

### form

Receive request form data and files.

```python hl_lines="7"
class UploadFileForm(BaseModel):
    file: UploadFile  # request.files["file"]
    file_type: str = Field(None, description="File type")


@app.post("/upload")
async def upload_file(form: UploadFileForm):
    ...
```

### body

Receive request body.

```python hl_lines="7"
class BookBody(BaseModel):
    age: int | None = Field(..., ge=2, le=4, description="Age")
    author: str = Field(None, min_length=2, max_length=4, description="Author")


@app.post("/book", tags=[book_tag])
async def create_book(body: BookBody):
    ...
```

### header

Receive request headers.

### cookie

Receive request cookies.

### request

Receive request from **starlette.requests.Request**.

## Request model

First, you need to define a [pydantic](https://github.com/pydantic/pydantic) model:

```python
class BookQuery(BaseModel):
    age: int = Field(..., ge=2, le=4, description="Age")
    author: str = Field(None, description="Author")
```

More information to see [BaseModel](https://docs.pydantic.dev/latest/usage/models/), and you
can [Customize the Field](https://docs.pydantic.dev/latest/usage/fields/).

However, you can also use **Field** to extend [Parameter Object](https://spec.openapis.org/oas/v3.1.0#parameter-object).
Here is an example:

`age` with **`example`** and `author` with **`deprecated`**.

```python
class BookQuery(BaseModel):
    age: int = Field(..., ge=2, le=4, description="Age", json_schema_extra={"example": 3})
    author: str = Field(None, description="Author", json_schema_extra={"deprecated": True})
```

Magic:

![](../assets/Snipaste_2022-09-04_10-10-03.png)

More available fields to see [Parameter Object Fixed Fields](https://spec.openapis.org/oas/v3.1.0#fixed-fields-9).

## RequestBody

Sometimes, you may need to customize the Content-Type in the request body.

!!! warning

    `request_body` may conflict with the `body` and `form` keyword, so try not to use them together unless the 
    content type wants to be the same.

```python
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


if __name__ == "__main__":
    print(app.routes)
    uvicorn.run(app)
```