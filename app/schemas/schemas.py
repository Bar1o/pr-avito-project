from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


# --- Enums ---
class PRStatus(str, Enum):
    OPEN = "OPEN"
    MERGED = "MERGED"


# --- Core Models ---
class TeamMember(BaseModel):
    user_id: str
    username: str
    is_active: bool


class Team(BaseModel):
    team_name: str
    members: list[TeamMember]


class User(BaseModel):
    user_id: str
    username: str
    team_name: str
    is_active: bool


class PullRequestShort(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PRStatus


class PullRequest(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PRStatus
    assigned_reviewers: list[str]
    created_at: datetime | None = Field(None, serialization_alias="createdAt")
    merged_at: datetime | None = Field(None, serialization_alias="mergedAt")

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)


# --- Request Bodies ---
class UserIsActiveUpdate(BaseModel):
    user_id: str
    is_active: bool


class PullRequestCreate(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str


class PullRequestMerge(BaseModel):
    pull_request_id: str


class PullRequestReassign(BaseModel):
    pull_request_id: str
    old_user_id: str


# --- Response Wrappers ---
class TeamResponseWrapper(BaseModel):
    team: Team


class UserResponseWrapper(BaseModel):
    user: User


class PRResponseWrapper(BaseModel):
    pr: PullRequest


class ReassignResponse(BaseModel):
    pr: PullRequest
    replaced_by: str


class UserReviewsResponse(BaseModel):
    user_id: str
    pull_requests: list[PullRequestShort]
