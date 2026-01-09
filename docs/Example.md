## Simple Demo

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


@app.get("/book", summary="get books", tags=[book_tag])
async def get_book(query: BookModel):
    """
    get all books
    """
    print(query.model_dump_json())
    return JSONResponse({"message": "Hello World"})


if __name__ == "__main__":
    print(app.routes)
    uvicorn.run(app)
```

## REST Demo

```python
from http import HTTPStatus

from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

from star_openapi import Info, OpenAPI, Tag

info = Info(title="book API", version="1.0.0")
# Basic Authentication Sample
basic = {"type": "http", "scheme": "basic"}
# JWT Bearer Sample
jwt = {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
# API Key Sample
api_key = {"type": "apiKey", "name": "api_key", "in": "header"}
# Implicit OAuth2 Sample
oauth2 = {
    "type": "oauth2",
    "flows": {
        "implicit": {
            "authorizationUrl": "https://example.com/api/oauth/dialog",
            "scopes": {"write:pets": "modify pets in your account", "read:pets": "read your pets"},
        }
    },
}
security_schemes = {"jwt": jwt, "api_key": api_key, "oauth2": oauth2, "basic": basic}


class NotFoundResponse(BaseModel):
    code: int = Field(-1, description="Status Code")
    message: str = Field("Resource not found!", description="Exception Information")


app = OpenAPI(info=info, security_schemes=security_schemes)

book_tag = Tag(name="book", description="Some Book")
security = [{"jwt": []}, {"oauth2": ["write:pets", "read:pets"]}]


class BookPath(BaseModel):
    id: int = Field(..., description="book id")


class BookQuery(BaseModel):
    age: int | None = Field(None, description="Age")
    s_list: list[str] = Field(None, alias="s_list[]", description="some array")


class BookBody(BaseModel):
    age: int | None = Field(..., ge=2, le=4, description="Age")
    author: str | None = Field(None, min_length=2, max_length=4, description="Author")


class BookBodyWithID(BaseModel):
    id: int = Field(..., description="book id")
    age: int | None = Field(None, ge=2, le=4, description="Age")
    author: str = Field(None, min_length=2, max_length=4, description="Author")


class BookResponse(BaseModel):
    code: int = Field(0, description="Status Code")
    message: str = Field("ok", description="Exception Information")
    data: BookBodyWithID | None


@app.get(
    "/book/{id}",
    tags=[book_tag],
    summary="new summary",
    description="new description",
    security=security,
)
async def get_book(path: BookPath):
    """Get a book
    to get some book by id, like:
    http://localhost:8000/book/3
    """
    if path.id == 4:
        return NotFoundResponse().model_dump_json(), 404
    return JSONResponse({"code": 0, "message": "ok", "data": {"id": path.id, "age": 3, "author": "no"}})


# set doc_ui False disable openapi UI
@app.get("/book", doc_ui=True, deprecated=True)
async def get_books(query: BookQuery):
    """get books
    to get all books
    """
    print(query)
    return JSONResponse(
        {
            "code": 0,
            "message": "ok",
            "data": [{"id": 1, "age": query.age, "author": "a1"}, {"id": 2, "age": query.age, "author": "a2"}],
        }
    )


@app.post("/book", tags=[book_tag])
async def create_book(body: BookBody):
    print(body)
    return JSONResponse({"code": 0, "message": "ok"})


@app.put("/book/{id}", tags=[book_tag])
async def update_book(path: BookPath, body: BookBody):
    print(path)
    print(body)
    return JSONResponse({"code": 0, "message": "ok"})


@app.delete("/book/{id}", tags=[book_tag], doc_ui=False)
async def delete_book(path: BookPath):
    print(path)
    return JSONResponse({"code": 0, "message": "ok"})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app)
```

## APIRouter

```python
import uvicorn
from pydantic import BaseModel
from starlette.responses import JSONResponse

from star_openapi import OpenAPI
from star_openapi.router import APIRouter

app = OpenAPI()

api1 = APIRouter(url_prefix="/api1")
api2 = APIRouter(url_prefix="/api2")


class IdModel(BaseModel):
    id: int


class BookModel(BaseModel):
    name: str
    age: int


@api1.get("/book")
async def ge_book():
    return JSONResponse({"message": "Hello World1"})


@api1.post("/book")
async def create_book(body: BookModel):
    return JSONResponse(body.model_dump())


@api1.put("/book/{id}")
async def update_book(path: IdModel, body: BookModel):
    return JSONResponse({"id": path.id, "name": body.name, "age": body.age})


@api1.delete("/book/{id}")
async def delete_book(path: IdModel):
    return JSONResponse({"id": path.id})


@api2.get("/")
async def get_api2():
    return JSONResponse({"message": "Hello World2"})


api1.register_api(api2)

app.register_api(api1)
app.register_api(api2)

if __name__ == "__main__":
    print(app.routes)
    uvicorn.run(app)
```

## Upload File Demo

```python
import uvicorn
from pydantic import BaseModel, Field
from starlette.responses import JSONResponse

from star_openapi import OpenAPI, UploadFile

app = OpenAPI()


class UploadFileForm(BaseModel):
    file: UploadFile
    file_type: str = Field(None, description="File Type")


class UploadFilesForm(BaseModel):
    files: list[UploadFile]
    file_type: str = Field(None, description="File Type")


@app.post("/upload/file")
async def upload_file(form: UploadFileForm):
    print(form.file.filename)
    print(form.file_type)

    content = await form.file.read()
    with open(form.file.filename, "wb") as f:
        f.write(content)
    return JSONResponse({"code": 0, "message": "ok"})


@app.post("/upload/files")
async def upload_files(form: UploadFilesForm):
    print(form.files)
    print(form.file_type)
    return JSONResponse({"code": 0, "message": "ok"})


if __name__ == "__main__":
    print(app.routes)
    uvicorn.run(app)
```

## Websocket Demo

```python
import uvicorn
from starlette.websockets import WebSocket

from star_openapi import OpenAPI

app = OpenAPI()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(data)


if __name__ == "__main__":
    uvicorn.run("websocket:app", reload=True)
```

## A complete project

see [star-api-demo](https://github.com/luolingchun/star-api-demo)