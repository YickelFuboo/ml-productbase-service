from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel


class GitAuthProvider(Enum):
    GITHUB = "github"
    GITEE = "gitee"
    GITLAB = "gitlab"

    @classmethod
    def values(cls):
        return [e.value for e in cls]


class GitAuthResponse(BaseModel):
    id: str
    user_id: str
    provider: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class GitAuthListResponse(BaseModel):
    items: list[GitAuthResponse]
    total: int
