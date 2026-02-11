"""
架构决策模型：ArchDecision（ADR - Architecture Decision Record）
架构决策是跨视图的通用内容，适用于逻辑视图、构建视图、部署视图等所有视图。
"""
import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer, Index
from sqlalchemy.orm import relationship
from app.infrastructure.database.models_base import Base


class ArchDecisionStatus(str, Enum):
    """ADR 状态"""
    PROPOSED = "proposed"  # 提议中
    ACCEPTED = "accepted"  # 已接受
    REJECTED = "rejected"  # 已拒绝
    DEPRECATED = "deprecated"  # 已废弃
    SUPERSEDED = "superseded"  # 已被取代

    @classmethod
    def values(cls):
        return [e.value for e in cls]


class ArchDecision(Base):
    """架构决策记录（ADR）"""
    __tablename__ = "arch_decision"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment="ID")
    version_id = Column(String(36), ForeignKey("version_record.id", ondelete="CASCADE"), nullable=False, index=True, comment="版本ID")
    adr_number = Column(Integer, nullable=True, index=True, comment="ADR 序号")

    title = Column(String(500), nullable=False, comment="决策标题")
    status = Column(String(24), nullable=False, default="accepted", comment="状态：proposed|accepted|rejected|deprecated|superseded")
    context = Column(Text, nullable=True, comment="背景与影响因素")
    decision = Column(Text, nullable=True, comment="决策内容")
    consequences = Column(Text, nullable=True, comment="后果")
    alternatives_considered = Column(Text, nullable=True, comment="已考虑的备选方案")
    supersedes_id = Column(String(36), ForeignKey("arch_decision.id", ondelete="SET NULL"), nullable=True, index=True, comment="取代的 ADR ID")

    create_user_id = Column(String(36), nullable=True, index=True, comment="创建人ID")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True, comment="更新时间")

    supersedes = relationship("ArchDecision", remote_side="ArchDecision.id")

    __table_args__ = (
        Index("uq_arch_decision_version_adr_number", "version_id", "adr_number", unique=True),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "version_id": self.version_id,
            "adr_number": self.adr_number,
            "title": self.title,
            "status": self.status,
            "context": self.context,
            "decision": self.decision,
            "consequences": self.consequences,
            "alternatives_considered": self.alternatives_considered,
            "supersedes_id": self.supersedes_id,
            "create_user_id": self.create_user_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
