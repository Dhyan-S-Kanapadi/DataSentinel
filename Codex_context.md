# Complete Project Context — OpenMetadata Workflow Agent

## Hackathon Details
- Event: Back to the Metadata — WeMakeDevs x OpenMetadata
- Track: T-01 — MCP Ecosystem & AI Agents
- Dates: April 17–26, 2026
- Deadline: April 26, 2026
- Team: AryaBit (3 members, Dhyan is team lead)
- OS: Windows
- Python: 3.14.3

## Sponsor Requirements
- Must use Cerebras API (LLM sponsor)
- Must use OpenMetadata (platform sponsor)
- Must use MCP (T-01 track requirement)

## Project Name
openmetadata-workflow-agent

## What We Are Building
A conversational AI agent that lets data teams manage their entire 
OpenMetadata platform through natural language. Instead of manually 
navigating the OpenMetadata UI, users just type questions and commands 
in plain English.

## Problem Statement
Data engineers waste hours manually navigating the OpenMetadata UI to 
trigger pipelines, check data quality, monitor governance, and find 
undocumented assets. Our agent eliminates this friction.

## Example Interactions
User: "Which tables have no owners?"
Agent: "Found 5 unowned tables: raw.events, raw.clicks..."

User: "Show data quality failures"
Agent: "2 failures — orders: row count dropped 34%..."

User: "Trigger the Snowflake pipeline"
Agent: "Pipeline triggered. 142 tables ingested successfully."

## Tech Stack
- LangGraph — agentic framework (ReAct loop)
- Cerebras Llama (llama3.1-8b) — AI brain
- OpenMetadata Sandbox API — data platform
- FastMCP — MCP server
- Streamlit — chat UI
- Python-dotenv — environment variables
- Requests — HTTP calls to OpenMetadata

## Architecture Flow
```
User types in Streamlit UI
        ↓
LangGraph agent receives message
        ↓
Cerebras Llama decides which tool to call
        ↓
Tool hits OpenMetadata API
        ↓
Data comes back
        ↓
Cerebras formats final answer
        ↓
Answer shown in Streamlit UI
```

## File Structure
```
openmetadata-workflow-agent/
├── config.py        
├── tools.py         
├── agent.py         
├── app.py           
├── server.py        
├── test.py          
├── requirements.txt 
├── .env             (NOT pushed to GitHub)
└── .gitignore       
```

## config.py (COMPLETE)
```python
import os
from dotenv import load_dotenv

load_dotenv()

CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
OPENMETADATA_URL = os.getenv("OPENMETADATA_URL")
```

## .env (COMPLETE)
```
CEREBRAS_API_KEY=your-cerebras-api-key-here
OPENMETADATA_URL=https://sandbox.open-metadata.org/api/v1
```

## .gitignore (COMPLETE)
```
.env
.venv/
__pycache__/
*.pyc
```

## requirements.txt (COMPLETE)
```
requests
python-dotenv
streamlit
mcp
langgraph
langchain-core
langchain-cerebras
```

