import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.anyio
async def test_health():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@pytest.mark.anyio
async def test_extract_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/extract", json={"raw_text": "Book dentist next Friday at 3pm"})
    assert response.status_code == 200
    payload = response.json()
    assert "entities" in payload
    assert payload["entities"]["department"] in {"Dentistry", "dentist", "Dental"}


@pytest.mark.anyio
async def test_process_endpoint_text():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post("/process", json={"text": "Book dentist next Friday at 3pm"})
    assert response.status_code == 200
    payload = response.json()
    assert payload["ocr"]["raw_text"]
    assert payload["extraction"]["entities"]["department"] is not None
    assert payload["final"]["status"] in {"ok", "needs_clarification"}


@pytest.mark.anyio
async def test_process_rejects_text_and_image_together():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/process",
            json={"text": "Book dentist next Friday at 3pm", "image": "ZmFrZQ=="},
        )
    assert response.status_code == 422
