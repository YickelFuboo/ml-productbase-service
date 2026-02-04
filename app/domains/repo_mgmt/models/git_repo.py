import enum
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Enum
from sqlalchemy.orm import relationship


class ProcessingStatus(str, enum.Enum):
    """处理状态枚举"""
    INIT = "init"
    CLONING = "cloning"
    CHUNKING = "chunking"
    WIKI_GENERATING = "wiki_generating"
    COMPLETED = "completed"
    FAILED = "failed"


class RepoRecord:
    """仓库模型"""
    __tablename__ = "repo_records"

    id = Column(String, primary_key=True, index=True, comment="ID")
    create_user_id = Column(String, nullable=False, comment="创建用户ID")
    git_type = Column(String, default="git", comment="仓库类型")
    repo_url = Column(String, default="", comment="仓库URL")
    repo_organization = Column(String, nullable=False, default="", comment="组织")
    repo_name = Column(String, nullable=False, comment="仓库名称")
    repo_description = Column(Text, default="", comment="仓库介绍")
    repo_branch = Column(String, default="main", comment="分支")
    local_path = Column(String, nullable=True, comment="本地路径")
    version = Column(String, nullable=True, comment="版本")
    processing_status = Column(Enum(ProcessingStatus), default=ProcessingStatus.INIT, comment="处理状态")
    processing_progress = Column(Integer, default=0, comment="处理进度(0-100)")
    processing_message = Column(Text, comment="处理状态消息")
    processing_error = Column(Text, comment="处理错误信息")
    is_cloned = Column(Boolean, default=False, comment="是否克隆完成")
    is_chunked = Column(Boolean, default=False, comment="是否分块完成")
    is_wiki_generated = Column(Boolean, default=False, comment="是否生成wiki完成")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "create_user_id": self.create_user_id,
            "git_type": self.git_type,
            "repo_url": self.repo_url,
            "repo_organization": self.repo_organization,
            "repo_name": self.repo_name,
            "repo_description": self.repo_description,
            "repo_branch": self.repo_branch,
            "local_path": self.local_path,
            "version": self.version,
            "processing_status": self.processing_status.value if self.processing_status else None,
            "processing_progress": self.processing_progress,
            "processing_message": self.processing_message,
            "processing_error": self.processing_error,
            "is_cloned": self.is_cloned,
            "is_chunked": self.is_chunked,
            "is_wiki_generated": self.is_wiki_generated,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
