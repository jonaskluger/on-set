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
