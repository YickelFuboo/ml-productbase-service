from datetime import datetime
from typing import List
from pydantic import BaseModel,ConfigDict,Field,computed_field
from app.domains.kb_mgmt.models.knowledge_base import KbCategory


class KbCategoryEnum(BaseModel):
    value:str=Field(...,description="分类编码")
    display_name:str=Field(...,description="分类显示名")


class CreateVersionKb(BaseModel):
    kb_id:str=Field(...,description="知识库ID（来自 knowledgebase 服务）")
    category:str=Field(...,description=f"分类：{'|'.join(KbCategory.values())}")


class UpdateVersionKb(BaseModel):
    category:str=Field(...,description=f"分类：{'|'.join(KbCategory.values())}")


class VersionKbInfo(BaseModel):
    id:str
    version_id:str
    kb_id:str
    category:str
    created_at:datetime
    updated_at:datetime|None=None

    model_config=ConfigDict(from_attributes=True)

    @computed_field
    @property
    def category_display(self)->str:
        return KbCategory.display_name(self.category)


class VersionKbCategoryGroup(BaseModel):
    category:str=Field(...,description="分类编码")
    category_display:str=Field(...,description="分类显示名")
    items:List[VersionKbInfo]=Field(default_factory=list,description="该分类下的知识库列表")


class VersionKbListResponse(BaseModel):
    version_id:str
    by_category:List[VersionKbCategoryGroup]=Field(default_factory=list,description="按分类分组的知识库列表")
