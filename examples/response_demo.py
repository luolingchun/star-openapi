from http import HTTPStatus

import uvicorn
from pydantic import BaseModel
from starlette.responses import JSONResponse

from star_openapi import APIRouter, OpenAPI, Response

app = OpenAPI(responses={200: Response(description="OK")})

api = APIRouter(url_prefix="/api", responses={200: Response(description="API OK")})


class BookModel(BaseModel):
    name: str
    age: int


@app.post("/book1")
def response1(body: BookModel):
    return JSONResponse(body.model_json_schema())


@app.post("/book2", responses={HTTPStatus.OK: BookModel})
def response2(body: BookModel):
    return JSONResponse(body.model_json_schema())


@app.post(
    "/book3",
    responses={
        "200": {
            "description": "Custom OK",
            "content": {"application/custom+json": {"schema": BookModel.model_json_schema()}},
        }
    },
)
def response3(body: BookModel):
    return JSONResponse(body.model_json_schema())


@api.post("/book4")
def response4(body: BookModel):
    return JSONResponse(body.model_json_schema())


@api.post("/book5", responses={HTTPStatus.OK: BookModel})
def response5(body: BookModel):
    return JSONResponse(body.model_json_schema())


@api.post(
    "/book6",
    responses={
        "200": {
            "description": "API OK",
            "content": {"application/custom+json": {"schema": BookModel.model_json_schema()}},
        }
    },
)
def response6(body: BookModel):
    return JSONResponse(body.model_json_schema())


app.register_api(api)

if __name__ == "__main__":
    print(app.routes)
    uvicorn.run(app)
