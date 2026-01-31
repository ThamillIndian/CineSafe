"""
CrewAI Agent Definitions
Define specialized agents that collaborate on the ShootSafe AI pipeline
"""
from crewai import Agent
from app.utils.llm_client import gemini_client
from app.utils.mcp_server import mcp_server
import logging

logger = logging.getLogger(__name__)


def create_scene_extractor_agent():
    """Create Scene Extractor Agent using CrewAI"""
    return Agent(
        role="🎬 Scene Data Extractor",
        goal="Extract comprehensive scene data from film scripts with high accuracy",
        backstory="""
        You are an expert line producer with 25 years of film production experience.
        You excel at reading scripts and identifying every production detail that matters:
        locations, stunts, talent, timing, permits, and logistics needs.
        You understand the nuances of filmmaking and what makes a production feasible.
        """,
        tools=[
            {
                "name": "gemini_call",
                "description": "Call Gemini LLM for analysis",
                "execute": lambda **kw: mcp_server.call_tool("gemini_call", **kw)
            },
            {
                "name": "extract_json",
                "description": "Extract JSON from text",
                "execute": lambda **kw: mcp_server.call_tool("extract_json", **kw)
            }
        ],
        llm=gemini_client.client,
        memory=True,
        verbose=True,
        max_iter=3
    )


def create_risk_scorer_agent():
    """Create Risk Scorer Agent using CrewAI"""
    return Agent(
        role="⚠️ Risk Analysis Expert",
        goal="Calculate precise risk scores using industry data and identify dangerous combinations",
        backstory="""
        You are a safety coordinator with deep expertise in film production risks.
        You understand that risks don't add - they compound. Some combinations are exponentially worse.
        You know production data intimately and can spot patterns others miss.
        Your goal is to flag risks early before they become catastrophic.
        """,
        tools=[
            {
                "name": "load_dataset",
                "description": "Load production datasets",
                "execute": lambda **kw: mcp_server.call_tool("load_dataset", **kw)
            },
            {
                "name": "get_risk_amplifiers",
                "description": "Get risk amplifier combinations",
                "execute": lambda **kw: mcp_server.call_tool("get_risk_amplifiers", **kw)
            }
        ],
        llm=gemini_client.client,
        memory=True,
        verbose=True,
        max_iter=2
    )


def create_budget_estimator_agent():
    """Create Budget Estimator Agent using CrewAI"""
    return Agent(
        role="💰 Budget Planning Expert",
        goal="Estimate accurate budget ranges with confidence levels",
        backstory="""
        You are a production accountant with 20 years of budgeting experience.
        You know every cost factor that affects film production budgets.
        You're honest about uncertainty - you don't pretend to know things you don't.
        You provide ranges with clear drivers, not false precision.
        """,
        tools=[
            {
                "name": "load_dataset",
                "description": "Load production datasets",
                "execute": lambda **kw: mcp_server.call_tool("load_dataset", **kw)
            },
            {
                "name": "validate_json_schema",
                "description": "Validate extracted data",
                "execute": lambda **kw: mcp_server.call_tool("validate_json_schema", **kw)
            }
        ],
        llm=gemini_client.client,
        memory=True,
        verbose=True,
        max_iter=2
    )


def create_cross_scene_auditor_agent():
    """Create Cross-Scene Auditor Agent using CrewAI"""
    return Agent(
        role="🔍 Project Orchestrator",
        goal="Find cross-scene inefficiencies and project-level optimization opportunities",
        backstory="""
        You are a veteran line producer who has coordinated hundreds of film shoots.
        You see patterns others miss. You know that filming the right scenes in the right order
        can save weeks and hundreds of thousands of dollars.
        You understand the human factors: crew fatigue, talent availability, logistics chains.
        You're the voice of experience that prevents costly mistakes.
        """,
        tools=[
            {
                "name": "gemini_call",
                "description": "Call Gemini LLM for analysis",
                "execute": lambda **kw: mcp_server.call_tool("gemini_call", **kw)
            },
            {
                "name": "extract_json",
                "description": "Extract JSON from text",
                "execute": lambda **kw: mcp_server.call_tool("extract_json", **kw)
            }
        ],
        llm=gemini_client.client,
        memory=True,
        verbose=True,
        max_iter=2
    )


def create_mitigation_planner_agent():
    """Create Mitigation Planner Agent using CrewAI"""
    return Agent(
        role="🛡️ Mitigation Strategist",
        goal="Generate actionable mitigation plans for identified risks",
        backstory="""
        You are a safety expert who has prevented countless production disasters.
        You turn risks into actionable plans. You think deeply about second-order effects.
        When someone says "we have a risky scene," you don't just give generic advice.
        You provide specific, tested mitigation strategies backed by real production experience.
        """,
        tools=[
            {
                "name": "gemini_call",
                "description": "Call Gemini LLM for analysis",
                "execute": lambda **kw: mcp_server.call_tool("gemini_call", **kw)
            }
        ],
        llm=gemini_client.client,
        memory=True,
        verbose=True,
        max_iter=2
    )


# Initialize agents (lazy-loaded when needed)
_agents = {}


def get_scene_extractor_agent():
    """Get or create scene extractor agent"""
    if "extractor" not in _agents:
        _agents["extractor"] = create_scene_extractor_agent()
    return _agents["extractor"]


def get_risk_scorer_agent():
    """Get or create risk scorer agent"""
    if "risk_scorer" not in _agents:
        _agents["risk_scorer"] = create_risk_scorer_agent()
    return _agents["risk_scorer"]


def get_budget_estimator_agent():
    """Get or create budget estimator agent"""
    if "budget" not in _agents:
        _agents["budget"] = create_budget_estimator_agent()
    return _agents["budget"]


def get_cross_scene_auditor_agent():
    """Get or create cross-scene auditor agent"""
    if "auditor" not in _agents:
        _agents["auditor"] = create_cross_scene_auditor_agent()
    return _agents["auditor"]


def get_mitigation_planner_agent():
    """Get or create mitigation planner agent"""
    if "mitigation" not in _agents:
        _agents["mitigation"] = create_mitigation_planner_agent()
    return _agents["mitigation"]


def get_all_agents():
    """Get all agents (creates if needed)"""
    return [
        get_scene_extractor_agent(),
        get_risk_scorer_agent(),
        get_budget_estimator_agent(),
        get_cross_scene_auditor_agent(),
        get_mitigation_planner_agent(),
    ]
