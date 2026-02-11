"""
接口视图 DTO：Interface、ElementInterface
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.domains.arch_mgmt.models.interfaces import (
    ArchInterfaceCategory,
    ArchPhysicalInterfaceType,
    ArchElementInterfaceRelationType,
)


class ArchInterfaceCreate(BaseModel):
    version_id: str = Field(..., description="版本ID")
    interface_category: str = Field(..., description=f"接口类别：{'|'.join(ArchInterfaceCategory.values())}")
    parent_id: Optional[str] = Field(None, description="父接口ID（逻辑接口可分层定义，物理接口的父接口是最底层的逻辑接口）")
    name: str = Field(..., description="接口名称")
    code: Optional[str] = Field(None, description="编码/代号")
    description: Optional[str] = Field(None, description="说明")
    definition: Optional[str] = Field(None, description="功能级定义说明")
    specification: Optional[str] = Field(None, description="规格")
    constraints: Optional[str] = Field(None, description="约束")
    interface_type: Optional[str] = Field(None, description=f"物理接口类型（仅物理接口使用）：{'|'.join(ArchPhysicalInterfaceType.values())}")
    tech_stack: Optional[str] = Field(None, description="技术栈（仅物理接口使用）")


class ArchInterfaceUpdate(BaseModel):
    name: Optional[str] = None
    code: Optional[str] = None
    description: Optional[str] = None
    definition: Optional[str] = None
    specification: Optional[str] = None
    constraints: Optional[str] = None
    parent_id: Optional[str] = None
    interface_type: Optional[str] = None
    tech_stack: Optional[str] = None
    owner_id: Optional[str] = None


class ArchInterfaceInfo(BaseModel):
    id: str
    version_id: str
    interface_category: str
    parent_id: Optional[str] = None
    name: str
    code: Optional[str] = None
    description: Optional[str] = None
    definition: Optional[str] = None
    specification: Optional[str] = None
    constraints: Optional[str] = None
    interface_type: Optional[str] = None
    tech_stack: Optional[str] = None
    create_user_id: Optional[str] = None
    owner_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ArchElementInterfaceCreate(BaseModel):
    version_id: str = Field(..., description="版本ID")
    element_id: str = Field(..., description="架构元素ID")
    interface_id: str = Field(..., description="接口ID")
    relation_type: str = Field(..., description=f"关系类型：{'|'.join(ArchElementInterfaceRelationType.values())}")
    description: Optional[str] = Field(None, description="关系说明")


class ArchElementInterfaceUpdate(BaseModel):
    description: Optional[str] = None


class ArchElementInterfaceInfo(BaseModel):
    id: str
    version_id: str
    element_id: str
    interface_id: str
    relation_type: str
    description: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
