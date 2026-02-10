"""
架构设计文档服务：根据当前架构元素生成完整的架构设计 Markdown 文档

文档名为「架构设计文档」，不作为标题。一级章节（#）为：
  # 总体设计
      ## 上下文与范围（section_key: context_and_scope）
      ## 解决方案策略（section_key: solution_strategy）
      ## 术语表（section_key: glossary）
      ## 架构决策（ADR）（可选）
  # 逻辑视图
      ## 逻辑架构：先表格罗列所有逻辑元素，再按父子关系以子章节呈现各元素（提供的接口、调用的接口等）
      ## 依赖关系：源元素 | 目标元素 | 类型 | 说明
  # 实现视图
      ## 编码模型：架构元素 | 代码仓 | 技术栈 表格
      ## 构建模型：构建产物、元素-产物映射、产物构建关系
  # 部署视图
      部署单元、产物-部署映射
"""
import re
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.domains.arch_mgmt.models.architecture import ArchOverviewSectionKey
from app.domains.arch_mgmt.services.architecture_service import ArchitectureService
from app.domains.arch_mgmt.services.interfaces_service import InterfacesService
from app.domains.arch_mgmt.services.build_service import BuildService
from app.domains.arch_mgmt.services.deployment_service import DeploymentService
from app.domains.arch_mgmt.services.decision_service import DecisionService
from app.domains.arch_mgmt.schemes.architecture import ArchElementTree


SECTION_KEY_TITLES = {
    "main": "概述",
    "context_and_scope": "上下文与范围",
    "solution_strategy": "解决方案策略",
    "glossary": "术语表",
}


def _section_title(section_key: str) -> str:
    return SECTION_KEY_TITLES.get(section_key, section_key.replace("_", " ").title())


def _downgrade_headings(content: str) -> str:
    """
    将用户内容中的 Markdown 标题降级，避免与文档结构冲突。
    
    文档结构使用到 ####（四级标题），用户内容中的标题统一降级 3 级：
    - #（一级）-> ####（四级）
    - ##（二级）-> #####（五级）
    - ###（三级）-> ######（六级）
    - ####（四级）-> ######（六级，Markdown 最多支持 6 级）
    
    Args:
        content: 用户输入的 Markdown 内容
    
    Returns:
        降级后的内容
    """
    if not content:
        return content
    
    def replace_heading(match):
        hashes = match.group(1)
        text = match.group(2)
        current_level = len(hashes)
        # 统一降级 3 级，但不超过 6 级（Markdown 最多支持 6 级标题）
        new_level = min(current_level + 3, 6)
        return f"{'#' * new_level} {text}"
    
    # 匹配 Markdown 标题格式：行首的 # 后跟空格和标题文本
    pattern = r'^(\#{1,6})\s+(.+)$'
    lines = content.split('\n')
    result_lines = []
    
    for line in lines:
        if re.match(pattern, line):
            result_lines.append(re.sub(pattern, replace_heading, line))
        else:
            result_lines.append(line)
    
    return '\n'.join(result_lines)


def _flatten_element_tree(nodes: List[ArchElementTree]) -> List[ArchElementTree]:
    """将元素树按先序遍历压平为列表，便于表格展示。"""
    out: List[ArchElementTree] = []
    for n in nodes:
        out.append(n)
        out.extend(_flatten_element_tree(n.children or []))
    return out


def _element_parent_map(nodes: List[ArchElementTree], parent_name: Optional[str] = None) -> dict:
    """返回 element_id -> 父元素名称（根节点无父）。"""
    m: dict = {}
    for n in nodes:
        if parent_name is not None:
            m[n.id] = parent_name
        for child in n.children or []:
            m[child.id] = n.name
            m.update(_element_parent_map([child], n.name))
    return m


