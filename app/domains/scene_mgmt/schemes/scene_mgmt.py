from datetime import datetime
from typing import List,Optional
from pydantic import BaseModel,ConfigDict,Field
from app.domains.scene_mgmt.models.scene import SceneFlowType


class CreateScene(BaseModel):
    version_id:str=Field(...,description="版本ID")
    parent_id:Optional[str]=Field(None,description="父场景ID")
    name:str=Field(...,description="场景名称")
    actors:Optional[List[str]]=Field(None,description="Actor（场景相关操作人员）")
    description:Optional[str]=Field(None,description="描述")


class UpdateScene(BaseModel):
    parent_id:Optional[str]=None
    name:Optional[str]=None
    actors:Optional[List[str]]=None
    description:Optional[str]=None
    owner_id:Optional[str]=None


class SceneInfo(BaseModel):
    id:str
    version_id:str
    parent_id:Optional[str]=None
    name:str
    actors:Optional[List[str]]=None
    description:Optional[str]=None
    create_user_id:Optional[str]=None
    owner_id:Optional[str]=None
    created_at:datetime
    updated_at:Optional[datetime]=None

    model_config=ConfigDict(from_attributes=True)


class SceneTree(SceneInfo):
    children:List["SceneTree"]=Field(default_factory=list,description="子场景")


SceneTree.model_rebuild()


class CreateSceneFlow(BaseModel):
    version_id:str=Field(...,description="版本ID")
    flow_type:str=Field(...,description=f"流程类型：{'|'.join(SceneFlowType.values())}")
    name:str=Field(...,description="流程名称")
    content:Optional[str]=Field(None,description="流程内容（Markdown，包含流程图和说明）")
    element_ids:List[str]=Field(default_factory=list,description="关联架构元素ID列表（有序）")


class UpdateSceneFlow(BaseModel):
    flow_type:Optional[str]=None
    name:Optional[str]=None
    content:Optional[str]=None
    owner_id:Optional[str]=None
    element_ids:Optional[List[str]]=None


class SceneFlowInfo(BaseModel):
    id:str
    version_id:str
    scene_id:str
    flow_type:str
    name:str
    content:Optional[str]=None
    element_ids:List[str]=Field(default_factory=list,description="关联架构元素ID列表（有序）")
    create_user_id:Optional[str]=None
    owner_id:Optional[str]=None
    created_at:datetime
    updated_at:Optional[datetime]=None

    model_config=ConfigDict(from_attributes=True)

