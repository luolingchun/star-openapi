from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from star_openapi import OpenAPI
from star_openapi.router import APIRouter

app = OpenAPI()

client = TestClient(app)

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
