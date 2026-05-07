from typing import Optional

from pydantic import BaseModel, Field, model_validator


class ProcessRequest(BaseModel):
    text: Optional[str] = Field(default=None, description="Raw appointment request text")
    image: Optional[str] = Field(default=None, description="Base64 image string")

    @model_validator(mode="after")
    def validate_input(self) -> "ProcessRequest":
        self.text = self.text.strip() if self.text and self.text.strip() else None
        self.image = self.image.strip() if self.image and self.image.strip() else None

        if not self.text and not self.image:
            raise ValueError("Provide exactly one input: either 'text' or 'image'.")

        if self.text and self.image:
            raise ValueError("Provide only one input at a time: either 'text' or 'image'.")

        return self


class OCRRequest(ProcessRequest):
    pass


class ExtractRequest(BaseModel):
    raw_text: str = Field(..., min_length=1)


class NormalizeRequest(BaseModel):
    date_phrase: Optional[str] = None
    time_phrase: Optional[str] = None
    department: Optional[str] = None