## tools.py (COMPLETE)
```python
import requests
from config import OPENMETADATA_URL

HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def get_tables(limit=20):
    res = requests.get(
        f"{OPENMETADATA_URL}/tables",
        headers=HEADERS,
        params={"limit": limit, "include": "all"}
    )
    data = res.json().get("data", [])
    return [
        {
            "name": t.get("fullyQualifiedName"),
            "owner": t.get("owner", {}).get("name") if t.get("owner") else None,
            "description": t.get("description"),
            "tags": [tag["tagFQN"] for tag in t.get("tags", [])]
        }
        for t in data
    ]

def get_unowned_tables():
    tables = get_tables(50)
    return [t for t in tables if not t["owner"]]

def get_undocumented_tables():
    tables = get_tables(50)
    return [t for t in tables if not t["description"]]

def get_pipelines():
    res = requests.get(
        f"{OPENMETADATA_URL}/services/ingestionPipelines",
        headers=HEADERS,
        params={"limit": 20}
    )
    data = res.json().get("data", [])
    return [
        {
            "name": p.get("name"),
            "id": p.get("id"),
            "status": p.get("pipelineStatuses", {})
        }
        for p in data
    ]

def trigger_pipeline(pipeline_id: str):
    res = requests.post(
        f"{OPENMETADATA_URL}/services/ingestionPipelines/trigger/{pipeline_id}",
        headers=HEADERS
    )
    if res.status_code == 200:
        return "Pipeline triggered successfully"
    return f"Failed to trigger pipeline: {res.status_code}"

def get_quality_failures():
    res = requests.get(
        f"{OPENMETADATA_URL}/dataQuality/testCases",
        headers=HEADERS,
        params={"limit": 50, "testCaseStatus": "Failed"}
    )
    data = res.json().get("data", [])
    return [
        {
            "name": t.get("name"),
            "table": t.get("entityLink"),
            "status": t.get("testCaseResult", {}).get("testCaseStatus")
        }
        for t in data
    ]

def get_lineage(table_fqn: str):
    res = requests.get(
        f"{OPENMETADATA_URL}/lineage/table/name/{table_fqn}",
        headers=HEADERS,
        params={"upstreamDepth": 2, "downstreamDepth": 2}
    )
    return res.json()
```

## agent.py (COMPLETE — LangGraph Version)
```python
import json
from typing import Annotated
from langchain_cerebras import ChatCerebras
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
import tools
from config import CEREBRAS_API_KEY

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]

@tool
def get_tables_tool() -> str:
    """Get all tables from OpenMetadata platform"""
    result = tools.get_tables()
    return json.dumps(result)

@tool
def get_unowned_tables_tool() -> str:
    """Get all tables that have no owner assigned in OpenMetadata"""
    result = tools.get_unowned_tables()
    return json.dumps(result)

@tool
def get_undocumented_tables_tool() -> str:
    """Get all tables that have no description in OpenMetadata"""
    result = tools.get_undocumented_tables()
    return json.dumps(result)

@tool
def get_pipelines_tool() -> str:
    """Get all ingestion pipelines and their current status"""
    result = tools.get_pipelines()
    return json.dumps(result)

@tool
def trigger_pipeline_tool(pipeline_id: str) -> str:
    """Trigger an ingestion pipeline by its ID in OpenMetadata"""
    result = tools.trigger_pipeline(pipeline_id)
    return json.dumps(result)

@tool
def get_quality_failures_tool() -> str:
    """Get all data quality test failures from OpenMetadata"""
    result = tools.get_quality_failures()
    return json.dumps(result)

@tool
def get_lineage_tool(table_fqn: str) -> str:
    """Get lineage of a table by its fully qualified name from OpenMetadata"""
    result = tools.get_lineage(table_fqn)
    return json.dumps(result)

TOOLS = [
    get_tables_tool,
    get_unowned_tables_tool,
    get_undocumented_tables_tool,
    get_pipelines_tool,
    trigger_pipeline_tool,
    get_quality_failures_tool,
    get_lineage_tool
]

llm = ChatCerebras(
    api_key=CEREBRAS_API_KEY,
    model="llama3.1-8b"
)
llm_with_tools = llm.bind_tools(TOOLS)

SYSTEM_MESSAGE = SystemMessage(content=(
    "You are an intelligent OpenMetadata assistant. "
    "You help data teams manage their data platform by "
    "querying pipelines, data quality, lineage, and governance. "
    "Use the available tools to answer questions accurately. "
    "Always provide clear and concise answers in plain text."
))

tool_map = {t.name: t for t in TOOLS}

def call_llm(state: AgentState):
    messages = [SYSTEM_MESSAGE] + state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}

def call_tools(state: AgentState):
    last_message = state["messages"][-1]
    tool_messages = []
    for tool_call in last_message.tool_calls:
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        try:
            result = tool_map[tool_name].invoke(tool_args)
        except Exception as e:
            result = f"Error calling tool: {str(e)}"
        tool_messages.append(
            ToolMessage(
                content=str(result),
                tool_call_id=tool_call["id"]
            )
        )
    return {"messages": tool_messages}

def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "call_tools"
    return END

def build_agent():
    graph = StateGraph(AgentState)
    graph.add_node("call_llm", call_llm)
    graph.add_node("call_tools", call_tools)
    graph.set_entry_point("call_llm")
    graph.add_conditional_edges("call_llm", should_continue)
    graph.add_edge("call_tools", "call_llm")
    return graph.compile()

agent = build_agent()

def run_agent(user_message: str) -> str:
    result = agent.invoke({
        "messages": [HumanMessage(content=user_message)]
    })
    for message in reversed(result["messages"]):
        if isinstance(message, AIMessage):
            if hasattr(message, "tool_calls") and message.tool_calls:
                continue
            if isinstance(message.content, str) and message.content.strip():
                return message.content
            if isinstance(message.content, list):
                for block in message.content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        return block["text"]
    return "Sorry I could not get an answer. Please try again."
```

