from typing import Optional

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from mmisp.db.mixins import DictMixin, UpdateMixin
from mmisp.db.models.tag import Tag
from mmisp.db.types import DBUUID, DBListJson
from mmisp.lib.uuid import uuid

from ..database import Base


class GalaxyCluster(Base, UpdateMixin, DictMixin["GalaxyClusterDict"]):
    __tablename__ = "galaxy_clusters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    uuid: Mapped[str] = mapped_column(DBUUID, default=uuid, nullable=False, index=True)
    collection_uuid: Mapped[str] = mapped_column(DBUUID, nullable=False, index=True, default="")
    type: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)
    tag_name: Mapped[str] = mapped_column(String(255), nullable=False, default="", index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    galaxy_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("galaxies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    source: Mapped[str] = mapped_column(String(255), nullable=False, default="")
    authors: Mapped[list[str]] = mapped_column(DBListJson, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=0, index=True)
    distribution: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sharing_group_id: Mapped[Optional[int]] = mapped_column(Integer, index=True, nullable=True, default=None)
    org_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, default=0)
    orgc_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True, default=0)
    default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)
    locked: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    extends_uuid: Mapped[str | None] = mapped_column(DBUUID, nullable=True, default=None, index=True)
    extends_version: Mapped[int | None] = mapped_column(Integer, index=True, nullable=True, default=None)
    published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    deleted: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    org = relationship(
        "Organisation",
        primaryjoin="GalaxyCluster.org_id == Organisation.id",
        back_populates="galaxy_clusters",
        lazy="raise_on_sql",
        foreign_keys="GalaxyCluster.org_id",
    )  # type:ignore[assignment,var-annotated]
    orgc = relationship(
        "Organisation",
        primaryjoin="GalaxyCluster.orgc_id == Organisation.id",
        back_populates="galaxy_clusters_created",
        lazy="raise_on_sql",
        foreign_keys="GalaxyCluster.orgc_id",
    )  # type:ignore[assignment,var-annotated]
    galaxy = relationship(
        "Galaxy",
        back_populates="galaxy_clusters",
        lazy="raise_on_sql",
    )  # type:ignore[assignment,var-annotated]
    galaxy_elements = relationship(
        "GalaxyElement",
        back_populates="galaxy_cluster",
        lazy="raise_on_sql",
    )  # type:ignore[assignment,var-annotated]
    cluster_relations: Mapped[list["GalaxyClusterRelation"]] = relationship(
        "GalaxyClusterRelation",
        back_populates="galaxy_cluster",
        lazy="raise_on_sql",
        foreign_keys="GalaxyClusterRelation.galaxy_cluster_id",
    )
    tag = relationship(
        "Tag",
        primaryjoin="GalaxyCluster.tag_name == Tag.name",
        back_populates="galaxy_cluster",
        lazy="raise_on_sql",
        foreign_keys="GalaxyCluster.tag_name",
        single_parent=True,
        uselist=False,
    )  # type:ignore[assignment,var-annotated]


class GalaxyElement(Base, DictMixin["GalaxyElementDict"], UpdateMixin):
    __tablename__ = "galaxy_elements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    galaxy_cluster_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(GalaxyCluster.id, ondelete="CASCADE"), nullable=False, index=True
    )
    key: Mapped[str] = mapped_column(String(255), nullable=False, default="", index=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)

    galaxy_cluster = relationship(
        "GalaxyCluster",
        back_populates="galaxy_elements",
        lazy="raise_on_sql",
    )  # type:ignore[assignment,var-annotated]


galaxy_relation_tag = Table(
    "galaxy_cluster_relation_tags",
    Base.metadata,
    Column("id", Integer, primary_key=True, nullable=False),
    Column(
        "galaxy_cluster_relation_id", Integer, ForeignKey("galaxy_cluster_relations.id"), nullable=False, index=True
    ),
    Column("tag_id", Integer, ForeignKey("tags.id"), nullable=False, index=True),
)


class GalaxyClusterRelation(Base, DictMixin["GalaxyClusterRelationDict"], UpdateMixin):
    __tablename__ = "galaxy_cluster_relations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    galaxy_cluster_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(GalaxyCluster.id, ondelete="CASCADE"), nullable=False, index=True
    )
    referenced_galaxy_cluster_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    referenced_galaxy_cluster_uuid: Mapped[str] = mapped_column(DBUUID, nullable=False, index=True)
    referenced_galaxy_cluster_type: Mapped[str] = mapped_column(Text, nullable=False)
    galaxy_cluster_uuid: Mapped[str] = mapped_column(DBUUID, nullable=False, index=True)
    distribution: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    sharing_group_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("sharing_groups.id"), index=True, nullable=True, default=None
    )
    default: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False, index=True)

    galaxy_cluster: Mapped[GalaxyCluster] = relationship(
        "GalaxyCluster",
        back_populates="cluster_relations",
        lazy="raise_on_sql",
        foreign_keys="GalaxyClusterRelation.galaxy_cluster_id",
    )
    relation_tags: Mapped[list[Tag]] = relationship("Tag", secondary=galaxy_relation_tag, lazy="raise_on_sql")


# TODO delete this class and rewrite dependent code in mmisp/api/routers/galaxies_cluster.py
class GalaxyReference(Base, DictMixin["GalaxyReferenceDict"]):
    __tablename__ = "galaxy_reference"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    galaxy_cluster_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(GalaxyCluster.id, ondelete="CASCADE"), nullable=False, index=True
    )
    referenced_galaxy_cluster_id: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    referenced_galaxy_cluster_uuid: Mapped[str] = mapped_column(DBUUID, nullable=False, index=True)
    referenced_galaxy_cluster_type: Mapped[str] = mapped_column(Text, nullable=False)
    referenced_galaxy_cluster_value: Mapped[str] = mapped_column(Text, nullable=False)
