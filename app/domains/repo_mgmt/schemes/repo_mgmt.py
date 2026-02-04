from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CreateRepositoryFromUrl(BaseModel):
    """通过Git URL创建仓库"""
    repo_url: str = Field(..., description="Git仓库URL")
    branch: str = Field(default="main", description="分支名称")
    description: str = Field(default="", description="仓库描述")

    @field_validator("repo_url")
    @classmethod
    def validate_repo_url(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("仓库URL不能为空")
        if not v.startswith(("http://", "https://", "git@")):
            raise ValueError("无效的Git仓库URL")
        return v.strip()

    @field_validator("branch")
    @classmethod
    def validate_branch(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("分支名称不能为空")
        return v.strip()


class UpdateRepository(BaseModel):
    """更新仓库"""
    description: Optional[str] = Field(None, description="仓库描述")
    branch: Optional[str] = Field(None, description="分支名称")

    @field_validator("branch")
    @classmethod
    def validate_branch(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not v.strip():
            raise ValueError("分支名称不能为空")
        return v.strip() if v else v


class RepositoryInfo(BaseModel):
    """仓库信息"""
    id: str = Field(..., description="仓库ID")
    create_user_id: str = Field(..., description="创建用户ID")
    git_type: str = Field(..., description="仓库类型")
    repo_url: str = Field(..., description="仓库URL")
    repo_organization: str = Field(..., description="组织")
    repo_name: str = Field(..., description="仓库名称")
    repo_description: str = Field(..., description="仓库描述")
    repo_branch: str = Field(..., description="分支")
    local_path: Optional[str] = Field(None, description="本地路径")
    version: Optional[str] = Field(None, description="版本")
    is_cloned: bool = Field(..., description="是否克隆完成")
    is_chunked: bool = Field(..., description="是否分块完成")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True
