# AI Appointment Scheduler Assistant

Backend service + lightweight web UI that converts natural-language appointment requests (text or image) into structured scheduling JSON.

## What It Does

This project implements a 4-stage pipeline:

1. OCR / Text Extraction
2. Entity Extraction
3. Normalization (Asia/Kolkata)
4. Guardrails + Final Structured Output

It supports:
- typed text input
- noisy image input (OCR)
- confidence scoring at each stage
- fallback extraction when LLM is unavailable

## Tech Stack

- Python 3.11+
- FastAPI
- pytesseract + Pillow
- dateparser
- pydantic
- OpenAI API (optional)
- pytest

## Project Structure

```text
.
├── app
│   ├── main.py
│   ├── models/
│   ├── routes/
│   ├── services/
│   └── utils/
├── tests/
├── samples/
├── requirements.txt
├── pytest.ini
└── README.md
```

## API Endpoints

- `GET /` → Web UI (Text/Image tabs)
- `GET /health`
- `POST /process` → full pipeline
- `POST /ocr` → OCR/Text extraction stage
- `POST /extract` → entity extraction stage
- `POST /normalize` → normalization stage
- `GET /docs` → Swagger docs

## Input Rule

For `POST /process` and `POST /ocr`, provide **exactly one** input:
- either `text`
- or `image` (base64)

Sending both is rejected by validation.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Install Tesseract (required for image OCR):

Ubuntu/Debian:
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng
```

macOS:
```bash
brew install tesseract
```

Run server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## UI Usage

Open `http://localhost:8000`:

- `Text` tab: enter text request
- `Image` tab: upload image
- `Run Pipeline (/process)`: stepwise assignment-style output
- `OCR Only (/ocr)`: raw_text + confidence output

## cURL Examples

### Full pipeline (text)

```bash
curl -X POST http://localhost:8000/process \
  -H "Content-Type: application/json" \
  -d '{"text":"Book dentist next Friday at 3pm"}'
```

### OCR only (text)

```bash
curl -X POST http://localhost:8000/ocr \
  -H "Content-Type: application/json" \
  -d '{"text":"book dentist nxt Friday @ 3 pm"}'
```

### OCR only (image)

```bash
BASE64_IMG=$(base64 -w 0 note.png)
curl -X POST http://localhost:8000/ocr \
  -H "Content-Type: application/json" \
  -d "{\"image\":\"${BASE64_IMG}\"}"
```

## Example Stage Outputs

### Step 1 - OCR/Text Extraction

```json
{
  "raw_text": "Book dentist next Friday at 3pm",
  "confidence": 0.90
}
```

### Step 2 - Entity Extraction

```json
{
  "entities": {
    "date_phrase": "next Friday",
    "time_phrase": "3pm",
    "department": "Dentistry"
  },
  "entities_confidence": 0.85
}
```

### Step 3 - Normalization

```json
{
  "normalized": {
    "date": "2026-05-08",
    "time": "15:00",
    "tz": "Asia/Kolkata"
  },
  "normalization_confidence": 1.0
}
```

### Guardrail Output

```json
{
  "status": "needs_clarification",
  "message": "Ambiguous date/time or department"
}
```

### Step 4 - Final Appointment JSON

```json
{
  "appointment": {
    "department": "Dentistry",
    "date": "2026-05-08",
    "time": "15:00",
    "tz": "Asia/Kolkata"
  },
  "status": "ok"
}
```

## Testing

```bash
pytest -q
```

## Public GitHub Checklist

Before pushing public:
- do **not** commit `.venv/`
- do **not** commit API keys/secrets
- keep `.gitignore` in repo root

If using OpenAI:

```bash
export OPENAI_API_KEY="your_key"
export OPENAI_MODEL="gpt-4o-mini"
```

If key is missing/unavailable, service falls back to rule-based extraction.
