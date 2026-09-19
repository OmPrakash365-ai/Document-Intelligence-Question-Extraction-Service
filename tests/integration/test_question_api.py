"""Integration tests for Question and Answer API endpoints."""

import uuid
from app.models.document import Document, DocumentStatus
from app.models.question import Question, QuestionType, ExtractionStatus
from app.models.option import Option
from app.models.answer import Answer, MatchingStatus


def test_get_questions_and_answer(client, db_session, test_user, auth_headers):
    # Seed document
    doc = Document(
        owner_id=test_user.id,
        filename="test.pdf",
        original_filename="test.pdf",
        content_type="application/pdf",
        file_size=1000,
        file_hash="hash123",
        storage_path="/tmp/test.pdf",
        status=DocumentStatus.COMPLETED.value,
        page_count=2,
    )
    db_session.add(doc)
    db_session.commit()

    # Seed question with options and answer
    q = Question(
        document_id=doc.id,
        question_number="1",
        question_text="What is 2 + 2?",
        question_type=QuestionType.MCQ.value,
        confidence=0.95,
        extraction_status=ExtractionStatus.SUCCESS.value,
        source_start_page=1,
        source_end_page=1,
    )
    opt_a = Option(option_key="A", option_text="3", confidence=1.0)
    opt_b = Option(option_key="B", option_text="4", confidence=1.0)
    q.options.extend([opt_a, opt_b])

    ans = Answer(
        answer_value="B",
        answer_type="OPTION_KEY",
        confidence=0.98,
        matching_status=MatchingStatus.MATCHED.value,
        source_document_id=doc.id,
        source_page=1,
    )
    q.answer = ans

    db_session.add(q)
    db_session.commit()

    # 1. Retrieve questions for document
    res = client.get(f"/api/v1/documents/{doc.id}/questions", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert data["total"] == 1
    item = data["items"][0]
    assert item["question_number"] == "1"
    assert item["question"] == "What is 2 + 2?"
    assert item["question_type"] == "MCQ"
    assert len(item["options"]) == 2
    assert item["answer"]["value"] == "B"
    assert item["source"]["pages"] == [1]

    # 2. Retrieve single question
    q_res = client.get(f"/api/v1/questions/{q.id}", headers=auth_headers)
    assert q_res.status_code == 200
    assert q_res.json()["id"] == str(q.id)

    # 3. Retrieve answer
    ans_res = client.get(f"/api/v1/questions/{q.id}/answer", headers=auth_headers)
    assert ans_res.status_code == 200
    assert ans_res.json()["value"] == "B"
    assert ans_res.json()["matching_status"] == "MATCHED"
