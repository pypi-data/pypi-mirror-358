from sqlalchemy import Integer, String

from mmisp.db.mypy import Mapped, mapped_column

from ..database import Base


class Tasks(Base):
    """
    A python class representation of the database model for tasks in MISP.

    """

    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, nullable=False)
    type: Mapped[str] = mapped_column(String(100), nullable=False)
    timer: Mapped[int] = mapped_column(Integer, nullable=False)
    scheduled_time: Mapped[String] = mapped_column(String(8), nullable=False, default="6:00")
    process_id: Mapped[str] = mapped_column(String(32), nullable=True)
    description: Mapped[str] = mapped_column(String(255), nullable=False)
    next_execution_time: Mapped[int] = mapped_column(Integer, nullable=False)
    message: Mapped[str] = mapped_column(String(255), nullable=False)
