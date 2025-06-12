from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime, UTC


def utcnow() -> datetime:
    return datetime.now(tz=UTC)


class Base(SQLModel):
    id: Optional[int] = Field(
        default=None,
        primary_key=True,
    )
    created_at: datetime = Field(
        default_factory=utcnow,
    )


class URL(Base, table=True):
    __tablename__ = "url"

    original_url: str = Field(
        index=True,
        unique=True,
    )
    short_code: str = Field(
        index=True,
        unique=True,
    )

    visits: List["URLVisit"] = Relationship(
        back_populates="url",
    )


class URLVisit(Base, table=True):
    __tablename__ = "url_visit"

    url_id: int = Field(
        foreign_key="url.id",
        index=True,
    )
    timestamp: datetime = Field(
        default_factory=utcnow,
    )
    ip_address: Optional[str] = Field(
        default=None,
    )

    url: Optional[URL] = Relationship(
        back_populates="visits",
    )
