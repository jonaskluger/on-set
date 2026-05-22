from __future__ import annotations

from typing import Any

from fastapi import FastAPI

from helper import _load_data

app = FastAPI(
    title="VES On-Set Data API",
    description="API wrapper for the VES On-Set Data dataset.",
    version="0.1.0",
    openapi_url="/api-docs/swagger.json",
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/v1/raw")
def get_raw_data() -> dict[str, Any]:
    return _load_data()
