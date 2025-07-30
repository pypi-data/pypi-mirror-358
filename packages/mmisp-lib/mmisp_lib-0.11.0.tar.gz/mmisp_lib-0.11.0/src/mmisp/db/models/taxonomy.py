from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base


class Taxonomy(Base):
    __tablename__ = "taxonomies"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    namespace: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    exclusive: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=False)
    required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    highlighted: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=False)

    predicates: Mapped[list["TaxonomyPredicate"]] = relationship(
        "TaxonomyPredicate", back_populates="taxonomy", lazy="raise_on_sql"
    )


class TaxonomyPredicate(Base):
    __tablename__ = "taxonomy_predicates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    taxonomy_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(Taxonomy.id, ondelete="CASCADE"), nullable=False, index=True
    )
    value: Mapped[str] = mapped_column(Text, nullable=False)
    expanded: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    colour: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    exclusive: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True, default=False)
    numerical_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)

    taxonomy: Mapped[Taxonomy] = relationship(Taxonomy, back_populates="predicates", lazy="raise_on_sql")
    entries: Mapped[list["TaxonomyEntry"]] = relationship(
        "TaxonomyEntry", back_populates="predicate", lazy="raise_on_sql"
    )


class TaxonomyEntry(Base):
    __tablename__ = "taxonomy_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    taxonomy_predicate_id: Mapped[int] = mapped_column(
        Integer, ForeignKey(TaxonomyPredicate.id, ondelete="CASCADE"), nullable=False, index=True
    )
    value: Mapped[str] = mapped_column(Text, nullable=False)
    expanded: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    colour: Mapped[Optional[str]] = mapped_column(String(7), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    numerical_value: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)

    predicate: Mapped[TaxonomyPredicate] = relationship(
        TaxonomyPredicate, back_populates="entries", lazy="raise_on_sql"
    )
