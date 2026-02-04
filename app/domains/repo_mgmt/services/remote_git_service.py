import os
import re
import asyncio
import logging
from typing import Tuple, Any
from sqlalchemy.ext.asyncio import AsyncSession


class RemoteGitService:
    """远程 Git 服务（URL 解析与本地操作）"""

    @staticmethod
    def get_git_provider(repo_url: str) -> str:
        """从 URL 解析 Git 提供商"""
        if not repo_url:
            return "git"
        url_lower = repo_url.lower()
        if "github.com" in url_lower:
            return "github"
        if "gitee.com" in url_lower:
            return "gitee"
        if "gitlab.com" in url_lower or "gitlab." in url_lower:
            return "gitlab"
        return "git"

    @staticmethod
    def get_git_url_info(repo_url: str) -> Tuple[str, str]:
        """从 URL 解析组织与仓库名 (organization, repo_name)"""
        if not repo_url:
            return "", ""
        url = repo_url.rstrip("/").rstrip(".git")
        patterns = [
            r"(?:https?://|git@)[^/:]+[:/]([^/]+)/([^/]+?)(?:\.git)?$",
            r"(?:https?://|git@)([^/:]+)[:/]([^/]+)/([^/]+?)(?:\.git)?$",
        ]
        for pattern in patterns:
            m = re.search(pattern, url)
            if m:
                groups = m.groups()
                if len(groups) == 2:
                    return groups[0], groups[1]
                if len(groups) == 3:
                    return groups[1], groups[2]
        if "/" in url:
            parts = url.replace("git@", "").replace("https://", "").replace("http://", "").split("/")
            if len(parts) >= 2:
                return parts[-2], parts[-1].replace(".git", "")
        return "", ""

    @staticmethod
    def checkout_branch(local_path: str, branch: str) -> bool:
        """切换本地仓库分支（需已安装 git）"""
        if not local_path or not os.path.isdir(os.path.join(local_path, ".git")):
            return False
        try:
            import subprocess
            r = subprocess.run(
                ["git", "checkout", branch],
                cwd=local_path,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return r.returncode == 0
        except Exception as e:
            logging.warning(f"checkout_branch failed: {e}")
            return False

    @staticmethod
    async def clone_repository(
        session: AsyncSession,
        repository_url: str,
        local_repo_path: str,
        branch: str,
        user_id: str,
    ) -> Any:
        """克隆远程仓库到本地（需已安装 git）"""
        try:
            import subprocess
            os.makedirs(os.path.dirname(local_repo_path) or ".", exist_ok=True)
            cmd = ["git", "clone", "--branch", branch, "--single-branch", "--depth", "1", repository_url, local_repo_path]
            proc = await asyncio.to_thread(subprocess.run, cmd, capture_output=True, text=True, timeout=600)
            if proc.returncode != 0:
                raise RuntimeError(proc.stderr or "clone failed")
            return type("CloneInfo", (), {"version": branch or "HEAD"})()
        except Exception as e:
            logging.error(f"clone_repository failed: {e}")
            raise
