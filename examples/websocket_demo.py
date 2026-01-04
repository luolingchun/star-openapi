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
