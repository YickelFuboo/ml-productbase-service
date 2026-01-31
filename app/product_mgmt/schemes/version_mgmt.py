from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CreateVersion(BaseModel):
    """新增版本"""
    name: str = Field(..., description="版本名称")
    product_id: str = Field(..., description="所属产品ID")
    description: Optional[str] = Field(None, description="描述")


class UpdateVersion(BaseModel):
    """修改版本"""
    name: Optional[str] = Field(None, description="版本名称")
    description: Optional[str] = Field(None, description="描述")


class VersionInfo(BaseModel):
    """版本信息"""
    id: str = Field(..., description="版本ID")
    name: str = Field(..., description="版本名称")
    product_id: str = Field(..., description="所属产品ID")
    description: Optional[str] = Field(None, description="描述")
    create_user_id: str = Field(..., description="创建人ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True
