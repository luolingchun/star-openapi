<div align="center">
    <a href="https://luolingchun.github.io/star-openapi/" target="_blank">
        <img class="off-glb" src="https://raw.githubusercontent.com/luolingchun/star-openapi/main/docs/images/logo-text.svg" 
             width="60%" height="auto" alt="logo">
    </a>
</div>
<p align="center">
    <em>A simple async API framework based on Starlette.</em>
</p>
<p align="center">
    <a href="https://github.com/luolingchun/star-openapi/actions/workflows/tests.yml" target="_blank">
        <img class="off-glb" src="https://img.shields.io/github/actions/workflow/status/luolingchun/star-openapi/tests.yml?branch=main" alt="test">
    </a>
    <a href="https://pypi.org/project/star-openapi/" target="_blank">
        <img class="off-glb" src="https://img.shields.io/pypi/v/star-openapi" alt="pypi">
    </a>
    <a href="https://pypistats.org/packages/star-openapi" target="_blank">
        <img class="off-glb" src="https://img.shields.io/pypi/dm/star-openapi" alt="pypistats">
    </a>
    <a href="https://pypi.org/project/star-openapi/" target="_blank">
        <img class="off-glb" src="https://img.shields.io/pypi/pyversions/star-openapi" alt="pypi versions">
    </a>
</p>

**Star OpenAPI** is a web API framework based on **Starlette**. It uses **Pydantic** to verify data and automatic
generation of interaction documentation.

The key features are:

- **Easy to code:** Easy to use and easy to learn

- **Standard document specification:** Based on [OpenAPI Specification](https://spec.openapis.org/oas/v3.1.0)

- **Interactive OpenAPI documentation:**
  [Swagger](https://github.com/swagger-api/swagger-ui), [Redoc](https://github.com/Redocly/redoc), [RapiDoc](https://github.com/rapi-doc/RapiDoc), [RapiPdf](https://mrin9.github.io/RapiPdf/), [Scalar](https://github.com/scalar/scalar), [Elements](https://github.com/stoplightio/elements)

- **Data validation:** Fast data verification based on [Pydantic](https://github.com/pydantic/pydantic)

- **Websocket**: Support for websocket

## Requirements

Python 3.11+

star-openapi is dependent on the following libraries:

- [Starlette](https://github.com/Kludex/starlette) for the web app.
- [Pydantic](https://github.com/pydantic/pydantic) for the data validation.

## Installation

```bash
pip install -U star-openapi[swagger]
```

<details markdown="block">
<summary>Optional dependencies</summary>

- [`httpx`](https://github.com/encode/httpx/) - Required if you want to use the `TestClient`.
- [`python-multipart`](https://github.com//kludex/python-multipart) - Required if you want to support form parsing, with
  `request.form()`.
- [`itsdangerous`](https://github.com/pallets/itsdangerous) - Required for `SessionMiddleware` support.
- [`pyyaml`](https://github.com/yaml/pyyaml) - Required for `SchemaGenerator` support.

You can install all of these with `pip install star-openapi[full]`.

- [star-openapi-plugins](https://github.com/luolingchun/star-openapi-plugins) Provide OpenAPI UI for star-openapi.

You can install all of these with `pip install star-openapi[swagger,redoc,rapidoc,rapipdf,scalar,elements]`.

</details>

## A Simple Example

Here's a simple example, further go to the [Example](https://luolingchun.github.io/star-openapi/v0.x/Example/).

```python
import uvicorn
from pydantic import BaseModel
from starlette.responses import JSONResponse

from star_openapi import OpenAPI

info = {"title": "Star API", "version": "1.0.0"}
app = OpenAPI(info=info)

book_tag = {"name": "book", "description": "book tag"}


class BookModel(BaseModel):
    name: str
    age: int


@app.post("/book", summary="get books", tags=[book_tag])
async def create_user(body: BookModel):
    """
    get all books
    """
    print(body.model_dump_json())
    return JSONResponse({"message": "Hello World"})


if __name__ == "__main__":
    print(app.routes)
    uvicorn.run(app)
```

## API Document

Run the [simple example](https://github.com/luolingchun/star-openapi/blob/main/examples/simple_demo.py), and go
to http://127.0.0.1:8000/openapi.

> OpenAPI UI plugins are optional dependencies that require manual installation.
>
> `pip install -U star-openapi[swagger,redoc,rapidoc,rapipdf,scalar,elements]`
>
> More optional ui templates goto the document
> about [UI_Templates](https://luolingchun.github.io/star-openapi/v0.x/Usage/UI_Templates/).

![openapi](https://raw.githubusercontent.com/luolingchun/star-openapi/main/docs/assets/openapi-all.png)
