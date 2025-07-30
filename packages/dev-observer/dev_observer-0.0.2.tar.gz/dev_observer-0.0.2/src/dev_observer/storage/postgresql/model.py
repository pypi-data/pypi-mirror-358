import datetime
from typing import Optional

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class GitRepoEntity(Base):
    __tablename__ = "git_repo"

    id: Mapped[str] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(index=True, unique=True)
    json_data: Mapped[str]

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"GitRepoEntity(id={self.id}, json_data={self.json_data})"


class GlobalConfigEntity(Base):
    __tablename__ = "global_config"

    id: Mapped[str] = mapped_column(primary_key=True)
    json_data: Mapped[str]

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"GlobalConfigEntity(id={self.id}, json_data={self.json_data})"


class ProcessingItemEntity(Base):
    __tablename__ = "processing_item"
    key: Mapped[str] = mapped_column(primary_key=True)
    json_data: Mapped[str]
    next_processing: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    last_processed: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime(timezone=True))
    last_error: Mapped[Optional[str]]
    no_processing: Mapped[bool] = mapped_column(default=False)

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"ProcessingItemEntity(key={self.key}, json_data={self.json_data}, next_processing={self.next_processing}, last_processed={self.last_processed}, last_error={self.last_error}, no_processing={self.no_processing})"


class WebsiteEntity(Base):
    __tablename__ = "web_site"

    id: Mapped[str] = mapped_column(primary_key=True)
    url: Mapped[str] = mapped_column(index=True, unique=True)
    json_data: Mapped[str]

    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self):
        return f"WebsiteEntity(id={self.id}, json_data={self.json_data})"