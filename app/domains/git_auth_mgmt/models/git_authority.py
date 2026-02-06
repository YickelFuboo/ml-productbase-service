import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Index
from app.infrastructure.database.models_base import Base


class GitAuthority(Base):
    """不同类型 Git 仓的鉴权信息；支持按 version_id 配置，同一 provider 不同版本可配置不同鉴权"""
    __tablename__ = "git_authorities"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), nullable=False, index=True)
    version_id = Column(String(36), nullable=True, index=True, comment="版本ID，为空表示该 provider 的默认鉴权")
    provider = Column(String(20), nullable=False)
    access_token = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    __table_args__ = (Index("idx_user_provider_version", "user_id", "provider", "version_id"),)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "version_id": self.version_id,
            "provider": self.provider,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
