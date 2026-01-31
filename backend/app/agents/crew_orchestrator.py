"""
CrewAI Orchestrator Agent
Main orchestrator using CrewAI for multi-agent coordination
"""
from crewai import Crew, Process
from app.agents.crew_agents import (
    get_scene_extractor_agent,
    get_risk_scorer_agent,
    get_budget_estimator_agent,
    get_cross_scene_auditor_agent,
    get_mitigation_planner_agent,
)
from app.agents.crew_tasks import (
    get_extraction_task,
    get_risk_scoring_task,
    get_budget_estimation_task,
    get_cross_scene_audit_task,
    get_mitigation_task,
)
import logging
from typing import Dict, Any
import json

logger = logging.getLogger(__name__)


class CrewOrchestratorAgent:
    """
    Main orchestrator using CrewAI for multi-agent coordination
    Replaces the manual orchestrator with intelligent hierarchical coordination
    """
    
    def __init__(self):
        """Initialize the crew orchestrator"""
        logger.info("🤖 Initializing CrewAI Orchestrator...")
        
        # Get all agents
        extractor = get_scene_extractor_agent()
        risk_scorer = get_risk_scorer_agent()
        budget_estimator = get_budget_estimator_agent()
        auditor = get_cross_scene_auditor_agent()
        mitigation_planner = get_mitigation_planner_agent()
        
        # Create tasks
        extraction_task = get_extraction_task(extractor)
        risk_task = get_risk_scoring_task(risk_scorer)
        budget_task = get_budget_estimation_task(budget_estimator)
        audit_task = get_cross_scene_audit_task(auditor)
        mitigation_task = get_mitigation_task(mitigation_planner)
        
        # Create crew with hierarchical process
        # Manager agent automatically created to coordinate
        self.crew = Crew(
            agents=[extractor, risk_scorer, budget_estimator, auditor, mitigation_planner],
            tasks=[extraction_task, risk_task, budget_task, audit_task, mitigation_task],
            process=Process.hierarchical,  # Manager coordinates all agents!
            verbose=True,  # Log everything
            memory=True,  # Agents share context/memory
        )
        
        logger.info("✅ CrewAI Orchestrator initialized successfully")
        logger.info("   Process: Hierarchical (Manager-coordinated)")
        logger.info("   Agents: 5")
        logger.info("   Tasks: 5")
        logger.info("   Memory: Shared across agents")
    
    def run_pipeline(self, project_id: str, script_text: str) -> Dict[str, Any]:
        """
        Run entire pipeline via CrewAI
        Agents collaborate intelligently with shared memory and hierarchical coordination
        
        Args:
            project_id: Project identifier
            script_text: Full script text to analyze
        
        Returns:
            Dictionary with results from all agents
        """
        
        logger.info(f"🚀 Starting pipeline for project: {project_id}")
        logger.info(f"   Script length: {len(script_text)} characters")
        
        try:
            # Kick off the crew
            # CrewAI Manager will orchestrate all agents
            result = self.crew.kickoff(inputs={
                "script": script_text,
                "project_id": project_id
            })
            
            logger.info("✅ Pipeline completed successfully")
            
            # Structure the output
            output = {
                "project_id": project_id,
                "status": "completed",
                "crew_output": str(result),  # Full crew output
                "memory_log": self._get_memory_log(),
                "call_history": self._get_call_history(),
            }
            
            return output
        
        except Exception as e:
            logger.error(f"❌ Pipeline failed: {e}")
            raise
    
    def _get_memory_log(self) -> Dict[str, Any]:
        """Get memory from all agents"""
        memory_log = {}
        
        # Get short-term memory (recent interactions)
        if hasattr(self.crew, 'memory'):
            try:
                memory_log["shared_memory"] = self.crew.memory.short_term_memory
            except:
                memory_log["shared_memory"] = "Not available"
        
        return memory_log
    
    def _get_call_history(self) -> list:
        """Get MCP tool call history"""
        from app.utils.mcp_server import mcp_server
        return mcp_server.get_call_history()


# Global orchestrator instance
crew_orchestrator = CrewOrchestratorAgent()


# Backwards compatibility wrapper
# (in case we need to use the old interface)
class OrchestratorAgent:
    """Backwards compatible wrapper for CrewOrchestratorAgent"""
    
    def __init__(self):
        self.crew_orchestrator = crew_orchestrator
    
    def run(self, project_id: str, script_text: str) -> Dict[str, Any]:
        """Run pipeline (legacy interface)"""
        return self.crew_orchestrator.run_pipeline(project_id, script_text)
