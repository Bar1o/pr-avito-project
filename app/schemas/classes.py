from pydantic import BaseModel, ConfigDict
from typing import Annotated, List, Optional
from enum import Enum
from datetime import datetime


class PRStatus(str, Enum):
    OPEN = "OPEN"
    MERGED = "MERGED"


class UserBase(BaseModel):
    user_id: str
    username: str
    teamname: str
    is_active: bool


class TeamCreate(BaseModel):
    team_name: str
    members: List[UserBase]


class TeamResponse(BaseModel):
    pass


class PullRequestCreate(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str


class PullRequestResponse(BaseModel):
    pull_request_id: str
    pull_request_name: str
    author_id: str
    status: PRStatus
    assigned_reviewers: List[str]
    created_at: Optional[datetime] = None
    merged_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
