from pydantic import BaseModel, Field
from starlette.responses import JSONResponse
from starlette.testclient import TestClient

from star_openapi import OpenAPI, UploadFile

app = OpenAPI()


client = TestClient(app)


class UploadFileForm(BaseModel):
    file: UploadFile
    file_type: str = Field(None, description="File Type")


class UploadFilesForm(BaseModel):
    files: list[UploadFile]
    file_type: str = Field(None, description="File Type")


@app.post("/upload/file")
async def upload_file(form: UploadFileForm):
    assert form.file_type == "t"
    assert await form.file.read() == b"xxx"
    return JSONResponse({"code": 0, "message": "ok"})


@app.post("/upload/files")
async def upload_files(form: UploadFilesForm):
    print(form.files)
    print(form.file_type)
    return JSONResponse({"code": 0, "message": "ok"})


def test_upload_file():
    from io import BytesIO

    data = {"file_type": "t"}

    files = {"file": ("test.txt", BytesIO(b"xxx"), "text/plain")}

    resp = client.post("/upload/file", data=data, files=files)

    assert resp.status_code == 200


def test_get_api_book():
    from io import BytesIO

    data = {"file_type": "t"}

    files = [
        ("files", ("file1.txt", BytesIO(b"file1"), "text/plain")),
        ("files", ("file2.txt", BytesIO(b"file2"), "text/plain")),
    ]

    resp = client.post("/upload/files", data=data, files=files)

    assert resp.status_code == 200
