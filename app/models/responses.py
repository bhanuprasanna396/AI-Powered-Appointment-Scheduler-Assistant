from typing import Optional

from pydantic import BaseModel


class OCRResponse(BaseModel):
    raw_text: str
    confidence: float


class EntityObject(BaseModel):
    date_phrase: Optional[str] = None
    time_phrase: Optional[str] = None
    department: Optional[str] = None


class EntityExtractionResponse(BaseModel):
    entities: EntityObject
    entities_confidence: float


class NormalizedObject(BaseModel):
    date: Optional[str] = None
    time: Optional[str] = None
    tz: str = "Asia/Kolkata"


class NormalizationResponse(BaseModel):
    normalized: NormalizedObject
    normalization_confidence: float


class Appointment(BaseModel):
    department: str
    date: str
    time: str
    tz: str = "Asia/Kolkata"


class GuardrailResponse(BaseModel):
    status: str
    message: Optional[str] = None
    appointment: Optional[Appointment] = None


class ProcessResponse(BaseModel):
    ocr: OCRResponse
    extraction: EntityExtractionResponse
    normalization: NormalizationResponse
    final: GuardrailResponse
