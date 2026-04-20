import base64

import requests

from config import (
    OPENMETADATA_EMAIL,
    OPENMETADATA_JWT_TOKEN,
    OPENMETADATA_PASSWORD,
    OPENMETADATA_URL,
)


def _build_headers(token: str | None = None) -> dict:
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _get_access_token() -> str | None:
    if OPENMETADATA_JWT_TOKEN:
        return OPENMETADATA_JWT_TOKEN

    if not OPENMETADATA_EMAIL or not OPENMETADATA_PASSWORD:
        return None

    encoded_password = base64.b64encode(
        OPENMETADATA_PASSWORD.encode("utf-8")
    ).decode("utf-8")

    res = requests.post(
        f"{OPENMETADATA_URL}/users/login",
        json={
            "email": OPENMETADATA_EMAIL,
            "password": encoded_password,
        },
        headers=_build_headers(),
        timeout=20,
    )

    if res.status_code != 200:
        raise RuntimeError(f"OpenMetadata login failed: {res.status_code} {res.text}")

    return res.json().get("accessToken")


def _request(method: str, path: str, **kwargs):
    token = _get_access_token()
    headers = _build_headers(token)
    request_headers = kwargs.pop("headers", {})
    headers.update(request_headers)

    res = requests.request(
        method,
        f"{OPENMETADATA_URL}{path}",
        headers=headers,
        timeout=20,
        **kwargs,
    )

    if res.status_code >= 400:
        raise RuntimeError(f"OpenMetadata API error: {res.status_code} {res.text}")

    return res


def get_tables(limit=20):
    res = _request(
        "GET",
        "/tables",
        params={"limit": limit, "include": "all"},
    )
    data = res.json().get("data", [])
    return [
        {
            "name": table.get("fullyQualifiedName"),
            "owner": table.get("owner", {}).get("name") if table.get("owner") else None,
            "description": table.get("description"),
            "tags": [tag["tagFQN"] for tag in table.get("tags", [])],
        }
        for table in data
    ]


def get_unowned_tables():
    tables = get_tables(50)
    return [table for table in tables if not table["owner"]]


def get_undocumented_tables():
    tables = get_tables(50)
    return [table for table in tables if not table["description"]]


def get_pipelines():
    res = _request(
        "GET",
        "/services/ingestionPipelines",
        params={"limit": 20},
    )
    data = res.json().get("data", [])
    return [
        {
            "name": pipeline.get("name"),
            "id": pipeline.get("id"),
            "status": pipeline.get("pipelineStatuses", {}),
        }
        for pipeline in data
    ]


def trigger_pipeline(pipeline_id: str):
    res = _request(
        "POST",
        f"/services/ingestionPipelines/trigger/{pipeline_id}",
    )
    if res.status_code == 200:
        return "Pipeline triggered successfully"
    return f"Failed to trigger pipeline: {res.status_code}"


def get_quality_failures():
    res = _request(
        "GET",
        "/dataQuality/testCases",
        params={"limit": 50, "testCaseStatus": "Failed"},
    )
    data = res.json().get("data", [])
    return [
        {
            "name": test_case.get("name"),
            "table": test_case.get("entityLink"),
            "status": test_case.get("testCaseResult", {}).get("testCaseStatus"),
        }
        for test_case in data
    ]


def get_lineage(table_fqn: str):
    res = _request(
        "GET",
        f"/lineage/table/name/{table_fqn}",
        params={"upstreamDepth": 2, "downstreamDepth": 2},
    )
    return res.json()
