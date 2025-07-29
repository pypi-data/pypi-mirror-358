from pydantic import BaseModel, Field


class SaveImageRequest(BaseModel):
    """Model for save image endpoint request"""

    image_data: str = Field(..., description="Base64 encoded PNG image data.")
    username: str = Field(..., description="Username for file naming.")
    image_type: str = Field(
        ..., description="Type of image (e.g., 'original', 'mask', 'overlay')."
    )
