import logging
import re
from typing import Optional

from app.models.responses import EntityExtractionResponse, EntityObject
from app.services.llm_service import LLMClient
from app.utils.confidence import average_confidence
from app.utils.logging_config import log_stage

logger = logging.getLogger(__name__)

KNOWN_DEPARTMENTS = {
    "dentist": "Dentistry",
    "dental": "Dentistry",
    "cardio": "Cardiology",
    "cardiology": "Cardiology",
    "derma": "Dermatology",
    "dermatology": "Dermatology",
    "neuro": "Neurology",
    "neurology": "Neurology",
    "ortho": "Orthopedics",
    "orthopedic": "Orthopedics",
    "orthopedics": "Orthopedics",
    "ent": "ENT",
    "pediatric": "Pediatrics",
    "pediatrics": "Pediatrics",
    "gyn": "Gynecology",
    "gynecology": "Gynecology",
    "ophthalmology": "Ophthalmology",
    "eye": "Ophthalmology",
    "general": "General Medicine",
}

DATE_REGEX = re.compile(
    r"\b(?:today|tomorrow|next\s+\w+|this\s+\w+|\d{1,2}[/-]\d{1,2}(?:[/-]\d{2,4})?|\w+\s+\d{1,2}(?:st|nd|rd|th)?)\b",
    re.IGNORECASE,
)
TIME_REGEX = re.compile(
    r"\b(?:at\s*)?(\d{1,2}(?::\d{2})?\s*(?:am|pm)|\d{1,2}:\d{2})\b",
    re.IGNORECASE,
)

llm_client = LLMClient()


def _extract_department(text: str) -> Optional[str]:
    lowered = text.lower()
    for key, mapped in KNOWN_DEPARTMENTS.items():
        if re.search(rf"\b{re.escape(key)}\b", lowered):
            return mapped
    return None


def _fallback_extract(raw_text: str) -> EntityObject:
    date_match = DATE_REGEX.search(raw_text)
    time_match = TIME_REGEX.search(raw_text)
    department = _extract_department(raw_text)

    time_phrase = None
    if time_match:
        time_phrase = time_match.group(1).strip()

    return EntityObject(
        date_phrase=date_match.group(0).strip() if date_match else None,
        time_phrase=time_phrase,
        department=department,
    )


def extract_entities(raw_text: str) -> EntityExtractionResponse:
    llm_entities = llm_client.extract_entities(raw_text)

    if llm_entities:
        entities = EntityObject(
            date_phrase=llm_entities.get("date_phrase"),
            time_phrase=llm_entities.get("time_phrase"),
            department=llm_entities.get("department"),
        )
        source_bonus = 0.1
    else:
        entities = _fallback_extract(raw_text)
        source_bonus = 0.0

    field_scores = [
        1.0 if entities.date_phrase else 0.0,
        1.0 if entities.time_phrase else 0.0,
        1.0 if entities.department else 0.0,
    ]
    confidence = average_confidence(field_scores) * 0.85 + source_bonus
    confidence = min(1.0, round(confidence, 2))

    result = EntityExtractionResponse(entities=entities, entities_confidence=confidence)
    log_stage(logger, "extract", result.model_dump())
    return result
