import re


OCR_DIGIT_MAP = {
    "O": "0",
    "o": "0",
    "I": "1",
    "l": "1",
    "S": "5",
    "s": "5",
    "B": "8",
    "Z": "7",
    "z": "7",
}


def _normalize_ocr_time_token(match: re.Match[str]) -> str:
    hour_raw = match.group("hour")
    minute_raw = match.group("minute")
    meridiem = match.group("meridiem")

    hour_digits = "".join(OCR_DIGIT_MAP.get(ch, ch) for ch in hour_raw)
    if not hour_digits.isdigit():
        return match.group(0)

    hour = int(hour_digits)
    if hour < 1 or hour > 12:
        return match.group(0)

    if minute_raw:
        minute_digits = "".join(OCR_DIGIT_MAP.get(ch, ch) for ch in minute_raw)
        if not minute_digits.isdigit():
            return match.group(0)
        minute = int(minute_digits)
        if minute < 0 or minute > 59:
            return match.group(0)
        return f"{hour}:{minute_digits} {meridiem}"

    return f"{hour}{meridiem}"


def clean_ocr_text(text: str) -> str:
    if not text:
        return ""

    normalized = text.replace("\n", " ").replace("\t", " ")
    normalized = re.sub(r"\s+", " ", normalized).strip()

    replacements = {
        " nxt ": " next ",
        " @ ": " at ",
        " @": " at",
        "@ ": "at ",
    }

    padded = f" {normalized} "
    for src, target in replacements.items():
        padded = padded.replace(src, target)

    padded = re.sub(
        r"\b(?P<hour>[0-9OolIsSBZz]{1,2})(?::(?P<minute>[0-9OolIsSBZz]{2}))?\s*(?P<meridiem>[ap]m)\b",
        _normalize_ocr_time_token,
        padded,
        flags=re.IGNORECASE,
    )

    cleaned = re.sub(r"\s+", " ", padded).strip()
    return cleaned