def _render_logical_element_section(
    node: ArchElementTree,
    level: int,
    element_provides: dict,
    element_uses: dict,
    interface_names: dict,
) -> str:
    """按父子关系渲染单个架构元素章节：提供的接口、调用的接口、职责与定义等。"""
    heading = "#" * (level + 3)
    lines = [f"{heading} {node.name}\n"]
    lines.append(f"- **类型**: {node.element_type or '-'}")
    if node.code:
        lines.append(f"- **编码**: {node.code}")
    if node.responsibility:
        lines.append(f"- **职责**: {node.responsibility}")
    if node.definition:
        lines.append(f"- **定义**: {node.definition}")
    if node.tech_stack:
        lines.append(f"- **技术栈**: {node.tech_stack}")
    if node.code_repo_url:
        lines.append(f"- **代码仓**: {node.code_repo_url}")
    lines.append("")
    provides = element_provides.get(node.id) or []
    if provides:
        lines.append("**提供的接口**")
        for iface_id in provides:
            lines.append(f"- {interface_names.get(iface_id, iface_id)}")
        lines.append("")
    uses = element_uses.get(node.id) or []
    if uses:
        lines.append("**调用的接口**")
        for iface_id in uses:
            lines.append(f"- {interface_names.get(iface_id, iface_id)}")
        lines.append("")
    for child in node.children or []:
        lines.append(
            _render_logical_element_section(child, level + 1, element_provides, element_uses, interface_names)
        )
    return "\n".join(lines)


