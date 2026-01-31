from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CreateProduct(BaseModel):
    """新增产品"""
    name: str = Field(..., description="产品名称")
    description: Optional[str] = Field(None, description="描述")


class UpdateProduct(BaseModel):
    """修改产品"""
    name: Optional[str] = Field(None, description="产品名称")
    description: Optional[str] = Field(None, description="描述")


class ProductInfo(BaseModel):
    """产品信息"""
    id: str = Field(..., description="产品ID")
    name: str = Field(..., description="产品名称")
    description: Optional[str] = Field(None, description="描述")
    create_user_id: str = Field(..., description="创建人ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True
