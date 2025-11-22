from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship, DeclarativeBase
from datetime import datetime


class Base(DeclarativeBase):
    pass


class TeamDB(Base):
    __tablename__ = "teams"

    team_name = Column(String, primary_key=True)
    members = relationship("UserDB", back_populates="team")


class UserDB(Base):
    __tablename__ = "users"

    user_id = Column(String, primary_key=True)
    username = Column(String, nullable=False)
    team_name = Column(String, ForeignKey("teams.team_name"))  # Fixed: points to team_name
    is_active = Column(Boolean, default=True)

    team = relationship("TeamDB", back_populates="members")
    assigned_prs = relationship("PullRequestDB", secondary="pr_reviewers", back_populates="reviewers")


class PullRequestDB(Base):
    __tablename__ = "pull_requests"

    pull_request_id = Column(String, primary_key=True)
    pull_request_name = Column(String, nullable=False)
    author_id = Column(String, ForeignKey("users.user_id"))
    status = Column(String, default="OPEN")
    created_at = Column(DateTime, default=datetime.now)
    merged_at = Column(DateTime, nullable=True)

    reviewers = relationship("UserDB", secondary="pr_reviewers", back_populates="assigned_prs")


pr_reviewers = Table(
    "pr_reviewers",
    Base.metadata,
    Column("pr_id", String, ForeignKey("pull_requests.pull_request_id"), primary_key=True),
    Column("user_id", String, ForeignKey("users.user_id"), primary_key=True),
)
