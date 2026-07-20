"""
db/models.py
SQLAlchemy 2.0 ORM models — full schema for the Marathi Kundali platform.

Tables:
  geocode_cache  — cached place → lat/lng/tz results (avoid repeated Nominatim calls)
  birth_profiles — canonical birth data (reused across kundali + biodata)
  kundalis       — computed kundali records, free + paid
  orders         — Razorpay orders + payment lifecycle
  matchings      — Ashtakoot matching records
  biodatas       — Biodata builder records (JSONB form data)
  webhook_events — raw Razorpay webhook payloads (idempotency + audit)
"""
from __future__ import annotations
import uuid
from datetime import datetime, date, time
from typing import Optional

from sqlalchemy import (
    String, Boolean, Integer, Float, Date, Time, DateTime, Text, JSON,
    ForeignKey, Index, Enum as SAEnum, func,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


# ──────────────────────────────────────────────────────────────────────────────
# Geocode Cache
# ──────────────────────────────────────────────────────────────────────────────
class GeocodeCache(Base):
    __tablename__ = "geocode_cache"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    query_normalized: Mapped[str] = mapped_column(String(300), nullable=False, unique=True, index=True)
    display_name: Mapped[str] = mapped_column(String(500), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    tz_iana: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


# ──────────────────────────────────────────────────────────────────────────────
# Birth Profile  (reused by both kundali + biodata)
# ──────────────────────────────────────────────────────────────────────────────
class BirthProfile(Base):
    __tablename__ = "birth_profiles"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    gender: Mapped[str] = mapped_column(SAEnum("male", "female", name="gender_enum"), nullable=False)
    dob: Mapped[date] = mapped_column(Date, nullable=False)
    time_of_birth: Mapped[Optional[time]] = mapped_column(Time, nullable=True)
    time_accuracy: Mapped[str] = mapped_column(
        SAEnum("exact", "approximate", "unknown", name="time_accuracy_enum"),
        nullable=False, default="exact",
    )
    place_text: Mapped[str] = mapped_column(String(500), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    tz_iana: Mapped[str] = mapped_column(String(100), nullable=False)
    rahu_mode: Mapped[str] = mapped_column(
        SAEnum("true_node", "mean_node", name="rahu_mode_enum"),
        nullable=False, default="true_node",
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Relationships
    kundalis: Mapped[list["Kundali"]] = relationship(back_populates="birth_profile")


# ──────────────────────────────────────────────────────────────────────────────
# Kundali  (computed chart — free + paid fields)
# ──────────────────────────────────────────────────────────────────────────────
class Kundali(Base):
    __tablename__ = "kundalis"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    birth_profile_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("birth_profiles.id", ondelete="CASCADE"), nullable=False
    )

    # Free-tier fields (always returned)
    rashi_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    nakshatra_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    pada: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    lagna_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    lagna_reliable: Mapped[bool] = mapped_column(Boolean, default=True)
    gana: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    nadi: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    varna: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Chart SVG (free — shown as D1 visual)
    chart_d1_svg: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Paid-tier fields (JSONB — only populated after payment)
    paid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    planet_positions: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    navamsa_svg: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    mangal_dosha: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    dasha: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    written_analysis: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Export
    pdf_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Resumable draft token (for payment failure recovery)
    resume_token: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)

    # Retention
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)  # 30d for unpaid

    # Relationships
    birth_profile: Mapped["BirthProfile"] = relationship(back_populates="kundalis")
    orders: Mapped[list["Order"]] = relationship(back_populates="kundali")

    __table_args__ = (
        Index("ix_kundalis_paid_created", "paid", "created_at"),
        Index("ix_kundalis_birth_profile", "birth_profile_id"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Matching
# ──────────────────────────────────────────────────────────────────────────────
class Matching(Base):
    __tablename__ = "matchings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Either references existing kundali OR stores birth profile inline
    bride_kundali_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("kundalis.id", ondelete="SET NULL"), nullable=True
    )
    groom_kundali_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("kundalis.id", ondelete="SET NULL"), nullable=True
    )
    bride_birth_profile_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("birth_profiles.id", ondelete="SET NULL"), nullable=True
    )
    groom_birth_profile_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("birth_profiles.id", ondelete="SET NULL"), nullable=True
    )

    bride_kundali: Mapped[Optional["Kundali"]] = relationship(foreign_keys=[bride_kundali_id])
    groom_kundali: Mapped[Optional["Kundali"]] = relationship(foreign_keys=[groom_kundali_id])
    bride_birth_profile: Mapped[Optional["BirthProfile"]] = relationship(foreign_keys=[bride_birth_profile_id])
    groom_birth_profile: Mapped[Optional["BirthProfile"]] = relationship(foreign_keys=[groom_birth_profile_id])


    # Free-tier: total score only
    total_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    total_max: Mapped[int] = mapped_column(Integer, default=36, nullable=False)
    bride_manglik: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    groom_manglik: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    bride_manglik_severity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    groom_manglik_severity: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Paid-tier (JSONB)
    paid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    koota_breakdown: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)  # list of koota rows
    dosha_analysis: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    verdict_mr: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    verdict_en: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pdf_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    resume_token: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    orders: Mapped[list["Order"]] = relationship(back_populates="matching")


