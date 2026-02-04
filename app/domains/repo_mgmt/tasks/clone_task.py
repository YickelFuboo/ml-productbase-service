import asyncio
import logging
from datetime import datetime
from sqlalchemy import select, update
from app.infrastructure.database import get_db
from app.domains.repo_mgmt.models.git_repo import RepoRecord, ProcessingStatus
from app.domains.repo_mgmt.services.remote_git_service import RemoteGitService


def clone_repository_task(repo_id: str):
    """同步入口：异步克隆仓库任务（可由 Celery 等调用）"""
    asyncio.run(_clone_repository_async(repo_id))


async def _clone_repository_async(repo_id: str):
    """异步克隆仓库"""
    async for session in get_db():
        try:
            result = await session.execute(select(RepoRecord).where(RepoRecord.id == repo_id))
            repo_record = result.scalar_one_or_none()
            if not repo_record:
                raise RuntimeError(f"仓库 {repo_id} 不存在")
            await session.execute(
                update(RepoRecord)
                .where(RepoRecord.id == repo_id)
                .values(
                    processing_status=ProcessingStatus.CLONING,
                    processing_progress=10,
                    processing_message="开始克隆仓库",
                    updated_at=datetime.utcnow(),
                )
            )
            await session.commit()
            try:
                git_info = await RemoteGitService.clone_repository(
                    session=session,
                    repository_url=repo_record.repo_url,
                    local_repo_path=repo_record.local_path or "",
                    branch=repo_record.repo_branch or "main",
                    user_id=repo_record.create_user_id,
                )
                await session.execute(
                    update(RepoRecord)
                    .where(RepoRecord.id == repo_id)
                    .values(
                        version=git_info.version if hasattr(git_info, "version") else repo_record.repo_branch,
                        processing_status=ProcessingStatus.COMPLETED,
                        processing_progress=100,
                        processing_message="仓库克隆完成",
                        is_cloned=True,
                        updated_at=datetime.utcnow(),
                    )
                )
                await session.commit()
                logging.info(f"仓库 {repo_record.repo_name} 克隆完成")
            except Exception as e:
                await session.execute(
                    update(RepoRecord)
                    .where(RepoRecord.id == repo_id)
                    .values(
                        processing_status=ProcessingStatus.FAILED,
                        processing_progress=0,
                        processing_message="克隆失败",
                        processing_error=str(e),
                        updated_at=datetime.utcnow(),
                    )
                )
                await session.commit()
                logging.error(f"仓库 {repo_id} 克隆失败: {e}")
                raise
        except Exception as e:
            logging.error(f"clone_repository_async error: {e}")
            raise
        break
