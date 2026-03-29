from __future__ import annotations

import uuid
from datetime import datetime, date
from sqlalchemy import String, Integer, BigInteger, Float, Date, DateTime, Text, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Policy(Base):
    __tablename__ = "policies"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    insurer_code: Mapped[str] = mapped_column(String(50), nullable=False)
    insurer_name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    product_type: Mapped[str] = mapped_column(String(50), nullable=False)
    policy_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    issue_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    sum_assured_cents: Mapped[int] = mapped_column(BigInteger, nullable=False, default=0)
    premium_amount_cents: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    premium_frequency: Mapped[str] = mapped_column(String(20), nullable=False, default="annual")
    currency: Mapped[str] = mapped_column(String(3), nullable=False, default="SGD")
    policy_status: Mapped[str] = mapped_column(String(20), nullable=False, default="active")
    policy_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    parse_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    parsing_session_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("parsing_sessions.id"), nullable=True)
    raw_pdf_key: Mapped[str | None] = mapped_column(String(500), nullable=True)
    structured_data: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    plain_english_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()", onupdate="now()")

    user = relationship("User", back_populates="policies")
    benefits = relationship("Benefit", back_populates="policy", cascade="all, delete-orphan")
    riders = relationship("Rider", back_populates="policy", cascade="all, delete-orphan")
    exclusions = relationship("Exclusion", back_populates="policy", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_policies_user_id", "user_id"),
        Index("idx_policies_type", "product_type"),
    )


class Benefit(Base):
    __tablename__ = "benefits"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False)
    benefit_type: Mapped[str] = mapped_column(String(50), nullable=False)
    benefit_subtype: Mapped[str | None] = mapped_column(String(100), nullable=True)
    trigger_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    payout_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    amount_cents: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    percentage_of_sum_assured: Mapped[float | None] = mapped_column(Float, nullable=True)
    survival_period_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    conditions: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    exclusions: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    parse_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    raw_text_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")

    policy = relationship("Policy", back_populates="benefits")

    __table_args__ = (
        Index("idx_benefits_policy_id", "policy_id"),
        Index("idx_benefits_type", "benefit_type"),
    )


class Rider(Base):
    __tablename__ = "riders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False)
    rider_name: Mapped[str] = mapped_column(String(255), nullable=False)
    rider_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    linked_benefit_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("benefits.id"), nullable=True)
    additional_premium_cents: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    additional_sum_assured_cents: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    conditions: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    parse_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")

    policy = relationship("Policy", back_populates="riders")


class Exclusion(Base):
    __tablename__ = "exclusions"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    policy_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("policies.id", ondelete="CASCADE"), nullable=False)
    benefit_ids: Mapped[list[uuid.UUID] | None] = mapped_column(JSONB, nullable=True)
    exclusion_text: Mapped[str] = mapped_column(Text, nullable=False)
    exclusion_category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    parse_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")

    policy = relationship("Policy", back_populates="exclusions")

    __table_args__ = (Index("idx_exclusions_policy_id", "policy_id"),)
