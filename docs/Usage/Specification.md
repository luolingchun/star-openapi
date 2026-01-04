## Specification

If you need the complete Specification, go to http://127.0.0.1:8000/openapi/openapi.json



## info

**`star-openapi`** provide [Swagger UI](https://github.com/swagger-api/swagger-ui), [Redoc](https://github.com/Redocly/redoc), [RapiDoc](https://github.com/rapi-doc/RapiDoc), [RapiPdf](https://mrin9.github.io/RapiPdf/), [Scalar](https://github.com/scalar/scalar) and [Elements](https://github.com/stoplightio/elements) interactive documentation.
Before that, you should know something about the [OpenAPI Specification](https://spec.openapis.org/oas/v3.1.0).

You can use a dictionary to provide the info parameters: **`title`**, **`version`**... , more information sees the [OpenAPI Specification Info Object](https://spec.openapis.org/oas/v3.1.0#info-object).

```python hl_lines="4 5"
from star_openapi import OpenAPI
from star_openapi.router import APIRouter

info = {"title": "book API", "version": "1.0.0"}
app = OpenAPI(info=info)
api = APIRouter(url_prefix='/api')

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app)
```

run it, and go to http://127.0.0.1:8000/openapi, you will see the documentation.

![openapi](../assets/openapi-all.png)

## security_schemes

There are some examples for Security Scheme Object,
more features see the [OpenAPI Specification Security Scheme Object](https://spec.openapis.org/oas/v3.1.0#security-scheme-object).

```python
# Basic Authentication Sample
basic = {
  "type": "http",
  "scheme": "basic"
}
# JWT Bearer Sample
jwt = {
  "type": "http",
  "scheme": "bearer",
  "bearerFormat": "JWT"
}
# API Key Sample
api_key = {
  "type": "apiKey",
  "name": "api_key",
  "in": "header"
}
# Implicit OAuth2 Sample
oauth2 = {
  "type": "oauth2",
  "flows": {
    "implicit": {
      "authorizationUrl": "https://example.com/api/oauth/dialog",
      "scopes": {
        "write:pets": "modify pets in your account",
        "read:pets": "read your pets"
      }
    }
  }
}
security_schemes = {"jwt": jwt, "api_key": api_key, "oauth2": oauth2, "basic": basic}
```

First, you need to define the **security_schemes** and **security** variable:

```python
jwt = {
    "type": "http",
    "scheme": "bearer",
    "bearerFormat": "JWT"
}
security_schemes = {"jwt": jwt}

security = [{"jwt": []}]

app = OpenAPI(info=info, security_schemes=security_schemes)
```

Second, add pass the [**security**](./Route_Operation.md#security) to your api, like this:

```python hl_lines="1"
@app.get('/book/{bid}', tags=[book_tag], security=security)
async def get_book(path: Path, query: BookBody):
    ...
```

result:

![image-20210525165350520](../assets/image-20210525165350520.png)


## doc_ui

You can pass `doc_ui=False` to disable the `OpenAPI spec` when init [`OpenAPI`](../Reference/OpenAPI.md).

```python
app = OpenAPI(info=info, doc_ui=False)
```

You can also use `doc_ui` in endpoint or when initializing [`APIRouter`](../Reference/APIRouter.md).

```python hl_lines="4 9"
api = APIRouter(
    url_prefix='/book',
    doc_ui=False
)

# or

@api.get('/', doc_ui=False)
async def get_book():
    ...
```

## servers

An array of Server Objects, which provide connectivity information to a target server. If the server's property is not provided, or is an empty array, the default value would be a Server Object with an url value of /.

```python
from star_openapi import OpenAPI, Server

servers = [
    Server(url='http://127.0.0.1:8000'),
    Server(url='https://127.0.0.1:8000'),
]
app = OpenAPI(info=info, servers=servers)
```

## external_docs

Allows referencing an external resource for extended documentation.

More information to see [External Documentation Object](https://spec.openapis.org/oas/v3.1.0#external-documentation-object).

```python
from star_openapi import OpenAPI, ExternalDocumentation

external_docs=ExternalDocumentation(
    url="https://www.openapis.org/",
    description="Something great got better, get excited!"
)
app = OpenAPI(info=info, external_docs=external_docs)
```

## openapi_extensions

While the OpenAPI Specification tries to accommodate most use cases, 
additional data can be added to extend the specification at certain points.
See [Specification Extensions](https://spec.openapis.org/oas/v3.1.0#specification-extensions).

It can also be available in every api, goto [Operation](Route_Operation.md#openapi_extensions).

```python hl_lines="3"
import uvicorn
from star_openapi import OpenAPI

app = OpenAPI(info={"title": "API", "version": "1.0.0"}, openapi_extensions={
    "x-google-endpoints": [
        {
            "name": "my-cool-api.endpoints.my-project-id.cloud.goog",
            "allowCors": True
        }
    ]
})

@app.get("/")
async def hello():
    return "ok"


if __name__ == "__main__":
    uvicorn.run(app)
```


## validation error

You can override validation error response use `validation_error_status`, `validation_error_model`
and `validation_error_callback`. 


- validation_error_status: HTTP Status of the response given when a validation error is detected by pydantic. 
                           Defaults to 422.
- validation_error_model: Validation error response model for OpenAPI Specification.
- validation_error_callback: Validation error response callback, the return format corresponds to 
                             the validation_error_model. Receive `ValidationError` and return `Starlette Response`.


```python
from starlette.responses import Response
from pydantic import BaseModel, ValidationError

class ValidationErrorModel(BaseModel):
    code: str
    message: str


def validation_error_callback(e: ValidationError) -> Response:
    validation_error_object = ValidationErrorModel(code="400", message=e.json())
    return Response(
        content=validation_error_object.model_dump_json(),
        media_type="application/json",
        status_code=400
    )


app = OpenAPI(
    info={"title": "API", "version": "1.0.0"},
    validation_error_status=400,
    validation_error_model=ValidationErrorModel,
    validation_error_callback=validation_error_callback
)
```
