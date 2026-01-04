from starlette.testclient import TestClient
from starlette.websockets import WebSocket

from star_openapi import OpenAPI
from star_openapi.router import APIRouter

app = OpenAPI()

api = APIRouter(url_prefix="/test")

client = TestClient(app)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_text()
    await websocket.send_text(data)
    await websocket.close()


@api.websocket("/ws")
async def websocket_endpoint_with_api_router(websocket: WebSocket):
    await websocket.accept()
    data = await websocket.receive_text()
    await websocket.send_text(data)
    await websocket.close()


app.register_api(api)


def test_websocket():
    with client.websocket_connect("/ws") as websocket:
        test_message = "Hello WebSocket"
        websocket.send_text(test_message)
        data = websocket.receive_text()
        assert data == test_message


def test_websocket__with_api_router():
    with client.websocket_connect("/test/ws") as websocket:
        test_message = "Hello WebSocket With API Router"
        websocket.send_text(test_message)
        data = websocket.receive_text()
        assert data == test_message
