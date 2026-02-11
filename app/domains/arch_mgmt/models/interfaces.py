"""
接口定义模型：ArchInterface（统一逻辑接口和物理接口）、ArchElementInterface
"""
import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Index, CheckConstraint
from sqlalchemy.orm import relationship, backref
from app.infrastructure.database.models_base import Base


class ArchInterfaceCategory(str, Enum):
    """接口类别"""
    LOGICAL = "logical"  # 逻辑接口（抽象接口定义）
    PHYSICAL = "physical"  # 物理接口（具体技术实现）

    @classmethod
    def values(cls):
        return [e.value for e in cls]


class ArchPhysicalInterfaceType(str, Enum):
    """物理接口类型（仅用于物理接口）"""
    REST_API = "rest_api"  # REST API
    GRPC = "grpc"  # gRPC
    MESSAGE_QUEUE = "message_queue"  # 消息队列
    FUNCTION_CALL = "function_call"  # 函数调用
    RPC = "rpc"  # RPC
    DATABASE = "database"  # 数据库连接
    FILE = "file"  # 文件
    OTHER = "other"  # 其他

    @classmethod
    def values(cls):
        return [e.value for e in cls]


class ArchElementInterfaceRelationType(str, Enum):
    """元素-接口关系类型"""
    PROVIDES = "provides"  # 提供
    USES = "uses"  # 使用

    @classmethod
    def values(cls):
        return [e.value for e in cls]


class ArchInterface(Base):
    """接口定义（统一逻辑接口和物理接口）"""
    __tablename__ = "arch_interface"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment="ID")
    version_id = Column(String(36), ForeignKey("version_record.id", ondelete="CASCADE"), nullable=False, index=True, comment="版本ID")

    interface_category = Column(String(16), nullable=False, index=True, comment=f"接口类别：{'|'.join(ArchInterfaceCategory.values())}")
    parent_id = Column(String(36), ForeignKey("arch_interface.id", ondelete="SET NULL"), nullable=True, index=True, comment="父接口ID（逻辑接口可分层定义，物理接口的父接口是最底层的逻辑接口）")

    name = Column(String(255), nullable=False, index=True, comment="接口名称")
    code = Column(String(64), nullable=True, index=True, comment="编码/代号")
    description = Column(Text, nullable=True, comment="说明")
    definition = Column(Text, nullable=True, comment="功能级定义说明")
    specification = Column(Text, nullable=True, comment="规格")
    constraints = Column(Text, nullable=True, comment="约束")

    interface_type = Column(String(32), nullable=True, index=True, comment=f"物理接口类型（仅物理接口使用）：{'|'.join(ArchPhysicalInterfaceType.values())}")
    tech_stack = Column(String(500), nullable=True, comment="技术栈（仅物理接口使用）")

    create_user_id = Column(String(36), nullable=True, index=True, comment="创建人ID")
    owner_id = Column(String(36), nullable=True, index=True, comment="数据Owner ID，默认创建人")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True, comment="更新时间")

    parent = relationship("ArchInterface", foreign_keys=[parent_id], remote_side="ArchInterface.id", backref=backref("children", passive_deletes=True))
    element_relations = relationship("ArchElementInterface", back_populates="interface", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_arch_interface_version_category", "version_id", "interface_category"),
        Index("idx_arch_interface_parent", "parent_id"),
        CheckConstraint("(interface_category = 'logical' AND interface_type IS NULL AND tech_stack IS NULL) OR interface_category = 'physical'", name="chk_interface_category_fields"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "version_id": self.version_id,
            "interface_category": self.interface_category,
            "parent_id": self.parent_id,
            "name": self.name,
            "code": self.code,
            "description": self.description,
            "definition": self.definition,
            "specification": self.specification,
            "constraints": self.constraints,
            "interface_type": self.interface_type,
            "tech_stack": self.tech_stack,
            "create_user_id": self.create_user_id,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class ArchElementInterface(Base):
    """架构元素与接口的关系（提供/使用）"""
    __tablename__ = "arch_element_interface"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), comment="ID")
    version_id = Column(String(36), ForeignKey("version_record.id", ondelete="CASCADE"), nullable=False, index=True, comment="版本ID")

    element_id = Column(String(36), ForeignKey("arch_element.id", ondelete="CASCADE"), nullable=False, index=True, comment="架构元素ID")
    interface_id = Column(String(36), ForeignKey("arch_interface.id", ondelete="CASCADE"), nullable=False, index=True, comment="接口ID")
    relation_type = Column(String(16), nullable=False, index=True, comment=f"关系类型：{'|'.join(ArchElementInterfaceRelationType.values())}")
    description = Column(Text, nullable=True, comment="关系说明")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True, comment="更新时间")

    element = relationship("ArchElement", foreign_keys=[element_id])
    interface = relationship("ArchInterface", foreign_keys=[interface_id], back_populates="element_relations")

    __table_args__ = (
        Index("idx_arch_elem_iface_version", "version_id"),
        Index("idx_arch_elem_iface_element", "element_id", "relation_type"),
        Index("idx_arch_elem_iface_interface", "interface_id", "relation_type"),
        Index("uq_arch_elem_iface_version_element_interface", "version_id", "element_id", "interface_id", "relation_type", unique=True),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "version_id": self.version_id,
            "element_id": self.element_id,
            "interface_id": self.interface_id,
            "relation_type": self.relation_type,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
