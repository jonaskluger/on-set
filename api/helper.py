from __future__ import annotations

import json
import re
from typing import Any
from urllib.error import URLError
from urllib.request import urlopen

from fastapi import HTTPException

DATA_URL = "https://ves-on-set-data.org/data/data.json"


def _load_data() -> dict[str, Any]:
    try:
        with urlopen(DATA_URL, timeout=15) as response:
            if response.status != 200:
                raise HTTPException(
                    status_code=502,
                    detail=f"Upstream data request failed with status {response.status}",
                )
            body = response.read().decode("utf-8")
            return json.loads(body)
    except URLError as exc:
        raise HTTPException(
            status_code=502, detail=f"Failed to fetch upstream data: {exc.reason}"
        ) from exc
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=502, detail=f"Invalid JSON from upstream data source: {exc}"
        ) from exc


def _to_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower())
    return slug.strip("-")


def _pairs_to_items(pairs: dict[str, str]) -> list[dict[str, str]]:
    return [{"name": key, "description": value} for key, value in pairs.items()]


def _pairs_to_slug_map(pairs: dict[str, str]) -> dict[str, dict[str, str]]:
    by_slug: dict[str, dict[str, str]] = {}
    for name, description in pairs.items():
        slug = _to_slug(name)
        by_slug[slug] = {
            "name": name,
            "slug": slug,
            "description": description,
        }
    return by_slug


def _extract_pairs(section_items: list[dict[str, Any]]) -> dict[str, str]:
    pairs: dict[str, str] = {}
    for entry in section_items:
        for key, value in entry.items():
            if key == "html":
                continue
            pairs[str(key)] = str(value)
    return pairs


def _extract_dataset_entries(raw_data: dict[str, Any]) -> list[dict[str, Any]]:
    """Flatten the nested "Data Sets" structure into dataset-centric entries.

    The source JSON stores datasets under categories -> subsections -> items.
    This helper converts each non-empty subsection into one normalized record.

    Parsing rules:
    - Subsection titles like "4.2 HDRIs" are split into:
      - id: "4.2"
      - name: "HDRIs"
    - If no numeric prefix is present, id is set to "" and name uses the title.
    - Slug is generated from the dataset name (for example, "HDRIs" -> "hdris").

    Returns dataset entries with ids/slugs and relationship metadata.
    """
    entries: list[dict[str, Any]] = []
    sections = raw_data.get("Data Sets", [])

    for category in sections:
        category_title = str(category.get("title", "")).strip()
        for subsection in category.get("subsections", []):
            subsection_title = str(subsection.get("title", "")).strip()
            items = subsection.get("items", [])

            if not subsection_title or not items:
                continue

            item = items[0]
            m = re.match(r"^(\d+\.\d+)\s*(.*)$", subsection_title)
            if m:
                dataset_id = m.group(1)
                dataset_name = m.group(2).strip(" .-:")
            else:
                dataset_id = ""
                dataset_name = subsection_title

            if not dataset_name:
                dataset_name = subsection_title

            entries.append(
                {
                    "id": dataset_id,
                    "name": dataset_name,
                    "title": subsection_title,
                    "slug": _to_slug(dataset_name),
                    "category": category_title,
                    "creators": item.get("Creator", []),
                    "consumers": item.get("Consumer", []),
                    "vfx_types": item.get("VFXTypes", []),
                    "scope": item.get("Scope", []),
                    "description": item.get("Description", ""),
                    "usage": item.get("Usage", ""),
                    "data_collected": item.get("Data Collected", []),
                }
            )

    return entries


def _dataset_lookup(
    raw_data: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    datasets = _extract_dataset_entries(raw_data)
    index: dict[str, dict[str, Any]] = {}

    for ds in datasets:
        if ds["id"]:
            index[ds["id"].lower()] = ds
        index[ds["slug"]] = ds
        index[_to_slug(ds["title"])] = ds

    return datasets, index


def _dataset_dependencies(dataset: dict[str, Any]) -> dict[str, Any]:
    """Build creator->dataset and dataset->consumer dependency edges.

    Returns a graph-friendly structure with:
    - inbound: edges from each creator to this dataset
    - outbound: edges from this dataset to each consumer
    - counts: number of inbound and outbound edges
    """
    dataset_entity = {
        "type": "dataset",
        "id": dataset.get("id"),
        "slug": dataset.get("slug"),
        "name": dataset["name"],
    }
    # Avoid serializing empty identifiers so API clients don't receive null/blank id/slug.
    dataset_entity = {
        key: value
        for key, value in dataset_entity.items()
        if key not in {"id", "slug"} or (value is not None and str(value).strip() != "")
    }

    inbound = [
        {
            "from": {
                "type": "creator",
                "name": creator,
            },
            "to": dataset_entity,
            "relationship": "creates",
        }
        for creator in dataset.get("creators", [])
    ]
    outbound = [
        {
            "from": dataset_entity,
            "to": {
                "type": "consumer",
                "name": consumer,
            },
            "relationship": "consumed_by",
        }
        for consumer in dataset.get("consumers", [])
    ]

    return {
        "inbound": inbound,
        "outbound": outbound,
        "counts": {
            "inbound": len(inbound),
            "outbound": len(outbound),
        },
    }
