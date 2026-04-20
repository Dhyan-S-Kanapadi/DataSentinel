 
from mcp.server.fastmcp import FastMCP
from agent import run_agent
import tools

# ── MCP Server Setup ───────────────────────────────────────────
mcp = FastMCP(
    name="OpenMetadata Workflow Agent",
    description="An MCP server that lets you manage OpenMetadata through natural language using Cerebras Llama and LangGraph"
)

# ── MCP Tools ──────────────────────────────────────────────────
@mcp.tool()
def ask_agent(question: str) -> str:
    """
    Ask the OpenMetadata AI agent anything about your data platform.
    Examples:
    - Which tables have no owners?
    - Show data quality failures
    - What is the lineage of orders table?
    - Trigger the Snowflake pipeline
    """
    return run_agent(question)

@mcp.tool()
def list_tables() -> str:
    """Get all tables from OpenMetadata"""
    import json
    return json.dumps(tools.get_tables())

@mcp.tool()
def list_unowned_tables() -> str:
    """Get all tables with no owner assigned"""
    import json
    return json.dumps(tools.get_unowned_tables())

@mcp.tool()
def list_undocumented_tables() -> str:
    """Get all tables with no description"""
    import json
    return json.dumps(tools.get_undocumented_tables())

@mcp.tool()
def list_pipelines() -> str:
    """Get all ingestion pipelines and their status"""
    import json
    return json.dumps(tools.get_pipelines())

@mcp.tool()
def list_quality_failures() -> str:
    """Get all data quality test failures"""
    import json
    return json.dumps(tools.get_quality_failures())

@mcp.tool()
def get_table_lineage(table_fqn: str) -> str:
    """
    Get lineage of a specific table.
    Args:
        table_fqn: Fully qualified name of the table (e.g. sample_data.ecommerce_db.shopify.orders)
    """
    import json
    return json.dumps(tools.get_lineage(table_fqn))

# ── Run Server ─────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run()