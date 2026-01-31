"""
MCP (Model Context Protocol) Server
Provides standardized tool and resource access for all agents
"""
from typing import Any, Dict, Callable, Optional
import logging
import json

logger = logging.getLogger(__name__)


class MCPTool:
    """Represents a tool in MCP"""
    
    def __init__(self, name: str, description: str, func: Callable, schema: Dict[str, Any]):
        self.name = name
        self.description = description
        self.func = func
        self.schema = schema
    
    def execute(self, **kwargs) -> Any:
        """Execute the tool with validation"""
        return self.func(**kwargs)
    
    def to_dict(self) -> Dict:
        """Convert to dict for agent consumption"""
        return {
            "name": self.name,
            "description": self.description,
            "schema": self.schema
        }


class MCPResource:
    """Represents a resource in MCP"""
    
    def __init__(self, name: str, description: str, data: Any):
        self.name = name
        self.description = description
        self.data = data
    
    def get(self) -> Any:
        """Get resource data"""
        return self.data


class MCPServer:
    """
    Model Context Protocol Server
    Central hub for tools and resources accessible to all agents
    """
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
        self.resources: Dict[str, MCPResource] = {}
        self.call_history = []
        logger.info("MCP Server initialized")
    
    def register_tool(
        self,
        name: str,
        func: Callable,
        description: str = "",
        schema: Optional[Dict] = None
    ) -> None:
        """
        Register a tool with MCP
        
        Args:
            name: Tool name (unique identifier)
            func: Callable function
            description: Human-readable description
            schema: Parameter schema
        """
        if name in self.tools:
            logger.warning(f"Tool {name} already registered, overwriting")
        
        schema = schema or {}
        tool = MCPTool(name, description, func, schema)
        self.tools[name] = tool
        logger.info(f"✅ Registered tool: {name}")
    
    def register_resource(
        self,
        name: str,
        data: Any,
        description: str = ""
    ) -> None:
        """
        Register a resource with MCP
        
        Args:
            name: Resource name (unique identifier)
            data: Resource data
            description: Human-readable description
        """
        if name in self.resources:
            logger.warning(f"Resource {name} already registered, overwriting")
        
        resource = MCPResource(name, description, data)
        self.resources[name] = resource
        logger.info(f"✅ Registered resource: {name}")
    
    def call_tool(self, name: str, **kwargs) -> Any:
        """
        Call a registered tool
        
        Args:
            name: Tool name
            **kwargs: Tool parameters
        
        Returns:
            Tool result
        """
        if name not in self.tools:
            raise ValueError(f"Tool '{name}' not found. Available: {list(self.tools.keys())}")
        
        try:
            tool = self.tools[name]
            result = tool.execute(**kwargs)
            
            # Log the call
            self.call_history.append({
                "tool": name,
                "params": kwargs,
                "status": "success"
            })
            
            logger.debug(f"✅ Tool '{name}' executed successfully")
            return result
        
        except Exception as e:
            logger.error(f"❌ Tool '{name}' execution failed: {e}")
            self.call_history.append({
                "tool": name,
                "params": kwargs,
                "status": "error",
                "error": str(e)
            })
            raise
    
    def get_resource(self, name: str) -> Any:
        """
        Get a registered resource
        
        Args:
            name: Resource name
        
        Returns:
            Resource data
        """
        if name not in self.resources:
            raise ValueError(f"Resource '{name}' not found")
        
        resource = self.resources[name]
        logger.debug(f"✅ Resource '{name}' retrieved")
        return resource.get()
    
    def list_tools(self) -> Dict[str, Dict]:
        """Get list of all registered tools"""
        return {name: tool.to_dict() for name, tool in self.tools.items()}
    
    def list_resources(self) -> Dict[str, str]:
        """Get list of all registered resources"""
        return {name: res.description for name, res in self.resources.items()}
    
    def get_call_history(self) -> list:
        """Get history of tool calls"""
        return self.call_history
    
    def clear_history(self) -> None:
        """Clear call history"""
        self.call_history = []
        logger.info("Call history cleared")


# Global MCP Server instance
mcp_server = MCPServer()
