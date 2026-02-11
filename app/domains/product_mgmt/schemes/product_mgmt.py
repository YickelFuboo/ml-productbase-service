from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class CreateProduct(BaseModel):
    """新增产品"""
    name: str = Field(..., description="产品名称")
    description: Optional[str] = Field(None, description="描述")
    product_define: Optional[str] = Field(None, description="产品定义，一般为MD文档，描述产品定位、周边关系等")


class UpdateProduct(BaseModel):
    """修改产品"""
    name: Optional[str] = Field(None, description="产品名称")
    description: Optional[str] = Field(None, description="描述")
    product_define: Optional[str] = Field(None, description="产品定义，一般为MD文档")
    owner_id: Optional[str] = Field(None, description="数据Owner ID")


class ProductInfo(BaseModel):
    """产品信息"""
    id: str = Field(..., description="产品ID")
    name: str = Field(..., description="产品名称")
    description: Optional[str] = Field(None, description="描述")
    product_define: Optional[str] = Field(None, description="产品定义，一般为MD文档")
    create_user_id: str = Field(..., description="创建人ID")
    owner_id: Optional[str] = Field(None, description="数据Owner ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    model_config = ConfigDict(from_attributes=True)


class ProductWithVersionsInfo(BaseModel):
    """产品信息（含其下版本列表）"""
    id: str = Field(..., description="产品ID")
    name: str = Field(..., description="产品名称")
    description: Optional[str] = Field(None, description="描述")
    product_define: Optional[str] = Field(None, description="产品定义")
    create_user_id: str = Field(..., description="创建人ID")
    owner_id: Optional[str] = Field(None, description="数据Owner ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    versions: List["VersionInfo"] = Field(default_factory=list, description="该产品下的版本列表")

    model_config = ConfigDict(from_attributes=True)


class CreateVersion(BaseModel):
    """新增版本"""
    name: str = Field(..., description="版本名称")
    product_id: str = Field(..., description="所属产品ID")


class UpdateVersion(BaseModel):
    """修改版本"""
    name: Optional[str] = Field(None, description="版本名称")
    owner_id: Optional[str] = Field(None, description="数据Owner ID")


class VersionInfo(BaseModel):
    """版本信息"""
    id: str = Field(..., description="版本ID")
    name: str = Field(..., description="版本名称")
    product_id: str = Field(..., description="所属产品ID")
    create_user_id: str = Field(..., description="创建人ID")
    owner_id: Optional[str] = Field(None, description="数据Owner ID")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    model_config = ConfigDict(from_attributes=True)


ProductWithVersionsInfo.model_rebuild()