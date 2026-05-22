from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from helper import (
    _dataset_dependencies,
    _dataset_lookup,
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
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


@app.get("/api/v1/vfx-types")
def get_vfx_types() -> dict[str, Any]:
    data = _load_data()
    pairs = _extract_pairs(data.get("VFX Types", []))
    items = _pairs_to_items(pairs)
    return {
        "data": items,
        "meta": {"count": len(items)},
    }


@app.get("/api/v1/vfx-types/{slug}")
def get_vfx_type(slug: str) -> dict[str, Any]:
    data = _load_data()
    pairs = _extract_pairs(data.get("VFX Types", []))
    slug_data = _pairs_to_slug_map(pairs)

    if slug in slug_data:
        return {"data": slug_data[slug]}

    raise HTTPException(status_code=404, detail=f"Unknown vfx type: {slug}")


@app.get("/api/v1/data-sets")
def get_data_sets() -> dict[str, Any]:
    data = _load_data()
    datasets, _ = _dataset_lookup(data)
    return {
        "data": [
            {
                "id": ds["id"],
                "name": ds["name"],
                "slug": ds["slug"],
                "category": ds["category"],
            }
            for ds in datasets
        ],
        "meta": {"count": len(datasets)},
    }


@app.get("/api/v1/data-sets/{slug}")
def get_data_set(slug: str) -> dict[str, Any]:
    data = _load_data()
    _, index = _dataset_lookup(data)

    dataset = index.get(slug.lower())
    if not dataset:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown dataset: {slug}. Try id like '4.2' or slug like 'hdris'.",
        )

    return {
        "data": {
            "id": dataset["id"],
            "title": dataset["title"],
            "name": dataset["name"],
            "slug": dataset["slug"],
            "category": dataset["category"],
            "description": dataset["description"],
            "usage": dataset["usage"],
            "scope": dataset["scope"],
            "vfx_types": dataset["vfx_types"],
            "data_collected": dataset["data_collected"],
            "creators": dataset["creators"],
            "consumers": dataset["consumers"],
        }
    }


@app.get("/api/v1/data-sets/{dataset_ref}/dependencies")
def get_data_set_dependencies(dataset_ref: str) -> dict[str, Any]:
    data = _load_data()
    _, index = _dataset_lookup(data)

    lookup_key = dataset_ref.lower()
    dataset = index.get(lookup_key)
    if not dataset:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown dataset: {dataset_ref}. Try id like '4.2' or slug like 'hdris'.",
        )

    return {
        "data": {
            "dataset": {
                "id": dataset["id"],
                "title": dataset["title"],
                "name": dataset["name"],
                "slug": dataset["slug"],
                "category": dataset["category"],
                "scope": dataset["scope"],
                "vfx_types": dataset["vfx_types"],
            },
            "dependencies": _dataset_dependencies(dataset),
        }
    }
