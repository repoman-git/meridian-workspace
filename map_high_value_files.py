#!/usr/bin/env python3
"""
Map High-Value Files to Architecture Components - BASTARD-APPROVED-PLAN Day 2 Task 2.2

Maps high-value files (non-test, non-config Python files) to architecture components.
"""

import sys
from pathlib import Path
from collections import defaultdict
from datetime import datetime
import re

workspace_root = Path(__file__).parent
sys.path.insert(0, str(workspace_root))

from workspace.db import WorkspaceDB
from workspace.wms.architecture_validator import ArchitectureValidator
from workspace.db.models import ArchitectureComponent, UnregisteredFile


def infer_component_from_path(file_path: str, repo: str, components: dict) -> tuple:
    """
    Infer the component ID from file path using heuristics.
    
    Returns:
        (component_id, mapping_reason) or (None, None) if not found
    """
    file_path_lower = file_path.lower()
    path_parts = Path(file_path).parts
    
    # Workspace repo mappings
    if repo == "workspace":
        # Direct mappings for known WMS components
        if "context_manager" in file_path_lower:
            return components.get("WorkspaceContextManager"), "Core context management component"
        if "bastard_integration" in file_path_lower:
            return components.get("WorkspaceBastardIntegration"), "Bastard integration component"
        if "workflow_engine" in file_path_lower:
            return components.get("WorkspaceWorkflowEngine"), "Workflow management component"
        if "governance_engine" in file_path_lower:
            return components.get("WorkspaceGovernanceEngine"), "Governance enforcement component"
        if "architecture_validator" in file_path_lower:
            return components.get("WorkspaceArchitectureValidator"), "Architecture validation component"
        if file_path.startswith("wms/cli"):
            return components.get("WorkspaceContextManager"), "WMS CLI interface"
        if file_path.startswith("db/models"):
            return components.get("WorkspaceDBModels"), "Database models"
        if file_path.startswith("db/workspace_db") or file_path.startswith("db/__init__"):
            return components.get("WorkspaceDBManager"), "Database manager"
        if "generate_governance_context" in file_path_lower:
            return components.get("GovernanceContextGenerator"), "Governance context generation script"
        if "housekeeping" in file_path_lower:
            return components.get("WorkspaceHousekeeping"), "Housekeeping script"
        if "session" in file_path_lower and "start" in file_path_lower:
            return components.get("WorkspaceSessionStart"), "Session start script"
        if file_path.startswith("scripts/"):
            # Generic script component
            return components.get("WorkspaceHousekeeping"), "Workspace management script"
        if file_path.startswith("db/"):
            return components.get("WorkspaceDBManager"), "Database component"
        if file_path.startswith("wms/"):
            return components.get("WorkspaceContextManager"), "WMS component"
    
    # Meridian-core mappings
    elif repo == "meridian-core":
        if "orchestrator" in file_path_lower or "orchestration" in file_path_lower:
            if "ai_orchestrator" in file_path_lower or "orchestrator.py" in file_path_lower:
                return components.get("AIOrchestrator"), "Core orchestrator"
            if "autonomous" in file_path_lower:
                return components.get("AutonomousOrchestrator"), "Autonomous orchestrator"
            if "review" in file_path_lower:
                return components.get("ReviewOrchestrator"), "Review orchestrator"
            if "preflight" in file_path_lower:
                return components.get("PreflightManager"), "Preflight safety component"
            if "voting" in file_path_lower:
                return components.get("VotingManager"), "Voting consensus component"
            if "allocation" in file_path_lower or "agent_selector" in file_path_lower:
                return components.get("AgentSelector"), "Agent routing component"
            if "decision_memory" in file_path_lower:
                return components.get("AgentSelector"), "Decision memory component"
            if "tool_access" in file_path_lower:
                return components.get("AgentSelector"), "Tool access controller"
            if "convergence" in file_path_lower:
                return components.get("AIOrchestrator"), "Convergence logic"
            if "lmstudio" in file_path_lower:
                return components.get("ConnectorManager"), "LM Studio connector"
            return components.get("AIOrchestrator"), "Orchestration component"
        
        if "learning" in file_path_lower:
            if "learning_engine" in file_path_lower or "abstract" in file_path_lower:
                return components.get("LearningEngine"), "Learning engine base class"
            if "orchestration_learning" in file_path_lower:
                return components.get("OrchestrationLearningEngine"), "Orchestration learning implementation"
            if "cycle" in file_path_lower:
                return components.get("LearningCycleManager"), "Learning cycle manager"
            return components.get("LearningEngine"), "Learning component"
        
        if "credential" in file_path_lower or "secret" in file_path_lower:
            return components.get("CredentialStore"), "Credential management"
        
        if "connector" in file_path_lower or "anthropic" in file_path_lower or "openai" in file_path_lower:
            return components.get("ConnectorManager"), "AI connector component"
        
        if "task" in file_path_lower:
            if "executor" in file_path_lower:
                return components.get("TaskExecutor"), "Task execution component"
            if "pipeline" in file_path_lower:
                return components.get("TaskPipelineExecutor"), "Task pipeline component"
            return components.get("TaskExecutor"), "Task component"
        
        if "monitoring" in file_path_lower or "metrics" in file_path_lower or "health" in file_path_lower:
            return components.get("EffectivenessTracker"), "Monitoring and analytics"
        
        if "api" in file_path_lower or "server" in file_path_lower:
            return components.get("ProposalManager"), "API service module"
        
        if "db" in file_path_lower or "database" in file_path_lower or "models" in file_path_lower:
            return components.get("ProposalManager"), "Database models"
        
        if "extraction" in file_path_lower or "embedding" in file_path_lower or "vector" in file_path_lower:
            return components.get("ProposalManager"), "Data extraction component"
        
        if "evaluation" in file_path_lower or "evaluator" in file_path_lower:
            return components.get("EffectivenessTracker"), "Evaluation component"
    
    # Meridian-research mappings
    elif repo == "meridian-research":
        if "research_engine" in file_path_lower or "core" in file_path_lower and "research" in file_path_lower:
            return components.get("ResearchEngine"), "Core research engine"
        
        if "knowledge" in file_path_lower or "provider" in file_path_lower:
            return components.get("KnowledgeProvider"), "Knowledge provider component"
        
        if "skill" in file_path_lower:
            if "loader" in file_path_lower:
                return components.get("SkillLoader"), "Skill loader"
            if "adapter" in file_path_lower:
                return components.get("SkillAdapter"), "Skill adapter"
            return components.get("SkillLoader"), "Skill component"
        
        if "workflow" in file_path_lower:
            if "orchestrator" in file_path_lower:
                return components.get("WorkflowOrchestrator"), "Workflow orchestrator"
            return components.get("WorkflowEngine"), "Workflow engine"
        
        if "task" in file_path_lower:
            if "sync" in file_path_lower:
                return components.get("ResearchTaskSync"), "Task sync component"
            if "manager" in file_path_lower:
                return components.get("ResearchTaskManager"), "Task manager"
            return components.get("ResearchTaskManager"), "Task component"
        
        if "session" in file_path_lower or "store" in file_path_lower:
            return components.get("ResearchSessionStore"), "Session storage component"
        
        if "pattern" in file_path_lower or "detector" in file_path_lower:
            return components.get("ResearchPatternDetector"), "Pattern detection component"
        
        if "learning" in file_path_lower or "bridge" in file_path_lower:
            return components.get("ResearchLearningBridge"), "Learning bridge component"
        
        if "feedback" in file_path_lower or "collector" in file_path_lower:
            return components.get("ResearchFeedbackCollector"), "Feedback collection component"
        
        if "adapter" in file_path_lower and "core" in file_path_lower:
            return components.get("MeridianCoreAdapter"), "Core adapter"
        
        if "db" in file_path_lower or "database" in file_path_lower or "storage" in file_path_lower:
            return components.get("ResearchSessionStore"), "Database storage component"
        
        if "utils" in file_path_lower:
            # Utility files can map to multiple components, use ResearchEngine as default
            return components.get("ResearchEngine"), "Utility component"
        
        if "export" in file_path_lower or "formatter" in file_path_lower:
            return components.get("ResearchEngine"), "Export formatter component"
        
        if "template" in file_path_lower:
            return components.get("ResearchEngine"), "Template component"
    
    # Meridian-trading mappings
    elif repo == "meridian-trading":
        if "strategy" in file_path_lower:
            if "williams" in file_path_lower or "reversal" in file_path_lower:
                return components.get("WilliamsRReversalStrategy"), "Williams R reversal strategy"
            if "combined" in file_path_lower or "timing" in file_path_lower:
                return components.get("CombinedTimingStrategy"), "Combined timing strategy"
            if "cot" in file_path_lower and "tdom" in file_path_lower:
                return components.get("COTTdomStrategy"), "COT TDOM strategy"
            return components.get("WilliamsRReversalStrategy"), "Trading strategy"
        
        if "indicator" in file_path_lower:
            if "williams" in file_path_lower or "r" in file_path_lower:
                return components.get("WilliamsRIndicator"), "Williams R indicator"
            if "atr" in file_path_lower:
                return components.get("ATRIndicator"), "ATR indicator"
            if "cot" in file_path_lower:
                return components.get("COTIndicator"), "COT indicator"
            return components.get("WilliamsRIndicator"), "Technical indicator"
        
        if "filter" in file_path_lower:
            if "tdom" in file_path_lower:
                return components.get("TDOMFilter"), "TDOM filter"
            if "tdow" in file_path_lower:
                return components.get("TDOWFilter"), "TDOW filter"
            if "tdoy" in file_path_lower:
                return components.get("TDOYFilter"), "TDOY filter"
            return components.get("TDOMFilter"), "Time-based filter"
        
        if "scanner" in file_path_lower or "market" in file_path_lower:
            return components.get("MarketScanner"), "Market scanner"
        
        if "risk" in file_path_lower or "correlation" in file_path_lower:
            if "correlation" in file_path_lower:
                return components.get("CorrelationManager"), "Correlation manager"
            return components.get("RiskManager"), "Risk management component"
        
        if "credential" in file_path_lower or "security" in file_path_lower:
            return components.get("TradingCredentialManager"), "Credential manager"
        
        if "data" in file_path_lower:
            if "gold" in file_path_lower:
                return components.get("MarketScanner"), "Gold data pipeline"
            if "cot" in file_path_lower:
                return components.get("COTIndicator"), "COT data fetcher"
            return components.get("MarketScanner"), "Data component"
        
        if "validator" in file_path_lower or "validation" in file_path_lower:
            return components.get("TradingDataValidator"), "Data validation utility"
        
        if "orchestrator" in file_path_lower or "bridge" in file_path_lower:
            return components.get("OrchestratorBridge"), "Orchestrator bridge adapter"
        
        if "review" in file_path_lower:
            return components.get("RiskManager"), "Review component"
    
    return None, None


