import os
import uuid
import shutil
import zipfile
import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, update
from fastapi import UploadFile
from app.config.settings import settings
from app.repo_mgmt.models.git_repo import RepoRecord, ProcessingStatus
from app.repo_mgmt.models.git_authority import GitAuthority
from app.repo_mgmt.schemes.repo_mgmt import CreateRepositoryFromUrl, UpdateRepository
from app.repo_mgmt.services.remote_git_service import RemoteGitService
from app.repo_mgmt.tasks.clone_task import clone_repository_task


class RepoMgmtService:
    """仓库管理服务"""

    @staticmethod
    def _get_base_storage_path() -> str:
        base = getattr(settings, "repo_storage_path", None)
        if base:
            return base
        return os.path.join(getattr(settings, "local_upload_dir", "./uploads"), "repos")

    @staticmethod
    async def create_repository_from_url(session: AsyncSession, user_id: str, create_data: CreateRepositoryFromUrl) -> RepoRecord:
        """通过Git URL创建仓库"""
        try:
            if not create_data.repo_url.strip() or not create_data.repo_url.startswith(("http://", "https://", "git@")):
                raise ValueError("无效的仓库URL")
            provider = RemoteGitService.get_git_provider(create_data.repo_url)
            repo_organization, repo_name = RemoteGitService.get_git_url_info(create_data.repo_url)
            existing_repo = await session.execute(
                select(RepoRecord).where(
                    RepoRecord.git_type == provider,
                    RepoRecord.repo_organization == repo_organization,
                    RepoRecord.repo_name == repo_name,
                    RepoRecord.create_user_id == user_id,
                )
            )
            if existing_repo.scalar_one_or_none():
                raise ValueError("仓库已存在")
            local_repo_path = os.path.join(RepoMgmtService._get_base_storage_path(), repo_organization, repo_name)
            repository = RepoRecord(
                id=str(uuid.uuid4()),
                create_user_id=user_id,
                git_type=provider,
                repo_url=create_data.repo_url,
                repo_organization=repo_organization,
                repo_name=repo_name,
                repo_description=create_data.description,
                repo_branch=create_data.branch,
                local_path=local_repo_path,
                processing_status=ProcessingStatus.INIT,
                processing_progress=0,
                processing_message="仓库已创建，等待开始克隆",
                created_at=datetime.utcnow(),
            )
            session.add(repository)
            await session.commit()
            await session.refresh(repository)
            try:
                if hasattr(clone_repository_task, "delay"):
                    clone_repository_task.delay(repository.id)
                else:
                    import threading
                    threading.Thread(target=clone_repository_task, args=(repository.id,), daemon=True).start()
            except Exception as e:
                logging.warning(f"clone_repository_task start failed: {e}")
            logging.info(f"Created repository: {repository.repo_name} by user {user_id}")
            return repository
        except Exception as e:
            logging.error(f"Failed to create repository: {e}")
            await session.rollback()
            raise

    @staticmethod
    async def create_repository_from_package(
        session: AsyncSession,
        user_id: str,
        name: str,
        description: str,
        file: UploadFile,
    ) -> RepoRecord:
        """通过上传压缩包创建仓库"""
        local_path = os.path.join(RepoMgmtService._get_base_storage_path(), "uploads", user_id, name)
        try:
            existing_repo = await session.execute(
                select(RepoRecord).where(RepoRecord.repo_name == name, RepoRecord.create_user_id == user_id)
            )
            if existing_repo.scalar_one_or_none():
                raise ValueError("仓库已存在")
            os.makedirs(local_path, exist_ok=True)
            try:
                file_path = os.path.join(local_path, file.filename or "archive.zip")
                content = await file.read()
                with open(file_path, "wb") as buffer:
                    buffer.write(content)
                if file_path.endswith(".zip"):
                    with zipfile.ZipFile(file_path, "r") as zip_ref:
                        zip_ref.extractall(local_path)
                elif file_path.endswith((".tar.gz", ".tar")):
                    import tarfile
                    with tarfile.open(file_path, "r:*") as tar_ref:
                        tar_ref.extractall(local_path)
                else:
                    raise ValueError("只支持zip、tar.gz、tar格式的压缩包")
                try:
                    os.remove(file_path)
                except OSError:
                    pass
            except Exception as e:
                if os.path.exists(local_path):
                    shutil.rmtree(local_path, ignore_errors=True)
                raise ValueError(f"处理上传文件失败: {str(e)}")
            repository = RepoRecord(
                id=str(uuid.uuid4()),
                create_user_id=user_id,
                git_type="upload",
                repo_url="",
                repo_organization="",
                repo_name=name,
                repo_description=description,
                repo_branch="",
                local_path=local_path,
                created_at=datetime.utcnow(),
            )
            session.add(repository)
            await session.commit()
            await session.refresh(repository)
            logging.info(f"Created repository from package: {repository.repo_name} by user {user_id}")
            return repository
        except Exception as e:
            if os.path.exists(local_path):
                shutil.rmtree(local_path, ignore_errors=True)
            logging.error(f"创建仓库失败: {e}")
            await session.rollback()
            raise

    @staticmethod
    async def create_repository_from_path(
        session: AsyncSession,
        user_id: str,
        name: str,
        description: str,
        local_repo_path: str,
    ) -> RepoRecord:
        """通过指定路径创建仓库"""
        try:
            if not local_repo_path:
                raise ValueError("路径不能为空")
            if not os.path.exists(local_repo_path):
                raise ValueError(f"路径不存在: {local_repo_path}")
            if not os.path.isdir(local_repo_path):
                raise ValueError(f"路径不是目录: {local_repo_path}")
            if not os.access(local_repo_path, os.R_OK):
                raise ValueError(f"路径无读取权限: {local_repo_path}")
            existing_repo = await session.execute(
                select(RepoRecord).where(RepoRecord.repo_name == name, RepoRecord.create_user_id == user_id)
            )
            if existing_repo.scalar_one_or_none():
                raise ValueError("仓库已存在")
            repository = RepoRecord(
                id=str(uuid.uuid4()),
                create_user_id=user_id,
                git_type="path",
                repo_url="",
                repo_organization="",
                repo_name=name,
                repo_description=description,
                repo_branch="main",
                local_path=local_repo_path,
                created_at=datetime.utcnow(),
            )
            session.add(repository)
            await session.commit()
            await session.refresh(repository)
            logging.info(f"Created repository from path: {repository.repo_name} by user {user_id}")
            return repository
        except Exception as e:
            logging.error(f"创建路径仓库失败: {e}")
            await session.rollback()
            raise

    @staticmethod
    async def get_repository_by_id(db: AsyncSession, repository_id: str) -> Optional[RepoRecord]:
        result = await db.execute(select(RepoRecord).where(RepoRecord.id == repository_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_repository_list(
        db: AsyncSession,
        user_id: str,
        page: int = 1,
        page_size: int = 10,
        keyword: Optional[str] = None,
    ) -> tuple[List[RepoRecord], int]:
        try:
            filtered = select(RepoRecord).where(RepoRecord.create_user_id == user_id)
            if keyword:
                filtered = filtered.where(
                    RepoRecord.repo_name.contains(keyword)
                    | RepoRecord.repo_description.contains(keyword)
                    | RepoRecord.repo_organization.contains(keyword)
                )
            from sqlalchemy import func
            total_result = await db.execute(select(func.count()).select_from(filtered.subquery()))
            total = total_result.scalar() or 0
            result = await db.execute(
                filtered.order_by(RepoRecord.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
            )
            return result.scalars().all(), total
        except Exception as e:
            logging.error(f"Failed to get repository list: {e}")
            raise

    @staticmethod
    async def update_repository(
        db: AsyncSession,
        repository_id: str,
        user_id: str,
        update_data: UpdateRepository,
    ) -> Optional[RepoRecord]:
        try:
            repository = await RepoMgmtService.get_repository_by_id(db, repository_id)
            if not repository:
                return None
            if repository.create_user_id != user_id:
                raise ValueError("无权限更新仓库")
            if update_data.description is not None:
                repository.repo_description = update_data.description
            if update_data.branch is not None:
                repository.repo_branch = update_data.branch
                try:
                    if repository.git_type not in ("upload",) and repository.local_path and os.path.isdir(os.path.join(repository.local_path, ".git")):
                        RemoteGitService.checkout_branch(repository.local_path, update_data.branch)
                except Exception as e:
                    logging.warning(f"checkout_branch: {e}")
            repository.updated_at = datetime.utcnow()
            await db.commit()
            await db.refresh(repository)
            return repository
        except Exception as e:
            logging.error(f"更新仓库失败: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def delete_repository(db: AsyncSession, repository_id: str, user_id: str) -> bool:
        try:
            repository = await RepoMgmtService.get_repository_by_id(db, repository_id)
            if not repository:
                return False
            if repository.create_user_id != user_id:
                raise ValueError("无权限删除仓库")
            if repository.local_path and os.path.exists(repository.local_path):
                shutil.rmtree(repository.local_path, ignore_errors=True)
            await db.execute(delete(RepoRecord).where(RepoRecord.id == repository_id))
            await db.commit()
            logging.info(f"Deleted repository: {repository.repo_name}")
            return True
        except Exception as e:
            logging.error(f"删除仓库失败: {e}")
            await db.rollback()
            raise

    @staticmethod
    async def update_repo_processing_status(
        session: AsyncSession,
        repo_id: str,
        status: ProcessingStatus,
        progress: Optional[int] = None,
        message: Optional[str] = None,
        error: Optional[str] = None,
    ) -> bool:
        try:
            values = {"processing_status": status, "updated_at": datetime.utcnow()}
            if progress is not None:
                values["processing_progress"] = progress
            if message is not None:
                values["processing_message"] = message
            if error is not None:
                values["processing_error"] = error
            result = await session.execute(update(RepoRecord).where(RepoRecord.id == repo_id).values(**values))
            await session.commit()
            return result.rowcount > 0
        except Exception as e:
            logging.error(f"更新仓库处理状态失败: {e}")
            return False
