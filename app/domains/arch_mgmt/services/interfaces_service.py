import uuid
import logging
from datetime import datetime
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.arch_mgmt.models.interfaces import (
    ArchInterface,
    ArchElementInterface,
    ArchInterfaceCategory,
)
from app.domains.arch_mgmt.schemes.interfaces import (
    ArchInterfaceCreate,
    ArchInterfaceUpdate,
    ArchElementInterfaceCreate,
    ArchElementInterfaceUpdate,
)
from app.domains.arch_mgmt.services.architecture_service import ArchitectureService


class InterfacesService:
    """接口视图服务（Interface, ElementInterface）"""

    # ==================== Interface ====================

    @staticmethod
    async def create_interface(session: AsyncSession, data: ArchInterfaceCreate, user_id: str) -> Optional[ArchInterface]:
        if data.interface_category == ArchInterfaceCategory.PHYSICAL.value:
            if not data.interface_type:
                return None
            if data.parent_id:
                parent_iface = await InterfacesService.get_interface_by_id(session, data.parent_id)
                if not parent_iface or parent_iface.version_id != data.version_id or parent_iface.interface_category != ArchInterfaceCategory.LOGICAL.value:
                    return None
        elif data.interface_category == ArchInterfaceCategory.LOGICAL.value:
            if data.interface_type or data.tech_stack:
                return None
            if data.parent_id:
                parent_iface = await InterfacesService.get_interface_by_id(session, data.parent_id)
                if not parent_iface or parent_iface.version_id != data.version_id or parent_iface.interface_category != ArchInterfaceCategory.LOGICAL.value:
                    return None
        
        interface = ArchInterface(
            id=str(uuid.uuid4()),
            version_id=data.version_id,
            interface_category=data.interface_category,
            parent_id=data.parent_id if data.parent_id else None,
            name=data.name,
            code=data.code,
            description=data.description,
            definition=data.definition,
            specification=data.specification,
            constraints=data.constraints,
            interface_type=data.interface_type,
            tech_stack=data.tech_stack,
            create_user_id=user_id,
            owner_id=user_id,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        session.add(interface)
        await session.commit()
        await session.refresh(interface)
        logging.info(f"创建接口 version_id={data.version_id} category={data.interface_category} name={data.name}")
        return interface

    @staticmethod
    async def update_interface(
        session: AsyncSession, interface_id: str, data: ArchInterfaceUpdate
    ) -> Optional[ArchInterface]:
        interface = await InterfacesService.get_interface_by_id(session, interface_id)
        if not interface:
            return None
        update_data = data.model_dump(exclude_unset=True)
        if "parent_id" in update_data and update_data["parent_id"] == "":
            update_data["parent_id"] = None
        for k, v in update_data.items():
            setattr(interface, k, v)
        interface.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(interface)
        return interface

    @staticmethod
    async def delete_interface(session: AsyncSession, interface_id: str) -> bool:
        interface = await InterfacesService.get_interface_by_id(session, interface_id)
        if not interface:
            return False
        await session.delete(interface)
        await session.commit()
        logging.info(f"删除接口 interface_id={interface_id}")
        return True

    @staticmethod
    async def list_interfaces(
        session: AsyncSession, version_id: str, interface_category: Optional[str] = None, interface_type: Optional[str] = None, parent_id: Optional[str] = None
    ) -> List[ArchInterface]:
        q = select(ArchInterface).where(ArchInterface.version_id == version_id).order_by(ArchInterface.created_at)
        if interface_category:
            q = q.where(ArchInterface.interface_category == interface_category)
        if interface_type:
            q = q.where(ArchInterface.interface_type == interface_type)
        if parent_id:
            q = q.where(ArchInterface.parent_id == parent_id)
        result = await session.execute(q)
        return list(result.scalars().all())

    @staticmethod
    async def get_interface_by_id(session: AsyncSession, interface_id: str) -> Optional[ArchInterface]:
        result = await session.execute(select(ArchInterface).where(ArchInterface.id == interface_id))
        return result.scalar_one_or_none()

    # ==================== ElementInterface ====================

    @staticmethod
    async def create_element_interface(
        session: AsyncSession, data: ArchElementInterfaceCreate
    ) -> Optional[ArchElementInterface]:
        element = await ArchitectureService.get_element_by_id(session, data.element_id)
        if not element or element.version_id != data.version_id:
            return None
        interface = await InterfacesService.get_interface_by_id(session, data.interface_id)
        if not interface or interface.version_id != data.version_id:
            return None
        
        elem_iface = ArchElementInterface(
            id=str(uuid.uuid4()),
            version_id=data.version_id,
            element_id=data.element_id,
            interface_id=data.interface_id,
            relation_type=data.relation_type,
            description=data.description,
            created_at=datetime.utcnow(),
        )
        session.add(elem_iface)
        await session.commit()
        await session.refresh(elem_iface)
        logging.info(f"创建元素-接口关系 version_id={data.version_id} element_id={data.element_id} interface_id={data.interface_id} relation_type={data.relation_type}")
        return elem_iface

    @staticmethod
    async def update_element_interface(
        session: AsyncSession, elem_iface_id: str, data: ArchElementInterfaceUpdate
    ) -> Optional[ArchElementInterface]:
        elem_iface = await InterfacesService.get_element_interface_by_id(session, elem_iface_id)
        if not elem_iface:
            return None
        if data.description is not None:
            elem_iface.description = data.description
        elem_iface.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(elem_iface)
        return elem_iface

    @staticmethod
    async def delete_element_interface(session: AsyncSession, elem_iface_id: str) -> bool:
        elem_iface = await InterfacesService.get_element_interface_by_id(session, elem_iface_id)
        if not elem_iface:
            return False
        await session.delete(elem_iface)
        await session.commit()
        logging.info(f"删除元素-接口关系 elem_iface_id={elem_iface_id}")
        return True

    @staticmethod
    async def list_element_interfaces(
        session: AsyncSession, version_id: str, element_id: Optional[str] = None, interface_id: Optional[str] = None, relation_type: Optional[str] = None
    ) -> List[ArchElementInterface]:
        q = select(ArchElementInterface).where(ArchElementInterface.version_id == version_id).order_by(ArchElementInterface.created_at)
        if element_id:
            q = q.where(ArchElementInterface.element_id == element_id)
        if interface_id:
            q = q.where(ArchElementInterface.interface_id == interface_id)
        if relation_type:
            q = q.where(ArchElementInterface.relation_type == relation_type)
        result = await session.execute(q)
        return list(result.scalars().all())

    @staticmethod
    async def get_element_interface_by_id(session: AsyncSession, elem_iface_id: str) -> Optional[ArchElementInterface]:
        result = await session.execute(select(ArchElementInterface).where(ArchElementInterface.id == elem_iface_id))
        return result.scalar_one_or_none()
