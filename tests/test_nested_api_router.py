from starlette.responses import JSONResponse
from starlette.testclient import TestClient
from starlette.websockets import WebSocket

from star_openapi import OpenAPI
from star_openapi.router import APIRouter

tags = [{"name": "english", "description": "english description"}]

app = OpenAPI()

client = TestClient(app)

api = APIRouter(url_prefix="/api/book")
api_english = APIRouter()
api_chinese = APIRouter()


@api_english.get("/english", tags=tags)
async def get_english_book():
    return JSONResponse({"message": "english"})


@api_chinese.get("/chinese")
async def get_chinese_book():
    return JSONResponse({"message": "chinese"})


@api_chinese.websocket("/ws")
async def websocket_endpoint_with_api_router(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_text()
    await websocket.send_text(data)
    await websocket.close()


# register nested api
api.register_api(api_english)
api.register_api(api_chinese)
# register api
app.register_api(api)


def test_english():
    response = client.get("/api/book/english")
    data = response.json()

    assert response.status_code == 200
    assert data == {"message": "english"}


def test_chinese():
    response = client.get("/api/book/chinese")
    data = response.json()

    assert response.status_code == 200
    assert data == {"message": "chinese"}


def test_api_ws():
    with client.websocket_connect("/api/book/ws") as websocket:
        test_message = "Hello WebSocket"
        websocket.send_text(test_message)
        data = websocket.receive_text()
        assert data == test_message
