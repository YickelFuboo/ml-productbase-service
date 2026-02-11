import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column,DateTime,ForeignKey,Index,JSON,String,Text
from sqlalchemy.orm import backref,relationship
from app.infrastructure.database.models_base import Base


class SceneFlowType(str,Enum):
    NORMAL="normal"
    EXCEPTION="exception"

    @classmethod
    def values(cls):
        return [e.value for e in cls]


class SceneRecord(Base):
    __tablename__="scene_record"

    id=Column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()),comment="ID")
    version_id=Column(String(36),ForeignKey("version_record.id",ondelete="CASCADE"),nullable=False,index=True,comment="版本ID")
    parent_id=Column(String(36),ForeignKey("scene_record.id",ondelete="CASCADE"),nullable=True,index=True,comment="父场景ID")

    name=Column(String(255),nullable=False,index=True,comment="场景名称")
    actors=Column(JSON,nullable=True,comment="Actor（场景相关操作人员）")
    description=Column(Text,nullable=True,comment="描述")

    create_user_id=Column(String(36),nullable=True,index=True,comment="创建人ID")
    owner_id=Column(String(36),nullable=True,index=True,comment="数据Owner ID，默认创建人")

    created_at=Column(DateTime,default=datetime.utcnow,nullable=False,comment="创建时间")
    updated_at=Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=True,comment="更新时间")

    parent=relationship("SceneRecord",remote_side="SceneRecord.id",backref=backref("children",passive_deletes=True))
    flows=relationship("SceneFlowRecord",back_populates="scene",cascade="all, delete-orphan",passive_deletes=True)

    __table_args__=(
        Index("idx_scene_version_parent","version_id","parent_id"),
    )

    def to_dict(self):
        return {
            "id":self.id,
            "version_id":self.version_id,
            "parent_id":self.parent_id,
            "name":self.name,
            "actors":self.actors,
            "description":self.description,
            "create_user_id":self.create_user_id,
            "owner_id":self.owner_id,
            "created_at":self.created_at.isoformat() if self.created_at else None,
            "updated_at":self.updated_at.isoformat() if self.updated_at else None,
        }


class SceneFlowRecord(Base):
    __tablename__="scene_flow"

    id=Column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()),comment="ID")
    version_id=Column(String(36),ForeignKey("version_record.id",ondelete="CASCADE"),nullable=False,index=True,comment="版本ID")
    scene_id=Column(String(36),ForeignKey("scene_record.id",ondelete="CASCADE"),nullable=False,index=True,comment="场景ID")

    flow_type=Column(String(16),nullable=False,index=True,comment="流程类型：normal|exception")
    name=Column(String(255),nullable=False,index=True,comment="流程名称")
    content=Column(Text,nullable=True,comment="流程内容（Markdown，包含流程图和说明）")

    create_user_id=Column(String(36),nullable=True,index=True,comment="创建人ID")
    owner_id=Column(String(36),nullable=True,index=True,comment="数据Owner ID，默认创建人")

    created_at=Column(DateTime,default=datetime.utcnow,nullable=False,comment="创建时间")
    updated_at=Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=True,comment="更新时间")

    scene=relationship("SceneRecord",back_populates="flows")
    flow_elements=relationship("SceneFlowElementRecord",back_populates="flow",cascade="all, delete-orphan",passive_deletes=True)

    __table_args__=(
        Index("idx_scene_flow_version_type","version_id","flow_type"),
        Index("idx_scene_flow_scene_type","scene_id","flow_type"),
    )

    def to_dict(self):
        return {
            "id":self.id,
            "version_id":self.version_id,
            "scene_id":self.scene_id,
            "flow_type":self.flow_type,
            "name":self.name,
            "content":self.content,
            "create_user_id":self.create_user_id,
            "owner_id":self.owner_id,
            "created_at":self.created_at.isoformat() if self.created_at else None,
            "updated_at":self.updated_at.isoformat() if self.updated_at else None,
        }


class SceneFlowElementRecord(Base):
    __tablename__="scene_flow_element"

    id=Column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()),comment="ID")
    version_id=Column(String(36),ForeignKey("version_record.id",ondelete="CASCADE"),nullable=False,index=True,comment="版本ID")
    flow_id=Column(String(36),ForeignKey("scene_flow.id",ondelete="CASCADE"),nullable=False,index=True,comment="流程ID")
    element_id=Column(String(36),ForeignKey("arch_element.id",ondelete="CASCADE"),nullable=False,index=True,comment="关联架构元素ID")
    created_at=Column(DateTime,default=datetime.utcnow,nullable=False,comment="创建时间")

    flow=relationship("SceneFlowRecord",back_populates="flow_elements")

    __table_args__=(
        Index("uq_scene_flow_element_flow_element","flow_id","element_id",unique=True),
    )

    def to_dict(self):
        return {
            "id":self.id,
            "version_id":self.version_id,
            "flow_id":self.flow_id,
            "element_id":self.element_id,
            "created_at":self.created_at.isoformat() if self.created_at else None,
        }