# ──────────────────────────────────────────────────────────────────────────────
# Biodata
# ──────────────────────────────────────────────────────────────────────────────
class Biodata(Base):
    __tablename__ = "biodatas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kundali_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("kundalis.id", ondelete="SET NULL"), nullable=True
    )

    # Form data stored as JSONB — flexible, no rigid column per field
    personal_info: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    family_info: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    education_info: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    horoscope_info: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    expectations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Template selection
    template_id: Mapped[str] = mapped_column(String(50), default="traditional", nullable=False)

    # Photo (stored in R2, URL here)
    photo_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Export
    paid: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    pdf_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    image_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    resume_token: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    orders: Mapped[list["Order"]] = relationship(back_populates="biodata")


# ──────────────────────────────────────────────────────────────────────────────
# Order  (Razorpay order + payment lifecycle)
# ──────────────────────────────────────────────────────────────────────────────
class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # What is being paid for
    product_type: Mapped[str] = mapped_column(
        SAEnum("kundali", "matching", "biodata", "bundle", name="product_type_enum"),
        nullable=False,
    )
    # Optional FK to the product being unlocked
    kundali_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("kundalis.id", ondelete="SET NULL"), nullable=True
    )
    matching_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("matchings.id", ondelete="SET NULL"), nullable=True
    )
    biodata_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("biodatas.id", ondelete="SET NULL"), nullable=True
    )

    # Pricing
    amount_paise: Mapped[int] = mapped_column(Integer, nullable=False)  # INR paise (100 = ₹1)
    currency: Mapped[str] = mapped_column(String(3), default="INR", nullable=False)

    # Razorpay
    razorpay_order_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True, index=True)
    razorpay_payment_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True, nullable=True, index=True)
    razorpay_signature: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Status lifecycle
    status: Mapped[str] = mapped_column(
        SAEnum("created", "attempted", "paid", "failed", "refunded", name="order_status_enum"),
        nullable=False, default="created", index=True,
    )
    paid_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    # Optional customer contact (collected at payment step only)
    customer_phone: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    customer_email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)

    # Relationships
    kundali: Mapped[Optional["Kundali"]] = relationship(back_populates="orders")
    matching: Mapped[Optional["Matching"]] = relationship(back_populates="orders")
    biodata: Mapped[Optional["Biodata"]] = relationship(back_populates="orders")

    __table_args__ = (
        Index("ix_orders_status_created", "status", "created_at"),
    )


# ──────────────────────────────────────────────────────────────────────────────
# Webhook Events  (idempotency log)
# ──────────────────────────────────────────────────────────────────────────────
class WebhookEvent(Base):
    __tablename__ = "webhook_events"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    event_id: Mapped[str] = mapped_column(String(200), unique=True, nullable=False, index=True)
    source: Mapped[str] = mapped_column(String(50), default="razorpay", nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload: Mapped[dict] = mapped_column(JSONB, nullable=False)
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    processed_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    error: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
