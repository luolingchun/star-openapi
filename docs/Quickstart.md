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
from star_openapi import OpenAPI
from starlette.responses import JSONResponse

info = {"title": "Book API", "version": "1.0.0"}
app = OpenAPI(info=info)


@app.get('/book')
async def get_books():
    return JSONResponse(["book1", "book2"])


@app.post('/book')
async def create_book():
    return JSONResponse({"message": "success"})


if __name__ == '__main__':
    uvicorn.run(app)
```

## APIRouter

[APIRouter](Reference/APIRouter.md) allows you to organize your API endpoints into logical groups.

```python hl_lines="18"
import uvicorn
from star_openapi import OpenAPI
from star_openapi.router import APIRouter
from starlette.responses import JSONResponse

info = {"title": "Book API", "version": "1.0.0"}
app = OpenAPI(info=info)

api = APIRouter(url_prefix='/api')


@api.post('/book')
async def create_book():
    return JSONResponse({"message": "success"})


# register api
app.register_api(api)

if __name__ == '__main__':
    uvicorn.run(app)
```

## Nested APIRouter

Allow an **APIRouter** to be registered on another **APIRouter**.

```python hl_lines="25 26"
import uvicorn
from star_openapi import OpenAPI
from star_openapi.router import APIRouter
from starlette.responses import JSONResponse

info = {"title": "Book API", "version": "1.0.0"}
app = OpenAPI(info=info)

api = APIRouter(url_prefix='/api/book')
api_english = APIRouter()
api_chinese = APIRouter()


@api_english.post('/english')
async def create_english_book():
    return JSONResponse({"message": "english"})


@api_chinese.post('/chinese')
async def create_chinese_book():
    return JSONResponse({"message": "chinese"})


# register nested api
api.register_api(api_english)
api.register_api(api_chinese)
# register api
app.register_api(api)

if __name__ == '__main__':
    uvicorn.run(app)
```
