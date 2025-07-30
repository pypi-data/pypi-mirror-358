from pydantic import BaseModel, ConfigDict


class ImageResponse(BaseModel):
    model_config = ConfigDict(extra="allow")
    content: bytes
    content_type: str


__all__ = ["ImageResponse"]
