from app.services.entity_service import extract_entities
from app.services.guardrail_service import apply_guardrails
from app.services.normalization_service import normalize_entities
from app.services.ocr_service import extract_raw_text
from app.utils.text_cleaning import clean_ocr_text


def test_ocr_text_passthrough():
    result = extract_raw_text(text="book dentist nxt Friday @ 3 pm")
    assert "next Friday" in result.raw_text
    assert result.confidence >= 0.9


def test_entity_extraction_fallback():
    result = extract_entities("Book dentist next Friday at 3pm")
    assert result.entities.date_phrase is not None
    assert result.entities.time_phrase is not None
    assert result.entities.department == "Dentistry"
    assert result.entities_confidence > 0.5


def test_normalization_stage():
    result = normalize_entities("next Friday", "3pm")
    assert result.normalized.date is not None
    assert result.normalized.time == "15:00"
    assert result.normalized.tz == "Asia/Kolkata"


def test_guardrail_needs_clarification_when_missing_department():
    extraction = extract_entities("Book next Friday at 3pm")
    normalization = normalize_entities(extraction.entities.date_phrase, extraction.entities.time_phrase)
    final = apply_guardrails(extraction, normalization)
    assert final.status == "needs_clarification"


def test_ocr_time_token_correction_for_zpm():
    cleaned = clean_ocr_text("Book dentist next Friday at Zpm")
    assert "7pm" in cleaned


def test_entity_extraction_from_ocr_noisy_time():
    result = extract_entities(clean_ocr_text("Book dentist next Friday at Zpm"))
    assert result.entities.time_phrase == "7pm"
