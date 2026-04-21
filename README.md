🤖 OpenMetadata Workflow Agent
> A conversational AI agent that lets data teams manage their entire OpenMetadata platform through natural language — powered by \*\*Cerebras Llama\*\* and \*\*LangGraph\*\*.
---
🎯 Problem Statement
Data engineers waste hours manually navigating the OpenMetadata UI to trigger pipelines, check data quality, monitor governance, and find undocumented assets. Our agent eliminates this friction by letting teams do everything through plain English commands.
---
💡 Solution
An intelligent agentic system that:
Understands natural language queries
Decides which OpenMetadata API to call (agentic behavior)
Fetches real data from OpenMetadata
Returns clear, human-readable answers
Instead of navigating the UI:
```
User: "Which tables have no owners?"
Agent: "Found 5 unowned tables: raw.events, raw.clicks, staging.logs..."

User: "Show data quality failures"
Agent: "2 failures found — orders: row count dropped 34%, transactions: null values in customer\_id"

User: "Trigger the Snowflake pipeline"
Agent: "Pipeline triggered successfully. Completed in 3 mins. 142 tables ingested."
```
---
🏗️ Architecture
```
User Input (Streamlit UI)
        ↓
LangGraph Agent (agent.py)
        ↓
Cerebras Llama - decides which tool to call
        ↓
Tools (tools.py) - hits OpenMetadata API
        ↓
OpenMetadata Sandbox API
        ↓
Cerebras formats final answer
        ↓
Answer shown in Streamlit UI
```
Dual Interface
Streamlit Chat UI — browser-based chat interface
MCP Server — exposes agent to any MCP compatible client (Claude Desktop, Cursor, VS Code)
---
🛠️ Tech Stack
Technology	Purpose
LangGraph	Agentic framework — ReAct loop
Cerebras Llama (llama3.1-8b)	AI brain — understands and reasons
OpenMetadata API	Data platform integration
FastMCP	MCP server — exposes tools to AI clients
Streamlit	Chat UI
Python	Core language
---
✅ Sponsor Requirements
✅ Cerebras — Llama3.1-8b used as the LLM brain
✅ OpenMetadata — Deep API integration across tables, pipelines, quality, lineage, governance
✅ MCP — FastMCP server built for T-01 track
---
📁 File Structure
```
openmetadata-workflow-agent/
│
├── config.py        — reads API keys from .env
├── tools.py         — all OpenMetadata API functions
├── agent.py         — LangGraph + Cerebras agentic loop
├── app.py           — Streamlit chat UI
├── server.py        — FastMCP MCP server
├── requirements.txt — dependencies
├── .env             — API keys (NOT pushed to GitHub)
└── .gitignore       — ignores .env and .venv
```
---
🔧 Agent Tools
Tool	What it does
`get\_tables\_tool`	Fetch all tables from OpenMetadata
`get\_unowned\_tables\_tool`	Find tables with no owner assigned
`get\_undocumented\_tables\_tool`	Find tables with no description
`get\_pipelines\_tool`	List all ingestion pipelines + status
`trigger\_pipeline\_tool`	Trigger a pipeline by ID
`get\_quality\_failures\_tool`	Get all failed data quality tests
`get\_lineage\_tool`	Get upstream/downstream lineage of a table
---
🚀 How to Run
Prerequisites
Python 3.10+
Cerebras API key (free at cerebras.ai)
OpenMetadata sandbox access
Setup
Step 1 — Clone the repo:
```bash
git clone https://github.com/YourUsername/openmetadata-workflow-agent
cd openmetadata-workflow-agent
```
Step 2 — Create virtual environment:
```bash
python -m venv .venv
.venv\\Scripts\\activate  # Windows
source .venv/bin/activate  # Mac/Linux
```
Step 3 — Install dependencies:
```bash
pip install -r requirements.txt
```
Step 4 — Create `.env` file:
```
CEREBRAS\_API\_KEY=your-cerebras-api-key-here
OPENMETADATA\_URL=https://sandbox.open-metadata.org/api/v1
```
Step 5 — Run Streamlit UI:
```bash
streamlit run app.py
```
Step 6 — Run MCP Server (optional):
```bash
python server.py
```
---
💬 Example Queries
```
"Which tables have no owners?"
"Show all data quality failures"
"Which tables are undocumented?"
"Show all ingestion pipelines"
"What is the lineage of sample\_data.ecommerce\_db.shopify.orders?"
"Trigger pipeline <pipeline-id>"
```
---
🏆 Hackathon
Event: Back to the Metadata — WeMakeDevs x OpenMetadata
Track: T-01 — MCP Ecosystem & AI Agents
Dates: April 17–26, 2026
Team: AryaBit
---
📋 Requirements
```
requests
python-dotenv
streamlit
mcp
langgraph
langchain-core
langchain-cerebras
```
---
🔒 Security
API keys stored in `.env` file
`.env` is gitignored — never pushed to GitHub
No hardcoded credentials anywhere in codebase
