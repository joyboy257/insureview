"""Initial migration: create all tables

Revision ID: 001
Revises:
Create Date: 2026-03-28
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgcrypto for UUID generation
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    # Users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("email", sa.String(320), unique=True, nullable=True),
        sa.Column("hashed_email", sa.String(64), unique=True, nullable=False),
        sa.Column("full_name", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("magic_link_token", sa.String(255), nullable=True),
        sa.Column("magic_link_expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("agreed_to_pdpa_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("pdpa_consent_version", sa.String(50), nullable=True),
        sa.Column("last_data_export_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_data_delete_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_users_email", "users", [sa.text("hashed_email")], unique=False, postgresql_using="hash")

    # Parsing sessions
    op.create_table(
        "parsing_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("original_filename", sa.String(500), nullable=True),
        sa.Column("file_size_bytes", sa.BigInteger, nullable=True),
        sa.Column("s3_upload_key", sa.String(500), nullable=True),
        sa.Column("s3_upload_url", sa.Text, nullable=True),
        sa.Column("document_type", sa.String(30), nullable=True),
        sa.Column("ocr_provider", sa.String(50), nullable=True),
        sa.Column("ocr_job_id", sa.String(255), nullable=True),
        sa.Column("parse_status", sa.String(20), server_default="pending", nullable=False),
        sa.Column("parse_error", sa.Text, nullable=True),
        sa.Column("claude_model", sa.String(50), nullable=True),
        sa.Column("tokens_used", sa.Integer, nullable=True),
        sa.Column("parse_cost_cents", sa.Integer, nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # Policies
    op.create_table(
        "policies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("insurer_code", sa.String(50), nullable=False),
        sa.Column("insurer_name", sa.String(255), nullable=False),
        sa.Column("product_name", sa.String(255), nullable=False),
        sa.Column("product_type", sa.String(50), nullable=False),
        sa.Column("policy_number", sa.String(100), nullable=True),
        sa.Column("issue_date", sa.Date, nullable=True),
        sa.Column("expiry_date", sa.Date, nullable=True),
        sa.Column("sum_assured_cents", sa.BigInteger, server_default="0", nullable=False),
        sa.Column("premium_amount_cents", sa.BigInteger, nullable=True),
        sa.Column("premium_frequency", sa.String(20), server_default="annual", nullable=False),
        sa.Column("currency", sa.String(3), server_default="SGD", nullable=False),
        sa.Column("policy_status", sa.String(20), server_default="active", nullable=False),
        sa.Column("policy_year", sa.Integer, nullable=True),
        sa.Column("parse_confidence", sa.Float, server_default="0.0", nullable=False),
        sa.Column("parsing_session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("parsing_sessions.id"), nullable=True),
        sa.Column("raw_pdf_key", sa.String(500), nullable=True),
        sa.Column("structured_data", postgresql.JSONB, server_default="{}", nullable=False),
        sa.Column("plain_english_summary", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_policies_user_id", "policies", ["user_id"])
    op.create_index("idx_policies_type", "policies", ["product_type"])

    # Benefits
    op.create_table(
        "benefits",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("policy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("policies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("benefit_type", sa.String(50), nullable=False),
        sa.Column("benefit_subtype", sa.String(100), nullable=True),
        sa.Column("trigger_description", sa.Text, nullable=True),
        sa.Column("payout_type", sa.String(30), nullable=True),
        sa.Column("amount_cents", sa.BigInteger, nullable=True),
        sa.Column("percentage_of_sum_assured", sa.Float, nullable=True),
        sa.Column("survival_period_days", sa.Integer, nullable=True),
        sa.Column("conditions", postgresql.JSONB, nullable=True),
        sa.Column("exclusions", postgresql.JSONB, nullable=True),
        sa.Column("is_active", sa.Boolean, server_default="true", nullable=False),
        sa.Column("parse_confidence", sa.Float, server_default="0.0", nullable=False),
        sa.Column("raw_text_excerpt", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_benefits_policy_id", "benefits", ["policy_id"])
    op.create_index("idx_benefits_type", "benefits", ["benefit_type"])

    # Riders
    op.create_table(
        "riders",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("policy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("policies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("rider_name", sa.String(255), nullable=False),
        sa.Column("rider_type", sa.String(50), nullable=True),
        sa.Column("linked_benefit_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("benefits.id"), nullable=True),
        sa.Column("additional_premium_cents", sa.BigInteger, nullable=True),
        sa.Column("additional_sum_assured_cents", sa.BigInteger, nullable=True),
        sa.Column("conditions", postgresql.JSONB, nullable=True),
        sa.Column("parse_confidence", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )

    # Exclusions
    op.create_table(
        "exclusions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("policy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("policies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("benefit_ids", postgresql.JSONB, nullable=True),
        sa.Column("exclusion_text", sa.Text, nullable=False),
        sa.Column("exclusion_category", sa.String(50), nullable=True),
        sa.Column("parse_confidence", sa.Float, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_exclusions_policy_id", "exclusions", ["policy_id"])

    # Analysis results
    op.create_table(
        "analysis_results",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("analysis_type", sa.String(50), nullable=False),
        sa.Column("trigger", sa.String(20), nullable=True),
        sa.Column("input_payload", postgresql.JSONB, server_default="{}", nullable=True),
        sa.Column("output_data", postgresql.JSONB, server_default="{}", nullable=False),
        sa.Column("plain_english_narrative", sa.Text, nullable=True),
        sa.Column("mas_disclaimer_text", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
    )
    op.create_index("idx_analysis_user", "analysis_results", ["user_id"])
    op.create_index("idx_analysis_type", "analysis_results", ["analysis_type"])

    # Consent records
    op.create_table(
        "consent_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("consent_type", sa.String(50), nullable=False),
        sa.Column("consent_version", sa.String(50), nullable=False),
        sa.Column("consent_text_hash", sa.String(64), nullable=False),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("given_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("withdrawn_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("idx_consent_user", "consent_records", ["user_id"])


def downgrade() -> None:
    op.drop_table("consent_records")
    op.drop_table("analysis_results")
    op.drop_table("exclusions")
    op.drop_table("riders")
    op.drop_table("benefits")
    op.drop_table("policies")
    op.drop_table("parsing_sessions")
    op.drop_table("users")
