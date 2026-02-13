import uuid
from datetime import datetime
from enum import Enum
from sqlalchemy import Column,DateTime,ForeignKey,Index,String,UniqueConstraint
from sqlalchemy.orm import relationship
from app.infrastructure.database.models_base import Base


class KbCategory(str,Enum):
    BUSINESS="business"
    SOLUTION="solution"
    CODING="coding"
    TESTING="testing"
    CASE="case"

    @classmethod
    def values(cls):
        return [e.value for e in cls]

    @classmethod
    def display_name(cls,value:str)->str:
        m={
            "business":"业务知识",
            "solution":"方案知识",
            "coding":"编码知识",
            "testing":"测试知识",
            "case":"问题案例知识",
        }
        return m.get(value,value)


class VersionKbRecord(Base):
    """版本下知识库关联：仅管理版本与知识库的绑定及分类，知识库实体由 knowledgebase 服务维护"""
    __tablename__="version_kb"

    id=Column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()),comment="ID")
    version_id=Column(String(36),ForeignKey("version_record.id",ondelete="CASCADE"),nullable=False,index=True,comment="版本ID")
    kb_id=Column(String(36),nullable=False,index=True,comment="知识库ID（来自 knowledgebase 服务）")
    category=Column(String(32),nullable=False,index=True,comment="分类：business|solution|coding|testing|case")
    
    created_at=Column(DateTime,default=datetime.utcnow,nullable=False,comment="创建时间")
    updated_at=Column(DateTime,default=datetime.utcnow,onupdate=datetime.utcnow,nullable=True,comment="更新时间")

    __table_args__=(
        UniqueConstraint("version_id","kb_id",name="uq_version_kb_version_kb"),
        Index("idx_version_kb_version_category","version_id","category"),
    )

    def to_dict(self):
        return {
            "id":self.id,
            "version_id":self.version_id,
            "kb_id":self.kb_id,
            "category":self.category,
            "created_at":self.created_at.isoformat() if self.created_at else None,
            "updated_at":self.updated_at.isoformat() if self.updated_at else None,
        }
