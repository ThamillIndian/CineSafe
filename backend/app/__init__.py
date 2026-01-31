"""
ShootSafe AI Backend Application
Multi-Agent System with MCP + CrewAI
"""

__version__ = "2.0.0"  # Option C: MCP + CrewAI
__author__ = "ShootSafe AI Team"

# Initialize MCP on app startup
def init_mcp():
    """Initialize Model Context Protocol tools"""
    try:
        from app.utils.mcp_tools import setup_mcp_tools
        setup_mcp_tools()
        import logging
        logger = logging.getLogger(__name__)
        logger.info("✅ MCP initialized successfully")
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"⚠️ MCP initialization skipped: {e}")
        logger.warning("ℹ️ System will work without MCP tools (non-critical)")
        pass

# Initialize when module loads (non-blocking)
try:
    init_mcp()
except Exception as e:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"⚠️ MCP failed: {e}")
    pass
