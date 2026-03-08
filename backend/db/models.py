import uuid
from sqlalchemy import (
    Column,
    String,
    Integer,
    Float,
    Boolean,
    Text,
    DateTime,
    ForeignKey,
    ARRAY,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from .database import Base


class ScrapeSession(Base):
    __tablename__ = "scrape_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform = Column(String(20), nullable=False)  # indeed, seek, careerone
    job_titles = Column(ARRAY(String), nullable=False)
    location = Column(String(255), nullable=False)
    max_pages = Column(Integer, default=3)
    status = Column(
        String(20), default="pending"
    )  # pending, scraping, validating, enriching, completed, failed
    total_jobs = Column(Integer, default=0)
    eligible_jobs = Column(Integer, default=0)
    error_message = Column(Text)
    started_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    jobs = relationship("Job", back_populates="session", cascade="all, delete-orphan")
    companies = relationship(
        "Company", secondary="session_companies", back_populates="sessions"
    )


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("scrape_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    platform = Column(String(20), nullable=False)
    job_title = Column(String(500), nullable=False)
    employer_name = Column(String(500))
    location = Column(String(255))
    job_description = Column(Text)
    salary = Column(String(255))
    posted_date = Column(String(100))
    url = Column(Text, nullable=False)
    search_title = Column(String(500))
    search_location = Column(String(255))
    scraped_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    session = relationship("ScrapeSession", back_populates="jobs")
    assessment = relationship(
        "AnzscoAssessment",
        back_populates="job",
        uselist=False,
        cascade="all, delete-orphan",
    )


class AnzscoAssessment(Base):
    __tablename__ = "anzsco_assessments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(
        UUID(as_uuid=True),
        ForeignKey("jobs.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    eligible = Column(Boolean, default=False)
    occupation = Column(String(500))
    anzsco_code = Column(String(20))
    confidence_score = Column(Float, default=0.0)
    reason = Column(Text)
    assessed_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    job = relationship("Job", back_populates="assessment")


class Company(Base):
    __tablename__ = "companies"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(500), nullable=False)
    description = Column(Text)
    website = Column(String(500))
    industry = Column(String(255))
    source = Column(String(20))
    source_url = Column(Text)
    anzsco_eligible = Column(Boolean, default=False)
    job_count = Column(Integer, default=0)
    hubspot_id = Column(String(100))
    hubspot_status = Column(String(20), default="not_synced")
    hubspot_synced_at = Column(DateTime(timezone=True))
    created_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    sessions = relationship(
        "ScrapeSession", secondary="session_companies", back_populates="companies"
    )

    __table_args__ = (
        UniqueConstraint("name", "source", name="uq_company_name_source"),
    )


class SessionCompany(Base):
    __tablename__ = "session_companies"

    session_id = Column(
        UUID(as_uuid=True),
        ForeignKey("scrape_sessions.id", ondelete="CASCADE"),
        primary_key=True,
    )
    company_id = Column(
        UUID(as_uuid=True),
        ForeignKey("companies.id", ondelete="CASCADE"),
        primary_key=True,
    )
