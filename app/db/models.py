from typing import Optional, List
from datetime import datetime, UTC

from sqlmodel import SQLModel, Field, Relationship


# Utility function for consistent UTC timestamping
def utcnow() -> datetime:
    return datetime.now(tz=UTC)


# -----------------------
# Base model for all tables
# -----------------------
class Base(SQLModel):
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
        description="Primary key"
    )
    created_at: datetime = Field(
        default_factory=utcnow,
        description="Creation timestamp in UTC"
    )


# -----------------------
# URL Table
# -----------------------
class URL(Base, table=True):
    __tablename__ = "url"

    original_url: str = Field(
        index=True,
        unique=True,
        description="The original long URL"
    )
    short_code: str = Field(
        index=True,
        unique=True,
        min_length=4,
        max_length=32,
        description="Unique short code for redirection"
    )

    # All visit records associated with this URL
    visits: List["URLVisit"] = Relationship(
        back_populates="url",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


# -----------------------
# URLVisit Table (tracks each visit)
# -----------------------
class URLVisit(Base, table=True):
    __tablename__ = "url_visit"

    url_id: int = Field(
        foreign_key="url.id",
        index=True,
        description="Foreign key referencing the URL table"
    )
    timestamp: datetime = Field(
        default_factory=utcnow,
        description="Visit timestamp (UTC)"
    )
    ip_address: Optional[str] = Field(
        default=None,
        max_length=45,  # Enough to support IPv6
        description="Visitor IP address"
    )

    # Parent URL record
    url: Optional[URL] = Relationship(
        back_populates="visits",
    )
