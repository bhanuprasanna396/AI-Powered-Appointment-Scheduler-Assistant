import logging

from app.models.responses import ProcessResponse
from app.services.entity_service import extract_entities
from app.services.guardrail_service import apply_guardrails
from app.services.normalization_service import normalize_entities
from app.services.ocr_service import extract_raw_text
from app.utils.logging_config import log_stage

logger = logging.getLogger(__name__)


def run_pipeline(text: str | None = None, image_b64: str | None = None) -> ProcessResponse:
    ocr_output = extract_raw_text(text=text, image_b64=image_b64)
    extraction_output = extract_entities(ocr_output.raw_text)
    normalization_output = normalize_entities(
        extraction_output.entities.date_phrase,
        extraction_output.entities.time_phrase,
    )
    final_output = apply_guardrails(extraction_output, normalization_output)

    response = ProcessResponse(
        ocr=ocr_output,
        extraction=extraction_output,
        normalization=normalization_output,
        final=final_output,
    )
    log_stage(logger, "process", response.model_dump())
    return response
