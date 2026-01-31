"""
MCP Tools Registration
Register all tools that agents can access via MCP protocol
"""
from app.utils.mcp_server import mcp_server
from app.datasets import dataset_loader
from app.utils.llm_client import gemini_client
from app.utils.constants import RISK_AMPLIFIERS
import logging

logger = logging.getLogger(__name__)


def setup_mcp_tools():
    """Initialize and register all MCP tools"""
    
    logger.info("🔧 Setting up MCP Tools...")
    
    # ============ TOOL 1: Gemini LLM Call ============
    def gemini_call_tool(prompt: str, temperature: float = 0.3) -> str:
        """Call Gemini LLM"""
        return gemini_client.call_model(prompt, temperature)
    
    mcp_server.register_tool(
        name="gemini_call",
        func=gemini_call_tool,
        description="Call Gemini 3 Flash LLM for text generation and analysis",
        schema={
            "prompt": {"type": "string", "description": "The prompt text"},
            "temperature": {"type": "float", "description": "Temperature (0.0-1.0)", "default": 0.3}
        }
    )
    
    # ============ TOOL 2: Dataset Loader ============
    def load_dataset_tool(dataset_name: str):
        """Load any registered dataset"""
        loaders = {
            "rate_card": dataset_loader.load_rate_card,
            "risk_weights": dataset_loader.load_risk_weights,
            "complexity_multipliers": dataset_loader.load_complexity_multipliers,
            "city_state_multipliers": dataset_loader.load_city_multipliers,
            "location_library": dataset_loader.load_location_library,
        }
        
        if dataset_name not in loaders:
            raise ValueError(f"Unknown dataset: {dataset_name}. Available: {list(loaders.keys())}")
        
        return loaders[dataset_name]()
    
    mcp_server.register_tool(
        name="load_dataset",
        func=load_dataset_tool,
        description="Load any production dataset (rate cards, risk weights, multipliers, etc.)",
        schema={
            "dataset_name": {
                "type": "string",
                "description": "Name of dataset",
                "enum": [
                    "rate_card",
                    "risk_weights",
                    "complexity_multipliers",
                    "city_state_multipliers",
                    "location_library"
                ]
            }
        }
    )
    
    # ============ TOOL 3: Extract JSON from LLM ============
    def extract_json_tool(response_text: str) -> dict:
        """Extract JSON from LLM response"""
        return gemini_client.extract_json_from_response(response_text)
    
    mcp_server.register_tool(
        name="extract_json",
        func=extract_json_tool,
        description="Extract JSON object from LLM response text",
        schema={
            "response_text": {"type": "string", "description": "LLM response text"}
        }
    )
    
    # ============ TOOL 4: Risk Amplifiers Reference ============
    def get_risk_amplifiers_tool() -> dict:
        """Get risk amplifier combinations"""
        return {
            str(combo): multiplier
            for combo, multiplier in RISK_AMPLIFIERS.items()
        }
    
    mcp_server.register_tool(
        name="get_risk_amplifiers",
        func=get_risk_amplifiers_tool,
        description="Get all pre-defined risk amplifier combinations (e.g., Night+Water+Stunt = 1.4x)",
        schema={}
    )
    
    # ============ TOOL 5: JSON Schema Validator ============
    def validate_json_schema_tool(data: dict, required_fields: list) -> dict:
        """Validate JSON schema"""
        missing = [f for f in required_fields if f not in data]
        
        return {
            "valid": len(missing) == 0,
            "missing_fields": missing,
            "message": "Valid" if len(missing) == 0 else f"Missing: {missing}"
        }
    
    mcp_server.register_tool(
        name="validate_json_schema",
        func=validate_json_schema_tool,
        description="Validate that JSON has required fields",
        schema={
            "data": {"type": "object", "description": "JSON object to validate"},
            "required_fields": {"type": "array", "description": "Required field names"}
        }
    )
    
    logger.info("✅ MCP Tools Setup Complete!")
    logger.info(f"   Registered {len(mcp_server.tools)} tools")
    logger.info(f"   Available tools: {list(mcp_server.tools.keys())}")
