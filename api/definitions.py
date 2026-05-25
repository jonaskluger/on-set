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
            "name": "Set",
            "description": "The physical build created by the Art Department or procured by Production for the purposes of filming.",
        },
        {
            "name": "Virtual stage",
            "description": "The environment which integrates physical and virtual production. Typically a set of LED panels, projection screens and/or process screens for keying.",
        },
    ],
    "meta": {"count": 2},
}

DEFINITION_DETAIL_EXAMPLE = {
    "data": {
        "name": "Virtual stage",
        "slug": "virtual-stage",
        "description": "The environment which integrates physical and virtual production. Typically a set of LED panels, projection screens and/or process screens for keying.",
    }
}

VFX_TYPE_LIST_EXAMPLE = {
    "data": [
        {
            "name": "Basic 2D VFX",
            "description": "2-D blue screen, wire or rig removal, etc.",
        },
        {
            "name": "Digital Matte Painting",
            "description": "Can include 3-D environments, but could be 2D, does not include characters.",
        },
    ],
    "meta": {"count": 2},
}

VFX_TYPE_DETAIL_EXAMPLE = {
    "data": {
        "name": "Basic 2D VFX",
        "slug": "basic-2d-vfx",
        "description": "2-D blue screen, wire or rig removal, etc.",
    }
}

DATA_SET_LIST_EXAMPLE = {
    "data": [
        {
            "id": "4.2",
            "name": "HDRIs",
            "slug": "hdris",
            "category": "4. Colour & Lighting Reference",
        },
        {
            "id": "3.1",
            "name": "Camera Reports",
            "slug": "camera-reports",
            "category": "3. Production Reports & Metadata",
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
        "category": "4. Colour & Lighting Reference",
        "description": "Captures a full light spectrum.",
        "usage": "Enables accurate recreation of on-set lighting in CG.",
        "scope": ["Lighting Setup"],
        "vfx_types": [
            "Basic 2D VFX",
            "Digital Matte Painting",
            "Complex VFX",
            "Virtual Production",
            "Real time",
        ],
        "data_collected": [
            "360° Hdr Images Of The Set Lighting Per Camera Setup",
        ],
        "creators": ["Data Wrangler", "VFX On-set Vendor"],
        "consumers": [
            "Studio Marketing For Commercial Or Game Creation",
            "VFX Post Production Vendor",
        ],
    }
}

DEPENDENCIES_EXAMPLE = {
    "data": {
        "dataset": {
            "id": "4.2",
            "title": "4.2 HDRIs",
            "name": "HDRIs",
            "slug": "hdris",
            "category": "4. Colour & Lighting Reference",
            "scope": ["Lighting Setup"],
            "vfx_types": [
                "Basic 2D VFX",
                "Digital Matte Painting",
                "Complex VFX",
                "Virtual Production",
                "Real time",
            ],
        },
        "dependencies": {
            "inbound": [
                {
                    "from": {"type": "creator", "name": "Data Wrangler"},
                    "to": {
                        "type": "dataset",
                        "id": "4.2",
                        "slug": "hdris",
                        "name": "HDRIs",
                    },
                    "relationship": "creates",
                },
                {
                    "from": {"type": "creator", "name": "VFX On-set Vendor"},
                    "to": {
                        "type": "dataset",
                        "id": "4.2",
                        "slug": "hdris",
                        "name": "HDRIs",
                    },
                    "relationship": "creates",
                },
            ],
            "outbound": [
                {
                    "from": {
                        "type": "dataset",
                        "id": "4.2",
                        "slug": "hdris",
                        "name": "HDRIs",
                    },
                    "to": {
                        "type": "consumer",
                        "name": "Studio Marketing For Commercial Or Game Creation",
                    },
                    "relationship": "consumed_by",
                },
                {
                    "from": {
                        "type": "dataset",
                        "id": "4.2",
                        "slug": "hdris",
                        "name": "HDRIs",
                    },
                    "to": {"type": "consumer", "name": "VFX Post Production Vendor"},
                    "relationship": "consumed_by",
                },
            ],
            "counts": {"inbound": 2, "outbound": 2},
        },
    }
}

RAW_DATA_EXAMPLE = {
    "Scope Definitions": [
        {
            "Set": "The physical build created by the Art Department or procured by Production for the purposes of filming."
        }
    ],
    "VFX Types": [{"Basic 2D VFX": "2-D blue screen, wire or rig removal, etc."}],
    "Data Sets": [
        {
            "title": "4. Colour & Lighting Reference",
            "subsections": [
                {
                    "title": "4.2 HDRIs",
                    "items": [
                        {
                            "Creator": ["Data Wrangler", "VFX On-set Vendor"],
                            "Consumer": [
                                "Studio Marketing For Commercial Or Game Creation",
                                "VFX Post Production Vendor",
                            ],
                            "VFXTypes": [
                                "Basic 2D VFX",
                                "Digital Matte Painting",
                                "Complex VFX",
                                "Virtual Production",
                                "Real time",
                            ],
                            "Scope": ["Lighting Setup"],
                            "Description": "Captures a full light spectrum.",
                            "Usage": "Enables accurate recreation of on-set lighting in CG.",
                            "Data Collected": [
                                "360° Hdr Images Of The Set Lighting Per Camera Setup"
                            ],
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
