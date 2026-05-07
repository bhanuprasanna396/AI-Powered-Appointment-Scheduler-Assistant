import logging
import re
from datetime import datetime, timedelta
from typing import Optional

import dateparser
from zoneinfo import ZoneInfo

from app.models.responses import NormalizationResponse, NormalizedObject
from app.utils.confidence import average_confidence
from app.utils.logging_config import log_stage

logger = logging.getLogger(__name__)

TZ = "Asia/Kolkata"
WEEKDAY_MAP = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def _base_now() -> datetime:
    return datetime.now(ZoneInfo(TZ))


def _parse_relative_weekday(date_phrase: str) -> Optional[str]:
    phrase = date_phrase.strip().lower()
    match = re.fullmatch(r"(next|this)\s+(monday|tuesday|wednesday|thursday|friday|saturday|sunday)", phrase)
    if not match:
        return None

    qualifier, weekday = match.groups()
    target = WEEKDAY_MAP[weekday]
    now = _base_now().date()
    current = now.weekday()

    days_ahead = (target - current) % 7
    if days_ahead == 0:
        days_ahead = 7

    if qualifier == "this" and target == current:
        days_ahead = 0

    resolved = now + timedelta(days=days_ahead)
    return resolved.isoformat()


def _parse_date(date_phrase: Optional[str]) -> Optional[str]:
    if not date_phrase:
        return None

    relative = _parse_relative_weekday(date_phrase)
    if relative:
        return relative

    parsed = dateparser.parse(
        date_phrase,
        settings={
            "TIMEZONE": TZ,
            "TO_TIMEZONE": TZ,
            "RETURN_AS_TIMEZONE_AWARE": True,
            "PREFER_DATES_FROM": "future",
            "RELATIVE_BASE": _base_now(),
        },
    )
    if not parsed:
        return None
    return parsed.date().isoformat()


def _parse_time(time_phrase: Optional[str]) -> Optional[str]:
    if not time_phrase:
        return None

    phrase = time_phrase.strip().lower()
    am_pm = re.fullmatch(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)", phrase)
    if am_pm:
        hour = int(am_pm.group(1))
        minute = int(am_pm.group(2) or "00")
        period = am_pm.group(3)
        if hour == 12:
            hour = 0
        if period == "pm":
            hour += 12
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return f"{hour:02d}:{minute:02d}"

    twenty_four = re.fullmatch(r"(\d{1,2}):(\d{2})", phrase)
    if twenty_four:
        hour = int(twenty_four.group(1))
        minute = int(twenty_four.group(2))
        if 0 <= hour <= 23 and 0 <= minute <= 59:
            return f"{hour:02d}:{minute:02d}"

    parsed = dateparser.parse(
        time_phrase,
        settings={
            "RELATIVE_BASE": _base_now(),
        },
    )

    if not parsed:
        return None

    return parsed.strftime("%H:%M")


def normalize_entities(date_phrase: Optional[str], time_phrase: Optional[str]) -> NormalizationResponse:
    date_iso = _parse_date(date_phrase)
    time_24h = _parse_time(time_phrase)

    confidence = average_confidence([
        1.0 if date_iso else 0.0,
        1.0 if time_24h else 0.0,
    ])

    result = NormalizationResponse(
        normalized=NormalizedObject(date=date_iso, time=time_24h, tz=TZ),
        normalization_confidence=confidence,
    )
    log_stage(logger, "normalize", result.model_dump())
    return result