## app.py (COMPLETE — Streamlit UI)
```python
import streamlit as st
from agent import run_agent

st.set_page_config(
    page_title="OpenMetadata Workflow Agent",
    page_icon="🤖",
    layout="centered"
)

st.title("🤖 OpenMetadata Workflow Agent")
st.caption("Powered by Cerebras Llama + LangGraph + OpenMetadata")

st.markdown("**Try asking:**")
col1, col2 = st.columns(2)
with col1:
    if st.button("Which tables have no owners?"):
        st.session_state.suggested = "Which tables have no owners?"
    if st.button("Show data quality failures"):
        st.session_state.suggested = "Show data quality failures"
with col2:
    if st.button("Which tables are undocumented?"):
        st.session_state.suggested = "Which tables are undocumented?"
    if st.button("Show all pipelines"):
        st.session_state.suggested = "Show all pipelines"

st.divider()

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if "suggested" in st.session_state:
    prompt = st.session_state.suggested
    del st.session_state.suggested
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = run_agent(prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})

if prompt := st.chat_input("Ask anything about your data platform..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = run_agent(prompt)
        st.markdown(response)
    st.session_state.messages.append({"role": "assistant", "content": response})
```

## server.py (COMPLETE — MCP Server)
```python
from mcp.server.fastmcp import FastMCP
from agent import run_agent
import tools

mcp = FastMCP(
    name="OpenMetadata Workflow Agent",
    description="An MCP server that lets you manage OpenMetadata through natural language using Cerebras Llama and LangGraph"
)

@mcp.tool()
def ask_agent(question: str) -> str:
    """Ask the OpenMetadata AI agent anything about your data platform."""
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
    """Get lineage of a specific table."""
    import json
    return json.dumps(tools.get_lineage(table_fqn))

if __name__ == "__main__":
    mcp.run()
```

## Current Status
- ✅ GitHub repo created (openmetadata-workflow-agent)
- ✅ All files created and filled with code
- ✅ Virtual environment created (.venv)
- ✅ Dependencies installed (requests, python-dotenv, streamlit, mcp, langgraph, langchain-core, langchain-cerebras)
- ✅ .env created with Cerebras API key
- ✅ .gitignore created
- ✅ OpenMetadata sandbox accessible (https://sandbox.open-metadata.org)
- ✅ Streamlit UI running successfully
- ✅ Agent correctly identifies which tool to call
- ⬜ Agent final answer display bug being fixed
- ⬜ OpenMetadata connection confirmed with https
- ⬜ Full end to end test passing
- ⬜ Pushed to GitHub
- ⬜ Teammates added as collaborators
- ⬜ Demo video recorded
- ⬜ Submitted

## Current Bug
The agent correctly calls the right tool but returns the raw tool
call JSON instead of the final formatted answer. The fix is in the
run_agent() function in agent.py — need to correctly extract the
final AIMessage content after tool execution.

## How to Run
```bash
# Activate venv
.venv\Scripts\activate

# Run Streamlit UI
streamlit run app.py

# Run MCP server
python server.py

# Test OpenMetadata connection
python test.py
```

## Important Notes
- Always activate .venv before running anything
- .env file must never be pushed to GitHub
- OpenMetadata URL must use https not http
- Cerebras model name must be exactly "llama3.1-8b"
- Virtual environment is .venv folder in project root