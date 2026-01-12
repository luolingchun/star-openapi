**`star_openapi`** based on [Starlette](https://github.com/Kludex/starlette)
and [Pydantic](https://github.com/pydantic/pydantic).

## A Minimal Application

Create `hello.py`:

``` python
import uvicorn
from star_openapi import OpenAPI
from starlette.responses import PlainTextResponse

info = {"title": "Hello API", "version": "1.0.0"}
app = OpenAPI(info=info)


@app.get('/')
async def hello_world():
    return PlainTextResponse('Hello, World!')


if __name__ == '__main__':
    uvicorn.run(app)
```

And then run it:

```shell
python hello.py
```

You will see the output information:

```
INFO:     Started server process [12345]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```

## REST API

You can use **`get`**, **`post`**, **`put`**, **`patch`**, **`delete`** REST API in `star-openapi`.

```python
import uvicorn
from pydantic import BaseModel
from starlette.responses import JSONResponse

from star_openapi import OpenAPI

app = OpenAPI()


class IdModel(BaseModel):
    id: int


class BookModel(BaseModel):
    name: str
    age: int


@app.get("/book")
async def get_book(query: BookModel):
    return JSONResponse(query.model_dump())


@app.post("/book")
async def create_book(body: BookModel):
    return JSONResponse(body.model_dump())


@app.put("/book/{id}")
async def update_book(path: IdModel, body: BookModel):
    return JSONResponse({"id": path.id, "name": body.name, "age": body.age})


@app.delete("/book/{id}")
async def delete_book(path: IdModel):
    return JSONResponse({"id": path.id})


if __name__ == "__main__":
    print(app.routes)
    uvicorn.run(app)
```

## APIRouter

[APIRouter](Reference/APIRouter.md) allows you to organize your API endpoints into logical groups.

```python hl_lines="19"
import uvicorn
from starlette.responses import JSONResponse

from star_openapi import OpenAPI
from star_openapi.router import APIRouter

info = {"title": "Book API", "version": "1.0.0"}
app = OpenAPI(info=info)

api = APIRouter(url_prefix="/api")


@api.post("/book")
async def create_book():
    return JSONResponse({"message": "success"})


# register api
app.register_api(api)

if __name__ == "__main__":
    uvicorn.run(app)

```

## Nested APIRouter

Allow an **APIRouter** to be registered on another **APIRouter**.

```python hl_lines="26 27"
import uvicorn
from starlette.responses import JSONResponse

from star_openapi import OpenAPI
from star_openapi.router import APIRouter

info = {"title": "Book API", "version": "1.0.0"}
app = OpenAPI(info=info)

api = APIRouter(url_prefix="/api/book")
api_english = APIRouter()
api_chinese = APIRouter()


@api_english.get("/english")
async def create_english_book():
    return JSONResponse({"message": "english"})


@api_chinese.get("/chinese")
async def create_chinese_book():
    return JSONResponse({"message": "chinese"})


# register nested api
api.register_api(api_english)
api.register_api(api_chinese)
# register api
app.register_api(api)

if __name__ == "__main__":
    uvicorn.run(app)
```

## Websocket

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