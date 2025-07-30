from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mmisp.db.database import Base
from mmisp.db.mixins import DictMixin
from mmisp.db.types import DBUUID, DateTimeEpoch, DBListJson, DBObjectJson
from mmisp.lib.uuid import uuid


class Object(Base, DictMixin["ObjectDict"]):
    __tablename__ = "objects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    uuid: Mapped[str] = mapped_column(DBUUID, unique=True, default=uuid, index=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    meta_category: Mapped[str] = mapped_column("meta-category", String(255), index=True)
    description: Mapped[str] = mapped_column(String(255))
    template_uuid: Mapped[str] = mapped_column(String(255), index=True, default=None)
    template_version: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    event_id: Mapped[int] = mapped_column(Integer, ForeignKey("events.id"), index=True, nullable=False)
    timestamp: Mapped[datetime] = mapped_column(DateTimeEpoch, index=True, nullable=False, default=0)
    distribution: Mapped[int] = mapped_column(Integer, index=True, nullable=False, default=0)
    sharing_group_id: Mapped[int] = mapped_column(Integer, ForeignKey("sharing_groups.id"), index=True)
    comment: Mapped[str] = mapped_column(String(255), nullable=False)
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    first_seen: Mapped[int] = mapped_column(Integer, index=True, default=None)
    last_seen: Mapped[int] = mapped_column(Integer, index=True, default=None)

    attributes = relationship(
        "Attribute",
        primaryjoin="Object.id == Attribute.object_id",
        back_populates="mispobject",
        lazy="raise_on_sql",
        foreign_keys="Attribute.object_id",
    )  # type:ignore[var-annotated]
    event = relationship(
        "Event",
        back_populates="mispobjects",
        lazy="raise_on_sql",
    )  # type:ignore[var-annotated]


class ObjectTemplate(Base, DictMixin["ObjectTemplateDict"]):
    __tablename__ = "object_templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    org_id: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    uuid: Mapped[str] = mapped_column(DBUUID, unique=True, default=uuid, index=True)
    name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    meta_category: Mapped[Optional[str]] = mapped_column(
        "meta-category", String(255), nullable=True, index=True, key="meta_category"
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    requirements: Mapped[dict | None] = mapped_column(DBObjectJson, nullable=True)
    fixed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    elements: Mapped[list["ObjectTemplateElement"]] = relationship(
        "ObjectTemplateElement", back_populates="object_template", lazy="raise_on_sql"
    )


class ObjectTemplateElement(Base, DictMixin["ObjectTemplateElementDict"]):
    __tablename__ = "object_template_elements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    object_template_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(ObjectTemplate.id, ondelete="CASCADE"), nullable=False, index=True
    )
    object_relation: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, index=True)
    type: Mapped[Optional[str]] = mapped_column(Text, nullable=True, index=True)
    ui_priority: Mapped[int] = mapped_column("ui-priority", Integer, nullable=False, key="ui_priority")
    categories: Mapped[list[str] | None] = mapped_column(DBListJson, nullable=True)
    sane_default: Mapped[list[str] | None] = mapped_column(DBListJson, nullable=True)
    values_list: Mapped[list[str] | None] = mapped_column(DBListJson, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    disable_correlation: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)
    multiple: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    object_template: Mapped[ObjectTemplate] = relationship(
        ObjectTemplate, back_populates="elements", lazy="raise_on_sql"
    )
