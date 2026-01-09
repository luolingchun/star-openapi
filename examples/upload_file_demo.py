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
