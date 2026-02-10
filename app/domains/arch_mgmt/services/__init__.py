from app.domains.arch_mgmt.services.architecture_service import ArchitectureService
from app.domains.arch_mgmt.services.interfaces_service import InterfacesService
from app.domains.arch_mgmt.services.build_service import BuildService
from app.domains.arch_mgmt.services.deployment_service import DeploymentService
from app.domains.arch_mgmt.services.decision_service import DecisionService
from app.domains.arch_mgmt.services.arch_doc_service import ArchDocService


class ArchMgmtService:
    """版本软件架构管理服务（统一入口，向后兼容）"""
    
    # 逻辑架构视图
    get_overview = ArchitectureService.get_overview
    list_overviews = ArchitectureService.list_overviews
    create_overview = ArchitectureService.create_overview
    update_overview = ArchitectureService.update_overview
    get_elements = ArchitectureService.get_elements
    get_element_by_id = ArchitectureService.get_element_by_id
    get_elements_tree = ArchitectureService.get_elements_tree
    create_element = ArchitectureService.create_element
    update_element = ArchitectureService.update_element
    delete_element = ArchitectureService.delete_element
    get_dependencies = ArchitectureService.get_dependencies
    get_dependency_by_id = ArchitectureService.get_dependency_by_id
    create_dependency = ArchitectureService.create_dependency
    update_dependency = ArchitectureService.update_dependency
    delete_dependency = ArchitectureService.delete_dependency

    # 架构决策
    list_decisions = DecisionService.list_decisions
    get_decision_by_id = DecisionService.get_decision_by_id
    create_decision = DecisionService.create_decision
    update_decision = DecisionService.update_decision
    delete_decision = DecisionService.delete_decision
    
    # 接口视图
    get_interface_by_id = InterfacesService.get_interface_by_id
    list_interfaces = InterfacesService.list_interfaces
    create_interface = InterfacesService.create_interface
    update_interface = InterfacesService.update_interface
    delete_interface = InterfacesService.delete_interface
    get_element_interface_by_id = InterfacesService.get_element_interface_by_id
    list_element_interfaces = InterfacesService.list_element_interfaces
    create_element_interface = InterfacesService.create_element_interface
    update_element_interface = InterfacesService.update_element_interface
    delete_element_interface = InterfacesService.delete_element_interface
    
    # 构建视图
    get_build_artifact_by_id = BuildService.get_build_artifact_by_id
    list_build_artifacts = BuildService.list_build_artifacts
    create_build_artifact = BuildService.create_build_artifact
    update_build_artifact = BuildService.update_build_artifact
    delete_build_artifact = BuildService.delete_build_artifact
    get_element_to_artifact_by_id = BuildService.get_element_to_artifact_by_id
    list_element_to_artifacts = BuildService.list_element_to_artifacts
    create_element_to_artifact = BuildService.create_element_to_artifact
    update_element_to_artifact = BuildService.update_element_to_artifact
    delete_element_to_artifact = BuildService.delete_element_to_artifact
    get_artifact_to_artifact_by_id = BuildService.get_artifact_to_artifact_by_id
    list_artifact_to_artifacts = BuildService.list_artifact_to_artifacts
    create_artifact_to_artifact = BuildService.create_artifact_to_artifact
    update_artifact_to_artifact = BuildService.update_artifact_to_artifact
    delete_artifact_to_artifact = BuildService.delete_artifact_to_artifact
    
    # 部署视图
    get_deployment_unit_by_id = DeploymentService.get_deployment_unit_by_id
    list_deployment_units = DeploymentService.list_deployment_units
    create_deployment_unit = DeploymentService.create_deployment_unit
    update_deployment_unit = DeploymentService.update_deployment_unit
    delete_deployment_unit = DeploymentService.delete_deployment_unit
    get_artifact_to_deployment_by_id = DeploymentService.get_artifact_to_deployment_by_id
    list_artifact_to_deployments = DeploymentService.list_artifact_to_deployments
    create_artifact_to_deployment = DeploymentService.create_artifact_to_deployment
    update_artifact_to_deployment = DeploymentService.update_artifact_to_deployment
    delete_artifact_to_deployment = DeploymentService.delete_artifact_to_deployment


__all__ = [
    "ArchMgmtService",
    "ArchitectureService",
    "InterfacesService",
    "BuildService",
    "DeploymentService",
    "DecisionService",
    "ArchDocService",
]
