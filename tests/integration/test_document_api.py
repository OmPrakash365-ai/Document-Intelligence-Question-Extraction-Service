"""Integration tests for Document API endpoints."""

import io
from pathlib import Path


def test_upload_pdf_document(client, auth_headers):
    # PDF with minimal valid header
    content = b"%PDF-1.4\n1 0 obj\n<<>>\nendobj\ntrailer\n<<>>\n%%EOF"
    file = io.BytesIO(content)

    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        files={"file": ("test_exam.pdf", file, "application/pdf")},
    )
    assert response.status_code == 202
    data = response.json()
    assert "document_id" in data
    assert data["status"] == "QUEUED"


def test_upload_unauthorized(client):
    content = b"%PDF-1.4 header"
    response = client.post(
        "/api/v1/documents",
        files={"file": ("test.pdf", io.BytesIO(content), "application/pdf")},
    )
    assert response.status_code == 401


def test_upload_invalid_file_type(client, auth_headers):
    response = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        files={"file": ("script.sh", io.BytesIO(b"echo 'hi'"), "text/plain")},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "UNSUPPORTED_FILE_TYPE"


def test_list_and_get_document(client, auth_headers):
    # 1. Upload document
    content = b"%PDF-1.4 sample file content"
    upload_res = client.post(
        "/api/v1/documents",
        headers=auth_headers,
        files={"file": ("exam1.pdf", io.BytesIO(content), "application/pdf")},
    )
    doc_id = upload_res.json()["document_id"]

    # 2. List documents
    list_res = client.get("/api/v1/documents", headers=auth_headers)
    assert list_res.status_code == 200
    list_data = list_res.json()
    assert list_data["total"] >= 1
    assert any(d["id"] == doc_id for d in list_data["items"])

    # 3. Get document details
    get_res = client.get(f"/api/v1/documents/{doc_id}", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["id"] == doc_id

    # 4. Check status
    status_res = client.get(f"/api/v1/documents/{doc_id}/status", headers=auth_headers)
    assert status_res.status_code == 200
    assert "current_stage" in status_res.json()

    # 5. Delete document
    del_res = client.delete(f"/api/v1/documents/{doc_id}", headers=auth_headers)
    assert del_res.status_code == 204

    # 6. Verify 404 after deletion
    get_after_del = client.get(f"/api/v1/documents/{doc_id}", headers=auth_headers)
    assert get_after_del.status_code == 404
