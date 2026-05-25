from __future__ import annotations

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str


class ErrorResponse(BaseModel):
    detail: str


class CountMeta(BaseModel):
    count: int


class DefinitionItem(BaseModel):
    name: str
    description: str


class DefinitionDetailItem(DefinitionItem):
    slug: str


class DefinitionListResponse(BaseModel):
    data: list[DefinitionItem]
    meta: CountMeta


class DefinitionDetailResponse(BaseModel):
    data: DefinitionDetailItem


class DataSetSummary(BaseModel):
    id: str
    name: str
    slug: str
    category: str


class DataSetDetail(DataSetSummary):
    title: str
    description: str
    usage: str
    scope: list[str]
    vfx_types: list[str]
    data_collected: list[str]
    creators: list[str]
    consumers: list[str]


class DataSetListResponse(BaseModel):
    data: list[DataSetSummary]
    meta: CountMeta


class DataSetDetailResponse(BaseModel):
    data: DataSetDetail


class DependencyEntity(BaseModel):
    type: str
    name: str
    id: str | None = None
    slug: str | None = None


class DependencyEdge(BaseModel):
    from_: DependencyEntity = Field(alias="from")
    to: DependencyEntity
    relationship: str


class DependencyCounts(BaseModel):
    inbound: int
    outbound: int


class DependencyGraph(BaseModel):
    inbound: list[DependencyEdge]
    outbound: list[DependencyEdge]
    counts: DependencyCounts


class DataSetDependencyInfo(BaseModel):
    id: str | None = None
    title: str
    name: str
    slug: str | None = None
    category: str
    scope: list[str]
    vfx_types: list[str]


class DataSetDependenciesPayload(BaseModel):
    dataset: DataSetDependencyInfo
    dependencies: DependencyGraph


class DataSetDependenciesResponse(BaseModel):
    data: DataSetDependenciesPayload


HEALTH_EXAMPLE = {"status": "ok"}

DEFINITION_LIST_EXAMPLE = {
    "data": [
        {
            "name": "Physical Objects",
            "description": "Collecting physical references such as props and environments.",
        },
        {
            "name": "Appearance",
            "description": "Surface look-dev data like material and color response.",
        },
    ],
    "meta": {"count": 2},
}

DEFINITION_DETAIL_EXAMPLE = {
    "data": {
        "name": "Physical Objects",
        "slug": "physical-objects",
        "description": "Collecting physical references such as props and environments.",
    }
}

VFX_TYPE_LIST_EXAMPLE = {
    "data": [
        {
            "name": "CG Environment",
            "description": "Digital world building and set extension workflows.",
        },
        {
            "name": "FX",
            "description": "Simulation-heavy work such as fire, smoke, water and destruction.",
        },
    ],
    "meta": {"count": 2},
}

VFX_TYPE_DETAIL_EXAMPLE = {
    "data": {
        "name": "CG Environment",
        "slug": "cg-environment",
        "description": "Digital world building and set extension workflows.",
    }
}

DATA_SET_LIST_EXAMPLE = {
    "data": [
        {
            "id": "4.2",
            "name": "HDRIs",
            "slug": "hdris",
            "category": "Environment",
        },
        {
            "id": "3.1",
            "name": "Textures",
            "slug": "textures",
            "category": "Materials",
        },
    ],
    "meta": {"count": 2},
}

DATA_SET_DETAIL_EXAMPLE = {
    "data": {
        "id": "4.2",
        "title": "4.2 HDRIs",
        "name": "HDRIs",
        "slug": "hdris",
        "category": "Environment",
        "description": "High dynamic range panoramas captured on set for image-based lighting.",
        "usage": "Lighting, reflection look-dev, and environment integration for CG assets.",
        "scope": ["Appearance", "Environment"],
        "vfx_types": ["CG Environment", "CG Character", "FX"],
        "data_collected": [
            "360 bracketed RAW captures",
            "Color checker chart frames",
            "Sun and key light direction notes",
        ],
        "creators": ["On-Set Data Wrangler", "Lighting Reference Team"],
        "consumers": ["Lighting", "Look Development", "Compositing"],
    }
}

DEPENDENCIES_EXAMPLE = {
    "data": {
        "dataset": {
            "id": "4.2",
            "title": "4.2 HDRIs",
            "name": "HDRIs",
            "slug": "hdris",
            "category": "Environment",
            "scope": ["Appearance", "Environment"],
            "vfx_types": ["CG Environment", "FX"],
        },
        "dependencies": {
            "inbound": [
                {
                    "from": {"type": "creator", "name": "On-Set Data Wrangler"},
                    "to": {
                        "type": "dataset",
                        "id": "4.2",
                        "slug": "hdris",
                        "name": "HDRIs",
                    },
                    "relationship": "creates",
                }
            ],
            "outbound": [
                {
                    "from": {
                        "type": "dataset",
                        "id": "4.2",
                        "slug": "hdris",
                        "name": "HDRIs",
                    },
                    "to": {"type": "consumer", "name": "Lighting"},
                    "relationship": "consumed_by",
                }
            ],
            "counts": {"inbound": 1, "outbound": 1},
        },
    }
}

RAW_DATA_EXAMPLE = {
    "Scope Definitions": [
        {
            "Appearance": "Surface-level references that define look and material response."
        }
    ],
    "VFX Types": [
        {"CG Environment": "Digital set extension and world building tasks."}
    ],
    "Data Sets": [
        {
            "title": "Environment",
            "subsections": [
                {
                    "title": "4.2 HDRIs",
                    "items": [
                        {
                            "Creator": ["On-Set Data Wrangler"],
                            "Consumer": ["Lighting"],
                            "VFXTypes": ["CG Environment"],
                            "Scope": ["Appearance"],
                            "Description": "High dynamic range panoramic lighting captures.",
                            "Usage": "Primary image-based lighting reference for shots.",
                            "Data Collected": ["Bracketed RAW panoramas"],
                        }
                    ],
                }
            ],
        }
    ],
}

NOT_FOUND_EXAMPLE = {
    "detail": "Unknown dataset: unknown-id. Try id like '4.2' or slug like 'hdris'."
}
