import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email: Mapped[str | None] = mapped_column(String(320), unique=True, nullable=True)
    hashed_email: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()", onupdate="now()")
    magic_link_token: Mapped[str | None] = mapped_column(String(255), nullable=True)
    magic_link_expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    agreed_to_pdpa_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    pdpa_consent_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    last_data_export_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    last_data_delete_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    policies = relationship("Policy", back_populates="user", cascade="all, delete-orphan")
    analysis_results = relationship("AnalysisResult", back_populates="user", cascade="all, delete-orphan")
    consent_records = relationship("ConsentRecord", back_populates="user", cascade="all, delete-orphan")
    parsing_sessions = relationship("ParsingSession", back_populates="user", cascade="all, delete-orphan")
