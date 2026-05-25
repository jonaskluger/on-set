from __future__ import annotations

from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from definitions import (
    DATA_SET_DETAIL_EXAMPLE,
    DATA_SET_LIST_EXAMPLE,
    DEFINITION_DETAIL_EXAMPLE,
    DEFINITION_LIST_EXAMPLE,
    DEPENDENCIES_EXAMPLE,
    HEALTH_EXAMPLE,
    NOT_FOUND_EXAMPLE,
    RAW_DATA_EXAMPLE,
    VFX_TYPE_DETAIL_EXAMPLE,
    VFX_TYPE_LIST_EXAMPLE,
    DataSetDependenciesResponse,
    DataSetDetailResponse,
    DataSetListResponse,
    DefinitionDetailResponse,
    DefinitionListResponse,
    ErrorResponse,
    HealthResponse,
)

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


@app.get(
    "/health",
    response_model=HealthResponse,
    responses={
        200: {
            "description": "Service health status.",
            "content": {"application/json": {"example": HEALTH_EXAMPLE}},
        }
    },
)
def health() -> HealthResponse:
    return {"status": "ok"}


@app.get(
    "/api/v1/raw",
    response_model=dict[str, Any],
    responses={
        200: {
            "description": "Raw upstream dataset payload.",
            "content": {"application/json": {"example": RAW_DATA_EXAMPLE}},
        }
    },
)
def get_raw_data() -> dict[str, Any]:
    return _load_data()


@app.get(
    "/api/v1/scope-definitions",
    response_model=DefinitionListResponse,
    responses={
        200: {
            "description": "All scope definitions.",
            "content": {"application/json": {"example": DEFINITION_LIST_EXAMPLE}},
        }
    },
)
def get_scope_definitions() -> dict[str, Any]:
    data = _load_data()
    pairs = _extract_pairs(data.get("Scope Definitions", []))
    items = _pairs_to_items(pairs)
    return {
        "data": items,
        "meta": {"count": len(items)},
    }


@app.get(
    "/api/v1/scope-definitions/{slug}",
    response_model=DefinitionDetailResponse,
    responses={
        200: {
            "description": "Single scope definition by slug.",
            "content": {"application/json": {"example": DEFINITION_DETAIL_EXAMPLE}},
        },
        404: {
            "model": ErrorResponse,
            "description": "Unknown scope definition slug.",
            "content": {
                "application/json": {
                    "example": {"detail": "Unknown scope definition: missing-slug"}
                }
            },
        },
    },
)
def get_scope_definition(slug: str) -> dict[str, Any]:
    data = _load_data()
    pairs = _extract_pairs(data.get("Scope Definitions", []))
    slug_data = _pairs_to_slug_map(pairs)

    if slug in slug_data:
        return {"data": slug_data[slug]}

    raise HTTPException(status_code=404, detail=f"Unknown scope definition: {slug}")


@app.get(
    "/api/v1/vfx-types",
    response_model=DefinitionListResponse,
    responses={
        200: {
            "description": "All VFX types.",
            "content": {"application/json": {"example": VFX_TYPE_LIST_EXAMPLE}},
        }
    },
)
def get_vfx_types() -> dict[str, Any]:
    data = _load_data()
    pairs = _extract_pairs(data.get("VFX Types", []))
    items = _pairs_to_items(pairs)
    return {
        "data": items,
        "meta": {"count": len(items)},
    }


@app.get(
    "/api/v1/vfx-types/{slug}",
    response_model=DefinitionDetailResponse,
    responses={
        200: {
            "description": "Single VFX type by slug.",
            "content": {"application/json": {"example": VFX_TYPE_DETAIL_EXAMPLE}},
        },
        404: {
            "model": ErrorResponse,
            "description": "Unknown VFX type slug.",
            "content": {
                "application/json": {
                    "example": {"detail": "Unknown vfx type: missing-slug"}
                }
            },
        },
    },
)
def get_vfx_type(slug: str) -> dict[str, Any]:
    data = _load_data()
    pairs = _extract_pairs(data.get("VFX Types", []))
    slug_data = _pairs_to_slug_map(pairs)

    if slug in slug_data:
        return {"data": slug_data[slug]}

    raise HTTPException(status_code=404, detail=f"Unknown vfx type: {slug}")


@app.get(
    "/api/v1/data-sets",
    response_model=DataSetListResponse,
    responses={
        200: {
            "description": "List all data sets.",
            "content": {"application/json": {"example": DATA_SET_LIST_EXAMPLE}},
        }
    },
)
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


@app.get(
    "/api/v1/data-sets/{slug}",
    response_model=DataSetDetailResponse,
    responses={
        200: {
            "description": "Get one data set by id, slug, or title slug.",
            "content": {"application/json": {"example": DATA_SET_DETAIL_EXAMPLE}},
        },
        404: {
            "model": ErrorResponse,
            "description": "Unknown dataset identifier.",
            "content": {"application/json": {"example": NOT_FOUND_EXAMPLE}},
        },
    },
)
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


@app.get(
    "/api/v1/data-sets/{slug}/dependencies",
    response_model=DataSetDependenciesResponse,
    response_model_exclude_none=True,
    responses={
        200: {
            "description": "Creator and consumer dependency edges for one data set.",
            "content": {"application/json": {"example": DEPENDENCIES_EXAMPLE}},
        },
        404: {
            "model": ErrorResponse,
            "description": "Unknown dataset identifier.",
            "content": {"application/json": {"example": NOT_FOUND_EXAMPLE}},
        },
    },
)
def get_data_set_dependencies(slug: str) -> dict[str, Any]:
    data = _load_data()
    _, index = _dataset_lookup(data)

    lookup_key = slug.lower()
    dataset = index.get(lookup_key)
    if not dataset:
        raise HTTPException(
            status_code=404,
            detail=f"Unknown dataset: {slug}. Try id like '4.2' or slug like 'hdris'.",
        )

    dataset_info = {
        "id": dataset.get("id"),
        "title": dataset["title"],
        "name": dataset["name"],
        "slug": dataset.get("slug"),
        "category": dataset["category"],
        "scope": dataset["scope"],
        "vfx_types": dataset["vfx_types"],
    }
    dataset_info = {
        key: value
        for key, value in dataset_info.items()
        if key not in {"id", "slug"} or (value is not None and str(value).strip() != "")
    }

    return {
        "data": {
            "dataset": dataset_info,
            "dependencies": _dataset_dependencies(dataset),
        }
    }
