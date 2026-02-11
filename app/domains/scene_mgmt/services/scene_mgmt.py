import uuid
import logging
from datetime import datetime
from typing import List,Optional
from sqlalchemy import delete,or_,select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.arch_mgmt.models.architecture import ArchElement
from app.domains.scene_mgmt.models.scene import SceneFlowElementRecord,SceneFlowRecord,SceneFlowType,SceneRecord
from app.domains.scene_mgmt.schemes.scene_mgmt import CreateScene,CreateSceneFlow,SceneFlowInfo,SceneInfo,SceneTree,UpdateScene,UpdateSceneFlow


class SceneMgmtService:
    @staticmethod
    def _has_permission(rec,user_id:str)->bool:
        if getattr(rec,"owner_id",None)==user_id:
            return True
        return getattr(rec,"create_user_id",None)==user_id

    @staticmethod
    async def create_scene(db:AsyncSession,user_id:str,data:CreateScene)->SceneRecord:
        rec=SceneRecord(
            id=str(uuid.uuid4()),
            version_id=data.version_id,
            parent_id=data.parent_id if data.parent_id else None,
            name=data.name,
            actors=data.actors,
            description=data.description,
            create_user_id=user_id,
            owner_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(rec)
        await db.commit()
        await db.refresh(rec)
        logging.info(f"创建场景 version_id={data.version_id} name={data.name} user_id={user_id}")
        return rec

    @staticmethod
    async def get_scene_by_id(db:AsyncSession,scene_id:str)->Optional[SceneRecord]:
        result=await db.execute(select(SceneRecord).where(SceneRecord.id==scene_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def update_scene(db:AsyncSession,scene_id:str,user_id:str,data:UpdateScene)->Optional[SceneRecord]:
        rec=await SceneMgmtService.get_scene_by_id(db,scene_id)
        if not rec:
            return None
        if not SceneMgmtService._has_permission(rec,user_id):
            raise ValueError("无权限修改该场景")
        update_data=data.model_dump(exclude_unset=True)
        if "parent_id" in update_data and update_data["parent_id"]=="":
            update_data["parent_id"]=None
        for k,v in update_data.items():
            setattr(rec,k,v)
        rec.updated_at=datetime.utcnow()
        await db.commit()
        await db.refresh(rec)
        return rec

    @staticmethod
    async def delete_scene(db:AsyncSession,scene_id:str,user_id:str)->bool:
        rec=await SceneMgmtService.get_scene_by_id(db,scene_id)
        if not rec:
            return False
        if not SceneMgmtService._has_permission(rec,user_id):
            raise ValueError("无权限删除该场景")
        await db.execute(delete(SceneRecord).where(SceneRecord.id==scene_id))
        await db.commit()
        return True

    @staticmethod
    async def list_scenes(db:AsyncSession,version_id:str,user_id:str,parent_id:Optional[str]=None)->List[SceneRecord]:
        q=select(SceneRecord).where(
            SceneRecord.version_id==version_id,
            or_(SceneRecord.owner_id==user_id,SceneRecord.create_user_id==user_id),
        ).order_by(SceneRecord.created_at)
        if parent_id is not None:
            q=q.where(SceneRecord.parent_id==parent_id)
        result=await db.execute(q)
        return list(result.scalars().all())

    @staticmethod
    def _scene_to_tree(node:SceneRecord,all_scenes:List[SceneRecord])->SceneTree:
        children=[s for s in all_scenes if s.parent_id==node.id]
        sorted_children=sorted(children,key=lambda x:x.created_at or datetime.min)
        data=SceneInfo.model_validate(node).model_dump()
        data["children"]=[SceneMgmtService._scene_to_tree(c,all_scenes) for c in sorted_children]
        return SceneTree(**data)

    @staticmethod
    async def get_scenes_tree(db:AsyncSession,version_id:str,user_id:str)->List[SceneTree]:
        result=await db.execute(
            select(SceneRecord).where(
                SceneRecord.version_id==version_id,
                or_(SceneRecord.owner_id==user_id,SceneRecord.create_user_id==user_id),
            ).order_by(SceneRecord.created_at)
        )
        all_scenes=list(result.scalars().all())
        roots=[s for s in all_scenes if s.parent_id is None]
        return [SceneMgmtService._scene_to_tree(r,all_scenes) for r in sorted(roots,key=lambda x:x.created_at or datetime.min)]

    @staticmethod
    async def _validate_elements(db:AsyncSession,version_id:str,element_ids:List[str])->bool:
        if not element_ids:
            return True
        result=await db.execute(
            select(ArchElement.id).where(ArchElement.version_id==version_id,ArchElement.id.in_(element_ids))
        )
        found=set(result.scalars().all())
        return len(found)==len(set(element_ids))

    @staticmethod
    async def create_flow(db:AsyncSession,scene_id:str,user_id:str,data:CreateSceneFlow)->Optional[SceneFlowRecord]:
        scene=await SceneMgmtService.get_scene_by_id(db,scene_id)
        if not scene or scene.version_id!=data.version_id:
            return None
        if data.flow_type not in SceneFlowType.values():
            raise ValueError(f"flow_type 不合法，合法值: {SceneFlowType.values()}")
        ok=await SceneMgmtService._validate_elements(db,data.version_id,data.element_ids)
        if not ok:
            return None
        rec=SceneFlowRecord(
            id=str(uuid.uuid4()),
            version_id=data.version_id,
            scene_id=scene_id,
            flow_type=data.flow_type,
            name=data.name,
            content=data.content,
            create_user_id=user_id,
            owner_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(rec)
        await db.flush()
        for eid in data.element_ids:
            db.add(SceneFlowElementRecord(
                id=str(uuid.uuid4()),
                version_id=data.version_id,
                flow_id=rec.id,
                element_id=eid,
                created_at=datetime.utcnow(),
            ))
        await db.commit()
        await db.refresh(rec)
        return rec

    @staticmethod
    async def get_flow_by_id(db:AsyncSession,flow_id:str)->Optional[SceneFlowRecord]:
        result=await db.execute(select(SceneFlowRecord).where(SceneFlowRecord.id==flow_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def list_flow_element_ids(db:AsyncSession,flow_id:str)->List[str]:
        result=await db.execute(
            select(SceneFlowElementRecord.element_id)
            .where(SceneFlowElementRecord.flow_id==flow_id)
            .order_by(SceneFlowElementRecord.created_at)
        )
        return list(result.scalars().all())

    @staticmethod
    async def to_flow_info(db:AsyncSession,rec:SceneFlowRecord)->SceneFlowInfo:
        element_ids=await SceneMgmtService.list_flow_element_ids(db,rec.id)
        data=SceneFlowInfo.model_validate(rec).model_dump()
        data["element_ids"]=element_ids
        return SceneFlowInfo(**data)

    @staticmethod
    async def update_flow(db:AsyncSession,flow_id:str,user_id:str,data:UpdateSceneFlow)->Optional[SceneFlowRecord]:
        rec=await SceneMgmtService.get_flow_by_id(db,flow_id)
        if not rec:
            return None
        if not SceneMgmtService._has_permission(rec,user_id):
            raise ValueError("无权限修改该流程")
        if data.flow_type is not None and data.flow_type not in SceneFlowType.values():
            raise ValueError(f"flow_type 不合法，合法值: {SceneFlowType.values()}")
        update_data=data.model_dump(exclude_unset=True,exclude={"element_ids"})
        for k,v in update_data.items():
            setattr(rec,k,v)
        if data.element_ids is not None:
            ok=await SceneMgmtService._validate_elements(db,rec.version_id,data.element_ids)
            if not ok:
                return None
            await db.execute(delete(SceneFlowElementRecord).where(SceneFlowElementRecord.flow_id==flow_id))
            for eid in data.element_ids:
                db.add(SceneFlowElementRecord(
                    id=str(uuid.uuid4()),
                    version_id=rec.version_id,
                    flow_id=flow_id,
                    element_id=eid,
                    created_at=datetime.utcnow(),
                ))
        rec.updated_at=datetime.utcnow()
        await db.commit()
        await db.refresh(rec)
        return rec

    @staticmethod
    async def delete_flow(db:AsyncSession,flow_id:str,user_id:str)->bool:
        rec=await SceneMgmtService.get_flow_by_id(db,flow_id)
        if not rec:
            return False
        if not SceneMgmtService._has_permission(rec,user_id):
            raise ValueError("无权限删除该流程")
        await db.execute(delete(SceneFlowRecord).where(SceneFlowRecord.id==flow_id))
        await db.commit()
        return True

    @staticmethod
    async def list_flows(db:AsyncSession,scene_id:str,user_id:str,flow_type:Optional[str]=None)->List[SceneFlowRecord]:
        q=select(SceneFlowRecord).where(
            SceneFlowRecord.scene_id==scene_id,
            or_(SceneFlowRecord.owner_id==user_id,SceneFlowRecord.create_user_id==user_id),
        ).order_by(SceneFlowRecord.created_at)
        if flow_type:
            q=q.where(SceneFlowRecord.flow_type==flow_type)
        result=await db.execute(q)
        return list(result.scalars().all())