def map_high_value_files():
    """Map high-value files to architecture components."""
    print("\n" + "="*60)
    print("BASTARD-APPROVED-PLAN - Day 2 Task 2.2")
    print("Map High-Value Files to Architecture Components")
    print("="*60)
    
    db = WorkspaceDB(workspace_root=workspace_root)
    session = db._get_session()
    
    try:
        validator = ArchitectureValidator(session, workspace_root)
        
        # Get unregistered files
        unregistered = validator.get_unregistered_files()
        print(f"\nTotal unregistered files: {len(unregistered)}")
        
        # Filter to high-value files (non-test, non-config Python files)
        high_value_files = []
        test_files = []
        config_files = []
        
        for uf in unregistered:
            file_path_obj = Path(uf.file_path)
            # Skip test files
            if 'test' in file_path_obj.parts or file_path_obj.name.startswith('test_'):
                test_files.append(uf)
                continue
            # Skip config/docs
            if file_path_obj.suffix.lower() in {'.json', '.yaml', '.yml', '.toml', '.md'}:
                config_files.append(uf)
                continue
            # Only Python files for now
            if file_path_obj.suffix == '.py':
                high_value_files.append(uf)
        
        print(f"High-value files to map: {len(high_value_files)}")
        print(f"Test files (skipping): {len(test_files)}")
        print(f"Config/docs files (skipping): {len(config_files)}")
        
        # Get all components by repo
        components_by_repo = {}
        for repo in ["meridian-core", "meridian-research", "meridian-trading", "workspace"]:
            comps = session.query(ArchitectureComponent).filter_by(repo=repo).all()
            components_by_repo[repo] = {c.component_name: c.id for c in comps}
        
        # Map files to components
        print("\n" + "-"*60)
        print("Mapping files to components...")
        print("-"*60)
        
        mapped_count = 0
        failed_count = 0
        mapped_files = []
        failed_files = []
        
        for uf in high_value_files:
            components = components_by_repo.get(uf.repo, {})
            component_id, mapping_reason = infer_component_from_path(uf.file_path, uf.repo, components)
            
            if component_id:
                try:
                    mapping = validator.map_file_to_component(
                        file_path=uf.file_path,
                        component_id=component_id,
                        mapping_reason=mapping_reason or "Auto-mapped based on file path",
                        mapping_type="direct",
                        created_by="auto-mapping-script"
                    )
                    mapped_count += 1
                    mapped_files.append((uf.file_path, component_id))
                    print(f"✓ {uf.file_path} -> {component_id}")
                except Exception as e:
                    failed_count += 1
                    failed_files.append((uf.file_path, str(e)))
                    print(f"✗ {uf.file_path}: {e}")
            else:
                failed_count += 1
                failed_files.append((uf.file_path, "No matching component found"))
                print(f"✗ {uf.file_path}: No matching component found")
        
        # Summary
        print("\n" + "="*60)
        print("MAPPING SUMMARY")
        print("="*60)
        print(f"Total high-value files: {len(high_value_files)}")
        print(f"Successfully mapped: {mapped_count}")
        print(f"Failed to map: {failed_count}")
        
        if failed_files:
            print("\nFailed files:")
            for file_path, reason in failed_files[:10]:
                print(f"  • {file_path}: {reason}")
            if len(failed_files) > 10:
                print(f"  ... and {len(failed_files) - 10} more")
        
        # Update unregistered files status
        session.commit()
        
        return {
            "total": len(high_value_files),
            "mapped": mapped_count,
            "failed": failed_count,
            "mapped_files": mapped_files,
            "failed_files": failed_files
        }
        
    finally:
        session.close()


if __name__ == "__main__":
    try:
        results = map_high_value_files()
        print("\n" + "="*60)
        print("MAPPING COMPLETE")
        print("="*60)
        print(f"\n✅ Mapped {results['mapped']}/{results['total']} high-value files")
        if results['failed'] > 0:
            print(f"⚠️  {results['failed']} files could not be mapped")
        print("="*60)
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Mapping failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)



