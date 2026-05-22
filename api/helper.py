from __future__ import annotations

import json
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