class ArchDocService:
    """将架构元素组装为完整架构设计 Markdown 文档"""

    @staticmethod
    async def build_arch_doc(session: AsyncSession, version_id: str) -> str:
        overviews = await ArchitectureService.list_overviews(session, version_id)
        elements_tree = await ArchitectureService.get_elements_tree(session, version_id)
        dependencies = await ArchitectureService.get_dependencies(session, version_id)
        decisions = await DecisionService.list_decisions(session, version_id)
        interfaces = await InterfacesService.list_interfaces(session, version_id)
        element_interfaces = await InterfacesService.list_element_interfaces(session, version_id)
        build_artifacts = await BuildService.list_build_artifacts(session, version_id)
        element_to_artifacts = await BuildService.list_element_to_artifacts(session, version_id)
        artifact_to_artifacts = await BuildService.list_artifact_to_artifacts(session, version_id)
        deployment_units = await DeploymentService.list_deployment_units(session, version_id)
        artifact_to_deployments = await DeploymentService.list_artifact_to_deployments(session, version_id)

        element_names = {}
        if elements_tree:
            def collect_names(nodes: List[ArchElementTree]) -> None:
                for n in nodes:
                    element_names[n.id] = n.name
                    if n.children:
                        collect_names(n.children)
            collect_names(elements_tree)

        interface_names = {i.id: i.name for i in interfaces}
        artifact_names = {a.id: a.name for a in build_artifacts}
        unit_names = {u.id: u.name for u in deployment_units}

        element_provides: dict = {}
        element_uses: dict = {}
        for ei in element_interfaces:
            eid = ei.element_id
            iid = ei.interface_id
            if ei.relation_type == "provides":
                element_provides.setdefault(eid, []).append(iid)
            else:
                element_uses.setdefault(eid, []).append(iid)

        parent_map: dict = {}
        if elements_tree:
            parent_map = _element_parent_map(elements_tree)

        parts = [f"架构设计文档\n\n版本 ID: `{version_id}`\n"]

        # ---------- 总体设计 ----------
        parts.append("\n---\n\n# 总体设计\n")
        overall_section_keys = ("context_and_scope", "solution_strategy", "glossary")
        overviews_for_overall = [o for o in overviews if o.section_key in overall_section_keys]
        if overviews_for_overall:
            ordered = sorted(
                overviews_for_overall,
                key=lambda o: (ArchOverviewSectionKey.order_for_key(o.section_key), o.section_key),
            )
            for o in ordered:
                title = _section_title(o.section_key)
                parts.append(f"## {title}\n\n")
                content = _downgrade_headings((o.content or "").strip())
                parts.append(content)
                parts.append("\n\n")
        if decisions:
            parts.append("## 架构决策（ADR）\n\n")
            for adr in decisions:
                num = f"ADR-{adr.adr_number}" if adr.adr_number is not None else adr.id[:8]
                parts.append(f"### {num} {adr.title}\n\n")
                parts.append(f"- **状态**: {adr.status}\n\n")
                if adr.context:
                    parts.append(f"**背景**\n\n{_downgrade_headings(adr.context)}\n\n")
                if adr.decision:
                    parts.append(f"**决策**\n\n{_downgrade_headings(adr.decision)}\n\n")
                if adr.consequences:
                    parts.append(f"**后果**\n\n{_downgrade_headings(adr.consequences)}\n\n")
                if adr.alternatives_considered:
                    parts.append(f"**备选方案**\n\n{_downgrade_headings(adr.alternatives_considered)}\n\n")
                parts.append("\n")

        # ---------- 逻辑视图 ----------
        parts.append("\n---\n\n# 逻辑视图\n")
        if elements_tree:
            parts.append("## 逻辑架构\n\n")
            flat_elements = _flatten_element_tree(elements_tree)
            parts.append("| 名称 | 类型 | 编码 | 父元素 | 职责 |\n")
            parts.append("|------|------|------|--------|------|\n")
            for n in flat_elements:
                parent = parent_map.get(n.id, "-")
                resp = (n.responsibility or "")[:80].replace("|", "\\|").replace("\n", " ") if n.responsibility else "-"
                parts.append(f"| {n.name} | {n.element_type or '-'} | {n.code or '-'} | {parent} | {resp} |\n")
            parts.append("\n")
            for root in elements_tree:
                parts.append(
                    _render_logical_element_section(root, 0, element_provides, element_uses, interface_names)
                )
                parts.append("\n")
        if dependencies:
            parts.append("### 依赖关系\n\n")
            parts.append("| 源元素 | 目标元素 | 类型 | 说明 |\n")
            parts.append("|--------|----------|------|------|\n")
            for d in dependencies:
                src = element_names.get(d.source_element_id, d.source_element_id)
                tgt = element_names.get(d.target_element_id, d.target_element_id)
                dtype = d.dependency_type or "-"
                desc = (d.description or "").replace("|", "\\|").replace("\n", " ")
                parts.append(f"| {src} | {tgt} | {dtype} | {desc} |\n")
            parts.append("\n")

        # ---------- 实现视图 ----------
        parts.append("\n---\n\n# 实现视图\n")
        if elements_tree:
            flat_elements = _flatten_element_tree(elements_tree)
            parts.append("## 编码模型\n\n")
            parts.append("| 架构元素 | 代码仓 | 技术栈 |\n")
            parts.append("|----------|--------|--------|\n")
            for n in flat_elements:
                repo = (n.code_repo_url or "-").replace("|", "\\|")
                tech = (n.tech_stack or "-").replace("|", "\\|").replace("\n", " ")
                parts.append(f"| {n.name} | {repo} | {tech} |\n")
            parts.append("\n")
        if build_artifacts or element_to_artifacts or artifact_to_artifacts:
            parts.append("## 构建模型\n\n")
            if build_artifacts:
                parts.append("**构建产物**\n\n")
                for a in build_artifacts:
                    parts.append(f"- **{a.name}** ({a.artifact_type})")
                    if a.description:
                        parts.append(f" — {a.description}")
                    parts.append("\n")
                    if a.build_command:
                        parts.append(f"  - 构建命令: `{a.build_command}`\n")
                    if a.build_environment:
                        parts.append(f"  - 构建环境: {a.build_environment}\n")
            if element_to_artifacts:
                parts.append("\n**元素-产物映射**\n\n")
                for ea in element_to_artifacts:
                    elem = element_names.get(ea.element_id, ea.element_id)
                    art = artifact_names.get(ea.build_artifact_id, ea.build_artifact_id)
                    parts.append(f"- {elem} → {art}\n")
            if artifact_to_artifacts:
                parts.append("\n**产物构建关系**\n\n")
                for aa in artifact_to_artifacts:
                    inp = artifact_names.get(aa.input_artifact_id, aa.input_artifact_id)
                    tgt = artifact_names.get(aa.target_artifact_id, aa.target_artifact_id)
                    parts.append(f"- {inp} → {tgt}\n")
            parts.append("\n")

        # ---------- 部署视图 ----------
        parts.append("\n---\n\n# 部署视图\n\n")
        if deployment_units:
            parts.append("**部署单元**\n\n")
            for u in deployment_units:
                parts.append(f"- **{u.name}** ({u.unit_type})")
                if u.description:
                    parts.append(f" — {u.description}")
                parts.append("\n")
        if artifact_to_deployments:
            parts.append("\n**产物-部署映射**\n\n")
            for ad in artifact_to_deployments:
                art = artifact_names.get(ad.build_artifact_id, ad.build_artifact_id)
                unit = unit_names.get(ad.deployment_unit_id, ad.deployment_unit_id)
                parts.append(f"- {art} → {unit}\n")

        return "".join(parts).strip()
