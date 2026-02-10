"""
架构决策 DTO：ArchDecision（ADR - Architecture Decision Record）
架构决策是跨视图的通用内容，适用于逻辑视图、构建视图、部署视图等所有视图。
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field
from app.domains.arch_mgmt.models.decision import ArchDecisionStatus


class ArchDecisionCreate(BaseModel):
    version_id: str = Field(..., description="版本ID")
    adr_number: Optional[int] = Field(None, description="ADR 序号")
    title: str = Field(..., description="决策标题")
    status: str = Field("accepted", description="状态，见 ArchDecisionStatus.values()")
    context: Optional[str] = Field(None, description="背景与影响因素")
    decision: Optional[str] = Field(None, description="决策内容")
    consequences: Optional[str] = Field(None, description="后果")
    alternatives_considered: Optional[str] = Field(None, description="已考虑的备选方案")
    supersedes_id: Optional[str] = Field(None, description="取代的 ADR ID")


class ArchDecisionUpdate(BaseModel):
    adr_number: Optional[int] = None
    title: Optional[str] = None
    status: Optional[str] = None
    context: Optional[str] = None
    decision: Optional[str] = None
    consequences: Optional[str] = None
    alternatives_considered: Optional[str] = None
    supersedes_id: Optional[str] = None


class ArchDecisionInfo(BaseModel):
    id: str
    version_id: str
    adr_number: Optional[int] = None
    title: str
    status: str
    context: Optional[str] = None
    decision: Optional[str] = None
    consequences: Optional[str] = None
    alternatives_considered: Optional[str] = None
    supersedes_id: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
