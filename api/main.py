from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from helper import (
    _extract_pairs,
    _load_data,
    _pairs_to_items,
    _pairs_to_slug_map,
)

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


@app.get("/api/v1/scope-definitions")
def get_scope_definitions() -> dict[str, Any]:
    data = _load_data()
    pairs = _extract_pairs(data.get("Scope Definitions", []))
    items = _pairs_to_items(pairs)
    return {
        "data": items,
        "meta": {"count": len(items)},
    }


@app.get("/api/v1/scope-definitions/{slug}")
def get_scope_definition(slug: str) -> dict[str, Any]:
    data = _load_data()
    pairs = _extract_pairs(data.get("Scope Definitions", []))
    slug_data = _pairs_to_slug_map(pairs)

    if slug in slug_data:
        return {"data": slug_data[slug]}

    raise HTTPException(status_code=404, detail=f"Unknown scope definition: {slug}")
