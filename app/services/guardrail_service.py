from app.models.responses import Appointment, EntityExtractionResponse, GuardrailResponse, NormalizationResponse


AMBIGUOUS_TERMS = {
    "sometime",
    "later",
    "next week",
    "weekend",
    "morning",
    "afternoon",
    "evening",
}


def apply_guardrails(extraction: EntityExtractionResponse, normalization: NormalizationResponse) -> GuardrailResponse:
    entities = extraction.entities
    normalized = normalization.normalized

    date_phrase = (entities.date_phrase or "").lower()
    time_phrase = (entities.time_phrase or "").lower()

    ambiguous = any(term in date_phrase for term in AMBIGUOUS_TERMS) or any(
        term in time_phrase for term in AMBIGUOUS_TERMS
    )

    missing_required = not entities.department or not normalized.date or not normalized.time

    if missing_required or ambiguous:
        return GuardrailResponse(
            status="needs_clarification",
            message="Ambiguous date/time or department",
        )

    appointment = Appointment(
        department=entities.department,
        date=normalized.date,
        time=normalized.time,
        tz=normalized.tz,
    )

    return GuardrailResponse(status="ok", appointment=appointment)
