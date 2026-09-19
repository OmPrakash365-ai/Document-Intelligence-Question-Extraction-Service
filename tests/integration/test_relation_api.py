"""Integration tests for Document Relations API endpoints."""

import uuid
from app.models.document import Document, DocumentStatus
from app.models.document_relation import RelationType


def test_document_relations(client, db_session, test_user, auth_headers):
    # Create two documents
    doc1 = Document(
        owner_id=test_user.id,
        filename="exam.pdf",
        original_filename="exam.pdf",
        content_type="application/pdf",
        file_size=1000,
        file_hash="hash_doc1",
        storage_path="/tmp/exam.pdf",
        status=DocumentStatus.COMPLETED.value,
    )
    doc2 = Document(
        owner_id=test_user.id,
        filename="answers.pdf",
        original_filename="answers.pdf",
        content_type="application/pdf",
        file_size=800,
        file_hash="hash_doc2",
        storage_path="/tmp/answers.pdf",
        status=DocumentStatus.COMPLETED.value,
    )
    db_session.add_all([doc1, doc2])
    db_session.commit()

    # 1. Create relation
    res = client.post(
        f"/api/v1/documents/{doc1.id}/relations",
        headers=auth_headers,
        json={"target_document_id": str(doc2.id), "relation_type": "ANSWER_KEY"},
    )
    assert res.status_code == 201
    relation_id = res.json()["id"]
    assert res.json()["relation_type"] == "ANSWER_KEY"

    # 2. List relations
    list_res = client.get(f"/api/v1/documents/{doc1.id}/relations", headers=auth_headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) == 1

    # 3. Delete relation
    del_res = client.delete(
        f"/api/v1/documents/{doc1.id}/relations/{relation_id}",
        headers=auth_headers,
    )
    assert del_res.status_code == 204
