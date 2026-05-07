from fastapi import FastAPI

from app.routes.extract import router as extract_router
from app.routes.normalize import router as normalize_router
from app.routes.ocr import router as ocr_router
from app.routes.process import router as process_router
from app.routes.ui import router as ui_router
from app.utils.logging_config import configure_logging

configure_logging()

app = FastAPI(
    title="AI Appointment Scheduler Assistant",
    version="1.0.0",
    description="OCR -> Entity Extraction -> Normalization pipeline with guardrails",
)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "healthy"}


app.include_router(ocr_router)
app.include_router(extract_router)
app.include_router(normalize_router)
app.include_router(process_router)
app.include_router(ui_router)
