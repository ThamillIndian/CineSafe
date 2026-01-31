"""
CrewAI Task Definitions
Define what each agent should do in the pipeline
"""
from crewai import Task
import logging

logger = logging.getLogger(__name__)


def create_extraction_task(agent):
    """Create scene extraction task"""
    return Task(
        description="""
        Extract comprehensive scene data from the film script.
        
        For each scene, identify and extract:
        1. Location (INT/EXT, specific place)
        2. Time of day (day, night, specific time)
        3. Stunt level (none, light, medium, heavy)
        4. Talent count and names if specified
        5. Extras count if specified
        6. Water complexity (none, simple, medium, complex)
        7. Vehicle types if any
        8. Animal presence if any
        9. Weather dependency
        10. Permit tier needed
        11. Special effects/pyrotechnics
        
        For each field, provide:
        - The value
        - Confidence score (0.0-1.0)
        - Evidence quote from script
        - Reasoning for the value
        
        Output as valid JSON array. Be strict: if information not in script, mark as UNKNOWN.
        """,
        agent=agent,
        expected_output="JSON array with detailed scene extractions",
        async_execution=False,
        human_input=False
    )


def create_risk_scoring_task(agent):
    """Create risk scoring task"""
    return Task(
        description="""
        Calculate risk scores for each scene using the production data.
        
        For each scene:
        1. Calculate base scores (0-30 per pillar):
           - Safety risk
           - Logistics risk
           - Schedule risk
           - Budget risk
           - Compliance risk
        
        2. Check for risk amplification:
           - Night + Water + Stunt = 1.4x amplification
           - Night + Crowd + Vehicle = 1.3x
           - Weather + Tight Schedule = 1.25x
           - Other dangerous combinations
        
        3. Apply amplification if detected
        
        4. Identify risk drivers (what's making this risky)
        
        5. Flag confidence level
        
        Output detailed risk scores for each scene with explanations.
        Remember: Risk compounds exponentially, not additively!
        """,
        agent=agent,
        expected_output="Risk scores for all scenes with amplifications flagged",
        async_execution=False,
        human_input=False
    )


def create_budget_estimation_task(agent):
    """Create budget estimation task"""
    return Task(
        description="""
        Estimate budget ranges for each scene using production datasets.
        
        For each scene:
        1. Load rate cards for the scale tier
        2. Load complexity multipliers
        3. Load city/region multipliers
        4. Calculate base department costs
        5. Apply multipliers based on extracted features
        6. Create min/likely/max ranges
        
        For confidence-based ranges:
        - High confidence fields (>0.9) = narrow range
        - Medium confidence fields (0.7-0.9) = medium range
        - Low confidence fields (<0.7) = wide range
        
        Identify volatility drivers (what's uncertain).
        
        Output detailed budget estimates with line items and confidence levels.
        Remember: Be honest about uncertainty - wide ranges beat false precision!
        """,
        agent=agent,
        expected_output="Budget estimates for all scenes with confidence ranges",
        async_execution=False,
        human_input=False
    )


def create_cross_scene_audit_task(agent):
    """Create cross-scene auditing task"""
    return Task(
        description="""
        Analyze entire project for cross-scene inefficiencies and optimizations.
        
        Look for:
        1. Location Chain Breaks
           - Same location shot on non-consecutive days
           - Could be consolidated to save travel time/cost
        
        2. Fatigue Clusters
           - Too many night shoots in a row
           - Too many heavy stunts close together
           - Could be spread out to reduce crew fatigue
        
        3. Talent Over-Utilization
           - Lead actor in too many scenes too close together
           - Should cluster their scenes to minimize total days
        
        4. Resource Bottlenecks
           - Multiple heavy scenes competing for same equipment
           - Should spread them out for efficiency
        
        5. Schedule Issues
           - Unrealistic timelines
           - Dependencies not accounted for
        
        For each inefficiency found:
        - Scene numbers affected
        - Current vs optimal arrangement
        - Estimated savings (time and money)
        - Confidence in recommendation
        
        Output actionable project-level insights with specific recommendations.
        This is your chance to show the producer YOUR EXPERIENCE in action!
        """,
        agent=agent,
        expected_output="Cross-scene insights with specific optimization recommendations",
        async_execution=False,
        human_input=False
    )


def create_mitigation_task(agent):
    """Create mitigation planning task"""
    return Task(
        description="""
        Generate mitigation plans for the highest-risk scenes and project-level risks.
        
        For each major risk:
        1. Understand the specific risk
        2. Develop concrete mitigation strategies
        3. Create actionable checklist
        4. Identify required resources
        5. Estimate timeline for mitigations
        6. Assign responsible party
        
        Types of mitigations:
        - Procedural (protocols, training, oversight)
        - Technical (equipment, tools, alternatives)
        - Staffing (specialists, coordinators, backup crew)
        - Schedule (more time, different timing, staging)
        
        Be specific and practical. These should be doable recommendations.
        Reference your experience: "In similar situations, here's what worked..."
        
        Output detailed mitigation plan with prioritized checklist.
        """,
        agent=agent,
        expected_output="Detailed mitigation plans with actionable checklists",
        async_execution=False,
        human_input=False
    )


# Task factory functions
def get_extraction_task(agent):
    """Get extraction task"""
    return create_extraction_task(agent)


def get_risk_scoring_task(agent):
    """Get risk scoring task"""
    return create_risk_scoring_task(agent)


def get_budget_estimation_task(agent):
    """Get budget estimation task"""
    return create_budget_estimation_task(agent)


def get_cross_scene_audit_task(agent):
    """Get cross-scene audit task"""
    return create_cross_scene_audit_task(agent)


def get_mitigation_task(agent):
    """Get mitigation task"""
    return create_mitigation_task(agent)
