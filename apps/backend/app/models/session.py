import uuid
from datetime import datetime
from sqlalchemy import String, Integer, BigInteger, DateTime, Text, ForeignKey, Index, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class ParsingSession(Base):
    __tablename__ = "parsing_sessions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    original_filename: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    s3_upload_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    s3_upload_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    document_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    ocr_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    ocr_job_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    parse_status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")
    parse_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    claude_model: Mapped[str | None] = mapped_column(String(50), nullable=True)
    tokens_used: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parse_cost_cents: Mapped[int | None] = mapped_column(Integer, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")

    user = relationship("User", back_populates="parsing_sessions")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    analysis_type: Mapped[str] = mapped_column(String(50), nullable=False)
    trigger: Mapped[str | None] = mapped_column(String(20), nullable=True)
    input_payload: Mapped[dict | None] = mapped_column(JSON, nullable=True, default=dict)
    output_data: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    plain_english_narrative: Mapped[str | None] = mapped_column(Text, nullable=True)
    mas_disclaimer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")

    user = relationship("User", back_populates="analysis_results")

    __table_args__ = (
        Index("idx_analysis_user", "user_id"),
        Index("idx_analysis_type", "analysis_type"),
    )


class ConsentRecord(Base):
    __tablename__ = "consent_records"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    consent_type: Mapped[str] = mapped_column(String(50), nullable=False)
    consent_version: Mapped[str] = mapped_column(String(50), nullable=False)
    consent_text_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)
    given_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")
    withdrawn_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    user = relationship("User", back_populates="consent_records")

    __table_args__ = (Index("idx_consent_user", "user_id"),)
