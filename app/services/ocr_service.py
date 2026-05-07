import base64
import io
import logging
from typing import Optional

import pytesseract
from PIL import Image
from pytesseract import Output

from app.models.responses import OCRResponse
from app.utils.confidence import clamp_confidence
from app.utils.logging_config import log_stage
from app.utils.text_cleaning import clean_ocr_text

logger = logging.getLogger(__name__)


def _decode_image(image_b64: str) -> Image.Image:
    if "," in image_b64 and "base64" in image_b64.split(",", 1)[0]:
        image_b64 = image_b64.split(",", 1)[1]

    try:
        image_bytes = base64.b64decode(image_b64, validate=True)
    except Exception as exc:  # noqa: BLE001
        raise ValueError("Invalid base64 image payload.") from exc

    try:
        return Image.open(io.BytesIO(image_bytes))
    except Exception as exc:  # noqa: BLE001
        raise ValueError("Unable to decode image content.") from exc


def _ocr_from_image(image_b64: str) -> tuple[str, float]:
    image = _decode_image(image_b64)

    data = pytesseract.image_to_data(image, output_type=Output.DICT)
    words = []
    confidences = []
    for txt, conf in zip(data.get("text", []), data.get("conf", [])):
        if txt and txt.strip():
            words.append(txt.strip())
        try:
            conf_value = float(conf)
            if conf_value >= 0:
                confidences.append(conf_value)
        except Exception:  # noqa: BLE001
            continue

    if not words:
        raise RuntimeError("OCR could not extract readable text.")

    raw_text = " ".join(words)
    mean_conf = sum(confidences) / len(confidences) / 100 if confidences else 0.5
    return clean_ocr_text(raw_text), clamp_confidence(mean_conf)


def extract_raw_text(text: Optional[str] = None, image_b64: Optional[str] = None) -> OCRResponse:
    if text and text.strip():
        cleaned = clean_ocr_text(text)
        result = OCRResponse(raw_text=cleaned, confidence=0.98)
        log_stage(logger, "ocr", result.model_dump())
        return result

    if image_b64:
        raw_text, conf = _ocr_from_image(image_b64)
        result = OCRResponse(raw_text=raw_text, confidence=conf)
        log_stage(logger, "ocr", result.model_dump())
        return result

    raise ValueError("Either text or image must be provided for OCR stage.")
