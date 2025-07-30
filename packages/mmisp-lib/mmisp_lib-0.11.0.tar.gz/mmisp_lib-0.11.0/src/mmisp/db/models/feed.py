from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import mapped_column

from mmisp.db.database import Base
from mmisp.db.mixins import DictMixin, UpdateMixin
from mmisp.db.mypy import Mapped


class Feed(Base, UpdateMixin, DictMixin["FeedDict"]):
    __tablename__ = "feeds"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[str] = mapped_column(String(255), nullable=False)
    url: Mapped[str] = mapped_column(String(255), nullable=False)
    rules: Mapped[str | None] = mapped_column(Text, nullable=True)
    enabled: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    distribution: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sharing_group_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    tag_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    default: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    source_format: Mapped[str | None] = mapped_column(String(255), nullable=True, default="misp")
    fixed_event: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    delta_merge: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    event_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    publish: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    override_ids: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    settings: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_source: Mapped[str] = mapped_column(String(255), nullable=False, default="network", index=True)
    delete_local_file: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    lookup_visible: Mapped[bool | None] = mapped_column(Boolean, nullable=True, default=False)
    headers: Mapped[str | None] = mapped_column(Text, nullable=True)
    caching_enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    force_to_ids: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    orgc_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0, index=True)
    tag_collection_id: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
