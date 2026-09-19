"""Integration tests for UI serving and 1-click sample document endpoints."""


def test_serve_ui_root(client):
    res = client.get("/")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "DocIntelligence" in res.text


def test_serve_ui_subpath(client):
    res = client.get("/ui")
    assert res.status_code == 200
    assert "text/html" in res.headers["content-type"]
    assert "DocIntelligence" in res.text


def test_sample_document_endpoint(client, auth_headers):
    res = client.post(
        "/api/v1/documents/sample/clean_digital",
        headers=auth_headers,
    )
    assert res.status_code == 202
    data = res.json()
    assert "document_id" in data
    assert data["status"] == "QUEUED"


def test_invalid_sample_name(client, auth_headers):
    res = client.post(
        "/api/v1/documents/sample/non_existent_sample",
        headers=auth_headers,
    )
    assert res.status_code == 404
