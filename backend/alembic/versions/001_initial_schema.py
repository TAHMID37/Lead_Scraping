"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-09

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # scrape_sessions
    op.create_table(
        "scrape_sessions",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("platform", sa.String(20), nullable=False),
        sa.Column("job_titles", sa.ARRAY(sa.String), nullable=False),
        sa.Column("location", sa.String(255), nullable=False),
        sa.Column("max_pages", sa.Integer, default=3),
        sa.Column("status", sa.String(20), default="pending"),
        sa.Column("total_jobs", sa.Integer, default=0),
        sa.Column("eligible_jobs", sa.Integer, default=0),
        sa.Column("error_message", sa.Text),
        sa.Column("started_at", sa.DateTime(timezone=True)),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_scrape_sessions_platform", "scrape_sessions", ["platform"])
    op.create_index("ix_scrape_sessions_status", "scrape_sessions", ["status"])
    op.create_index("ix_scrape_sessions_created_at", "scrape_sessions", ["created_at"])

    # jobs
    op.create_table(
        "jobs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "session_id",
            UUID(as_uuid=True),
            sa.ForeignKey("scrape_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("platform", sa.String(20), nullable=False),
        sa.Column("job_title", sa.String(500), nullable=False),
        sa.Column("employer_name", sa.String(500)),
        sa.Column("location", sa.String(255)),
        sa.Column("job_description", sa.Text),
        sa.Column("salary", sa.String(255)),
        sa.Column("posted_date", sa.String(100)),
        sa.Column("url", sa.Text, nullable=False),
        sa.Column("search_title", sa.String(500)),
        sa.Column("search_location", sa.String(255)),
        sa.Column("scraped_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_jobs_session_id", "jobs", ["session_id"])
    op.create_index("ix_jobs_platform", "jobs", ["platform"])
    op.create_index("ix_jobs_employer_name", "jobs", ["employer_name"])
    op.create_index("ix_jobs_job_title", "jobs", ["job_title"])

    # anzsco_assessments
    op.create_table(
        "anzsco_assessments",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "job_id",
            UUID(as_uuid=True),
            sa.ForeignKey("jobs.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("eligible", sa.Boolean, default=False),
        sa.Column("occupation", sa.String(500)),
        sa.Column("anzsco_code", sa.String(20)),
        sa.Column("confidence_score", sa.Float, default=0.0),
        sa.Column("reason", sa.Text),
        sa.Column("assessed_at", sa.DateTime(timezone=True)),
    )
    op.create_index("ix_anzsco_assessments_job_id", "anzsco_assessments", ["job_id"])
    op.create_index(
        "ix_anzsco_assessments_eligible", "anzsco_assessments", ["eligible"]
    )
    op.create_index(
        "ix_anzsco_assessments_anzsco_code", "anzsco_assessments", ["anzsco_code"]
    )

    # companies
    op.create_table(
        "companies",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("description", sa.Text),
        sa.Column("website", sa.String(500)),
        sa.Column("industry", sa.String(255)),
        sa.Column("source", sa.String(20)),
        sa.Column("source_url", sa.Text),
        sa.Column("anzsco_eligible", sa.Boolean, default=False),
        sa.Column("job_count", sa.Integer, default=0),
        sa.Column("hubspot_id", sa.String(100)),
        sa.Column("hubspot_status", sa.String(20), default="not_synced"),
        sa.Column("hubspot_synced_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True)),
        sa.Column("updated_at", sa.DateTime(timezone=True)),
        sa.UniqueConstraint("name", "source", name="uq_company_name_source"),
    )
    op.create_index("ix_companies_name", "companies", ["name"])
    op.create_index("ix_companies_source", "companies", ["source"])
    op.create_index(
        "ix_companies_hubspot_status", "companies", ["hubspot_status"]
    )
    op.create_index(
        "ix_companies_anzsco_eligible", "companies", ["anzsco_eligible"]
    )

    # session_companies
    op.create_table(
        "session_companies",
        sa.Column(
            "session_id",
            UUID(as_uuid=True),
            sa.ForeignKey("scrape_sessions.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "company_id",
            UUID(as_uuid=True),
            sa.ForeignKey("companies.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )


def downgrade() -> None:
    op.drop_table("session_companies")
    op.drop_table("companies")
    op.drop_table("anzsco_assessments")
    op.drop_table("jobs")
    op.drop_table("scrape_sessions")
