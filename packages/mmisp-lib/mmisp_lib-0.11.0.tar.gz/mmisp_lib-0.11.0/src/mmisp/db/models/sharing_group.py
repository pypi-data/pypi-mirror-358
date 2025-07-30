from datetime import datetime

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mmisp.db.mixins import DictMixin, UpdateMixin
from mmisp.db.types import DBUUID
from mmisp.lib.uuid import uuid

from ..database import Base


class SharingGroup(Base, UpdateMixin, DictMixin["SharingGroupDict"]):
    __tablename__ = "sharing_groups"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    name = mapped_column(String(255), nullable=False, unique=True)
    releasability = mapped_column(Text, nullable=False)
    description = mapped_column(Text, nullable=False, default="")
    uuid = mapped_column(DBUUID, unique=True, default=uuid, nullable=False)
    organisation_uuid = mapped_column(DBUUID, nullable=False)
    org_id = mapped_column(Integer, nullable=False, index=True)  # the organisation that created the sharing group
    sync_user_id = mapped_column(Integer, nullable=False, default=0, index=True)
    active = mapped_column(Boolean, nullable=False, default=False)
    created = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    modified = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    local = mapped_column(Boolean, nullable=False, default=True)
    roaming = mapped_column(Boolean, default=False, nullable=False)

    creator_org = relationship(
        "Organisation",
        primaryjoin="SharingGroup.org_id == Organisation.id",
        lazy="raise_on_sql",
        foreign_keys="SharingGroup.org_id",
    )  # type:ignore[assignment,var-annotated]
    organisations = relationship(
        "Organisation",
        primaryjoin="SharingGroup.id == SharingGroupOrg.sharing_group_id",
        secondary="sharing_group_orgs",
        secondaryjoin="SharingGroupOrg.org_id == Organisation.id",
        lazy="selectin",
        viewonly=True,
    )

    sharing_group_orgs = relationship(
        "SharingGroupOrg",
        primaryjoin="SharingGroup.id == SharingGroupOrg.sharing_group_id",
        lazy="raise_on_sql",
        foreign_keys="SharingGroupOrg.sharing_group_id",
    )  # type:ignore[assignment,var-annotated]
    sharing_group_servers = relationship(
        "SharingGroupServer",
        primaryjoin="SharingGroup.id == SharingGroupServer.sharing_group_id",
        lazy="raise_on_sql",
        foreign_keys="SharingGroupServer.sharing_group_id",
    )  # type:ignore[assignment,var-annotated]


class SharingGroupOrg(Base, UpdateMixin, DictMixin["SharingGroupOrgDict"]):
    __tablename__ = "sharing_group_orgs"

    id = mapped_column(Integer, primary_key=True, nullable=False)
    sharing_group_id = mapped_column(Integer, index=True, nullable=False)
    org_id = mapped_column(Integer, index=True, nullable=False)
    extend = mapped_column(Boolean, default=False, nullable=False)

    organisation = relationship(
        "Organisation",
        primaryjoin="SharingGroupOrg.org_id == Organisation.id",
        lazy="raise_on_sql",
        foreign_keys="SharingGroupOrg.org_id",
    )  # type:ignore[assignment,var-annotated]


class SharingGroupServer(Base, UpdateMixin, DictMixin["SharingGroupServerDict"]):
    __tablename__ = "sharing_group_servers"

    id = mapped_column(Integer, primary_key=True, nullable=False)
    sharing_group_id = mapped_column(Integer, index=True, nullable=False)
    server_id = mapped_column(Integer, index=True, nullable=False)
    all_orgs = mapped_column(Boolean, index=True, nullable=False, default=False)

    server = relationship(
        "Server",
        primaryjoin="SharingGroupServer.server_id == Server.id",
        lazy="raise_on_sql",
        foreign_keys="SharingGroupServer.server_id",
    )  # type:ignore[assignment,var-annotated]
