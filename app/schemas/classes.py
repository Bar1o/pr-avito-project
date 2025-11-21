from pydantic import BaseModel
from typing import Annotated, List, Optional
from enum import Enum


class PRStatus(str, Enum):
    OPEN = "OPEN"
    MERGED = "MERGED"


class User(BaseModel):
    id: str  # unique
    name: str
    is_active: bool

    team: str  # maybe i need a method that gets user's team name


class Team(BaseModel):
    name: str  # must be a unique name
    users: List[User] = []


class PullRequest(BaseModel):
    id: str
    name: str
    author: User
    status: PRStatus = PRStatus.OPEN
    reviewers: List[str] = []
    _MAX_REVIEWERS: int = 2


class ReviewerService:
    def __init__(self):
        # check number of users in author's team available (isActive == True) (except the author)
        # if available > 2: set two of them randomly
        # if only 1 is av: set them
        # if 0: set noone
        self.teams: dict[str, Team] = {}
        self.users: dict[str, User] = {}
        self.prs: dict[str, PullRequest] = {}

    def is_available(user: User) -> bool:
        pass

    def update_reviewers(user_to_remove: User):
        # change one of reviewers to one from available
        pass
