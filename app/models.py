from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship, DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime


class Base(DeclarativeBase):
    pass


pr_reviewers = Table(
    "pr_reviewers",
    Base.metadata,
    Column("pr_id", String, ForeignKey("pull_requests.id"), primary_key=True),
    Column("user_id", String, ForeignKey("users.id"), primary_key=True),
)


class UserDB(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    team_name = Column(String, ForeignKey("teams.name"))

    team = relationship("TeamDB", back_populates="members")
    assigned_prs = relationship("PullRequestDB", secondary=pr_reviewers, back_populates="reviewers")


class TeamDB(Base):
    __tablename__ = "teams"

    name = Column(String, primary_key=True)
    members = relationship("UserDB", back_populates="team")


class PullRequestDB(Base):
    __tablename__ = "pull_requests"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    author_id = Column(String, ForeignKey("users.id"))
    status = Column(String, default="OPEN")
    created_at = Column(DateTime, default=datetime.now)
    merged_at = Column(DateTime, nullable=True)

    reviewers = relationship("UserDB", secondary=pr_reviewers, back_populates="assigned_prs")
