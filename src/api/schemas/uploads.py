from pydantic import BaseModel, Field, field_validator


class PresignRequest(BaseModel):
    filename: str = Field(..., description="Original filename incl. extension")
    mime: str = Field(..., description="MIME type, e.g. application/pdf")

    @field_validator("filename")
    @classmethod
    def no_empty_filename(cls, v):
        if "." not in v:
            raise ValueError("filename must include an extension")
        return v


class PresignResponse(BaseModel):
    url: str
    method: str = "PUT"
    headers: dict = {}
    key: str
    file_extension: str

    @staticmethod
    def from_filename(url: str, key: str, mime: str, headers: dict | None = None):
        ext = key.split("/")[-1].split(".")[-1].lower()
        return PresignResponse(
            url=url, key=key, headers=headers or {"Content-Type": mime}, file_extension=ext
        )


class IngestPDFResponse(BaseModel):
    message: str = Field(..., description="Success message")
    file_path: str = Field(..., description="Path where PDF was saved")
    chunks_ingested: int = Field(default=0, description="Number of document chunks ingested")

