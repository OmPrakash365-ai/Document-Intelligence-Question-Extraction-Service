"""Initial schema migration

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-09-19 22:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users
    op.create_table(
        "users",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.create_index("ix_users_id", "users", ["id"])

    # 2. documents
    op.create_table(
        "documents",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("owner_id", sa.CHAR(36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("filename", sa.String(length=255), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("file_hash", sa.String(length=64), nullable=False),
        sa.Column("storage_path", sa.String(length=500), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False, server_default="UPLOADED"),
        sa.Column("document_type", sa.String(length=50), nullable=False, server_default="UNKNOWN"),
        sa.Column("page_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_stage", sa.String(length=50), nullable=False, server_default="UPLOADING"),
        sa.Column("pages_processed", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("processing_started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("processing_completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_documents_id", "documents", ["id"])
    op.create_index("ix_documents_owner_id", "documents", ["owner_id"])
    op.create_index("ix_documents_file_hash", "documents", ["file_hash"])
    op.create_index("ix_documents_status", "documents", ["status"])
    op.create_index("ix_documents_owner_status", "documents", ["owner_id", "status"])

    # 3. document_pages
    op.create_table(
        "document_pages",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("document_id", sa.CHAR(36), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("page_number", sa.Integer(), nullable=False),
        sa.Column("extracted_text", sa.Text(), nullable=True),
        sa.Column("ocr_used", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("image_path", sa.String(length=500), nullable=True),
        sa.Column("processing_status", sa.String(length=50), nullable=False, server_default="PENDING"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_document_pages_id", "document_pages", ["id"])
    op.create_index("ix_document_pages_document_id", "document_pages", ["document_id"])
    op.create_index("ix_document_pages_doc_page", "document_pages", ["document_id", "page_number"])

    # 4. questions
    op.create_table(
        "questions",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("document_id", sa.CHAR(36), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_number", sa.String(length=50), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("question_type", sa.String(length=50), nullable=False, server_default="UNKNOWN"),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("extraction_status", sa.String(length=50), nullable=False, server_default="SUCCESS"),
        sa.Column("source_start_page", sa.Integer(), nullable=False),
        sa.Column("source_end_page", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_questions_id", "questions", ["id"])
    op.create_index("ix_questions_document_id", "questions", ["document_id"])
    op.create_index("ix_questions_doc_number", "questions", ["document_id", "question_number"])

    # 5. options
    op.create_table(
        "options",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("question_id", sa.CHAR(36), sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("option_key", sa.String(length=20), nullable=False),
        sa.Column("option_text", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="1.0"),
    )
    op.create_index("ix_options_id", "options", ["id"])
    op.create_index("ix_options_question_id", "options", ["question_id"])
    op.create_index("ix_options_question_key", "options", ["question_id", "option_key"])

    # 6. answers
    op.create_table(
        "answers",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("question_id", sa.CHAR(36), sa.ForeignKey("questions.id", ondelete="CASCADE"), unique=True, nullable=False),
        sa.Column("answer_value", sa.Text(), nullable=False),
        sa.Column("answer_type", sa.String(length=50), nullable=False, server_default="OPTION_KEY"),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("source_document_id", sa.CHAR(36), sa.ForeignKey("documents.id", ondelete="SET NULL"), nullable=True),
        sa.Column("source_page", sa.Integer(), nullable=True),
        sa.Column("matching_status", sa.String(length=50), nullable=False, server_default="UNMATCHED"),
    )
    op.create_index("ix_answers_id", "answers", ["id"])
    op.create_index("ix_answers_question_id", "answers", ["question_id"])
    op.create_index("ix_answers_source_document_id", "answers", ["source_document_id"])
    op.create_index("ix_answers_matching_status", "answers", ["matching_status"])

    # 7. review_items
    op.create_table(
        "review_items",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("document_id", sa.CHAR(36), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question_id", sa.CHAR(36), sa.ForeignKey("questions.id", ondelete="CASCADE"), nullable=True),
        sa.Column("issue_type", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(length=20), nullable=False, server_default="MEDIUM"),
        sa.Column("resolved", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_review_items_id", "review_items", ["id"])
    op.create_index("ix_review_items_document_id", "review_items", ["document_id"])
    op.create_index("ix_review_items_question_id", "review_items", ["question_id"])
    op.create_index("ix_review_items_issue_type", "review_items", ["issue_type"])
    op.create_index("ix_review_items_severity", "review_items", ["severity"])
    op.create_index("ix_review_items_doc_severity", "review_items", ["document_id", "severity"])

    # 8. document_relations
    op.create_table(
        "document_relations",
        sa.Column("id", sa.CHAR(36), primary_key=True),
        sa.Column("source_document_id", sa.CHAR(36), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_document_id", sa.CHAR(36), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("relation_type", sa.String(length=50), nullable=False, server_default="RELATED_DOCUMENT"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_document_relations_id", "document_relations", ["id"])
    op.create_index("ix_document_relations_source_document_id", "document_relations", ["source_document_id"])
    op.create_index("ix_document_relations_target_document_id", "document_relations", ["target_document_id"])
    op.create_index("ix_document_relations_source_target", "document_relations", ["source_document_id", "target_document_id"], unique=True)


def downgrade() -> None:
    op.drop_table("document_relations")
    op.drop_table("review_items")
    op.drop_table("answers")
    op.drop_table("options")
    op.drop_table("questions")
    op.drop_table("document_pages")
    op.drop_table("documents")
    op.drop_table("users")
