"""
逻辑架构视图 DTO：Overview、Element、Dependency、VersionSummary
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field
from app.domains.arch_mgmt.models.architecture import (
    ArchOverviewSectionKey,
    ArchElementType,
    ArchDependencyType,
)


class ArchOverviewCreate(BaseModel):
    version_id: str = Field(..., description="版本ID")
    section_key: str = Field("main", description="视点/章节键，标准键见 ArchOverviewSectionKey，也支持自定义")
    content: Optional[str] = Field(None, description="该节内容，支持 Markdown")


class ArchOverviewUpdate(BaseModel):
    content: Optional[str] = Field(None, description="该节内容")
    owner_id: Optional[str] = Field(None, description="数据Owner ID")


class ArchOverviewInfo(BaseModel):
    id: str
    version_id: str
    section_key: str
    content: Optional[str] = None
    create_user_id: Optional[str] = None
    owner_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ArchElementCreate(BaseModel):
    version_id: str = Field(..., description="版本ID")
    parent_id: Optional[str] = Field(None, description="父元素ID")
    element_type: str = Field(..., description="类型，见 ArchElementType.values()")
    name: str = Field(..., description="名称")
    code: Optional[str] = Field(None, description="编码/代号")
    code_repo_url: Optional[str] = Field(None, description="代码仓地址")
    code_repo_path: Optional[str] = Field(None, description="代码仓内相对路径")
    responsibility: Optional[str] = Field(None, description="职责/目的（Arc42 Responsibility）")
    definition: Optional[str] = Field(None, description="详细定义")
    tech_stack: Optional[str] = Field(None, description="技术栈")
    quality_attributes: Optional[str] = Field(None, description="质量属性，如可用性、性能")
    constraints: Optional[str] = Field(None, description="约束")
    specifications: Optional[str] = Field(None, description="规格")


class ArchElementUpdate(BaseModel):
    parent_id: Optional[str] = None
    element_type: Optional[str] = None
    name: Optional[str] = None
    owner_id: Optional[str] = None
    code: Optional[str] = None
    code_repo_url: Optional[str] = None
    code_repo_path: Optional[str] = None
    responsibility: Optional[str] = None
    definition: Optional[str] = None
    tech_stack: Optional[str] = None
    quality_attributes: Optional[str] = None
    constraints: Optional[str] = None
    specifications: Optional[str] = None


class ArchElementInfo(BaseModel):
    id: str
    version_id: str
    parent_id: Optional[str] = None
    element_type: str
    name: str
    create_user_id: Optional[str] = None
    owner_id: Optional[str] = None
    code: Optional[str] = None
    code_repo_url: Optional[str] = None
    code_repo_path: Optional[str] = None
    responsibility: Optional[str] = None
    definition: Optional[str] = None
    tech_stack: Optional[str] = None
    quality_attributes: Optional[str] = None
    constraints: Optional[str] = None
    specifications: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class ArchElementTree(ArchElementInfo):
    children: List["ArchElementTree"] = Field(default_factory=list, description="子元素")


ArchElementTree.model_rebuild()


class ArchDependencyCreate(BaseModel):
    version_id: str = Field(..., description="版本ID")
    source_element_id: str = Field(..., description="源架构元素ID（依赖的发起方）")
    target_element_id: str = Field(..., description="目标架构元素ID")
    dependency_type: Optional[str] = Field(None, description="关系类型：calls|reads_data_from|writes_data_to|depends_on")
    description: Optional[str] = Field(None, description="关系说明")


class ArchDependencyUpdate(BaseModel):
    dependency_type: Optional[str] = None
    description: Optional[str] = None
    owner_id: Optional[str] = None


class ArchDependencyInfo(BaseModel):
    id: str
    version_id: str
    source_element_id: str
    target_element_id: str
    dependency_type: Optional[str] = None
    description: Optional[str] = None
    create_user_id: Optional[str] = None
    owner_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ArchVersionSummary(BaseModel):
    """某版本的架构完整摘要（逻辑架构层）"""
    overviews: List[ArchOverviewInfo] = Field(default_factory=list, description="架构说明各节")
    elements: List[ArchElementInfo] = Field(default_factory=list, description="架构元素列表")
    elements_tree: Optional[List[ArchElementTree]] = Field(None, description="架构元素树")
    dependencies: List[ArchDependencyInfo] = Field(default_factory=list, description="依赖关系列表")
