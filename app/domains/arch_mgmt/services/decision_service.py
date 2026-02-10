import uuid
import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.arch_mgmt.models.decision import ArchDecision
from app.domains.arch_mgmt.schemes.decision import (
    ArchDecisionCreate,
    ArchDecisionUpdate,
)


class DecisionService:
    """架构决策服务（ADR - Architecture Decision Record）"""

    @staticmethod
    async def create_decision(session: AsyncSession, data: ArchDecisionCreate) -> ArchDecision:
        rec = ArchDecision(
            id=str(uuid.uuid4()),
            version_id=data.version_id,
            adr_number=data.adr_number,
            title=data.title,
            status=data.status or "accepted",
            context=data.context,
            decision=data.decision,
            consequences=data.consequences,
            alternatives_considered=data.alternatives_considered,
            supersedes_id=data.supersedes_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(rec)
        await session.commit()
        await session.refresh(rec)
        logging.info(f"创建架构决策 version_id={data.version_id} title={data.title}")
        return rec

    @staticmethod
    async def update_decision(
        session: AsyncSession, decision_id: str, data: ArchDecisionUpdate
    ) -> Optional[ArchDecision]:
        rec = await DecisionService.get_decision_by_id(session, decision_id)
        if not rec:
            return None
        update_data = data.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(rec, k, v)
        rec.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(rec)
        return rec

    @staticmethod
    async def delete_decision(session: AsyncSession, decision_id: str) -> bool:
        rec = await DecisionService.get_decision_by_id(session, decision_id)
        if not rec:
            return False
        await session.delete(rec)
        await session.commit()
        logging.info(f"删除架构决策 decision_id={decision_id}")
        return True

    @staticmethod
    async def list_decisions(session: AsyncSession, version_id: str) -> List[ArchDecision]:
        result = await session.execute(
            select(ArchDecision).where(ArchDecision.version_id == version_id).order_by(ArchDecision.adr_number, ArchDecision.created_at)
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_decision_by_id(session: AsyncSession, decision_id: str) -> Optional[ArchDecision]:
        result = await session.execute(select(ArchDecision).where(ArchDecision.id == decision_id))
        return result.scalar_one_or_none()
