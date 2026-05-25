# API

Python API service backed by `https://ves-on-set-data.org/data/data.json`.

## Run locally
From repository root:

```bash
pip install -r requirements.txt
uvicorn --app-dir api main:app --reload
```

Open:
- `http://127.0.0.1:8000/docs` for Swagger UI
- `http://127.0.0.1:8000/redoc` for ReDoc
- `http://127.0.0.1:8000/api-docs/swagger.json` for OpenAPI JSON

## Endpoints
- `GET /health`
- `GET /api/v1/scope-definitions`
- `GET /api/v1/scope-definitions/{slug}`
- `GET /api/v1/vfx-types`
- `GET /api/v1/vfx-types/{slug}`
- `GET /api/v1/data-sets`
- `GET /api/v1/data-sets/{slug}`
- `GET /api/v1/data-sets/{slug}/dependencies`
- `GET /api/v1/raw`

`GET /api/v1/raw` proxies upstream data from `https://ves-on-set-data.org/data/data.json`.

Slug endpoints use lowercase kebab-case (spaces replaced by `-`).

Data set dependency lookup accepts:
- dataset id (example: `4.2`)
- dataset slug (example: `hdris`)

Examples:
- `GET /api/v1/data-sets/hdris`
- `GET /api/v1/data-sets/4.2/dependencies`
- `GET /api/v1/data-sets/hdris/dependencies`
