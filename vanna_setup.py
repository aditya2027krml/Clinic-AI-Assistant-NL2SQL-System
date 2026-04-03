"""
vanna_setup.py
--------------
Sets up the full Vanna 2.0 Agent with:
- Groq (llama-3.3-70b) as the LLM
- SQLite as the database
- All required tools registered
- Agent memory system
- User resolver

HOW TO TEST (in your terminal):
    py -3.13 vanna_setup.py
"""

import os
from dotenv import load_dotenv

# ─────────────────────────────────────────────
# LOAD API KEY FROM .env FILE
# ─────────────────────────────────────────────
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "❌ GROQ_API_KEY not found! "
        "Make sure your .env file has: GROQ_API_KEY=your_key_here"
    )

# ─────────────────────────────────────────────
# VANNA 2.0 IMPORTS
# ─────────────────────────────────────────────
from vanna import Agent, AgentConfig
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext
from vanna.tools import RunSqlTool, VisualizeDataTool
from vanna.tools.agent_memory import (
    SaveQuestionToolArgsTool,
    SearchSavedCorrectToolUsesTool,
)
from vanna.integrations.sqlite import SqliteRunner
from vanna.integrations.local.agent_memory import DemoAgentMemory
from vanna.integrations.openai import OpenAILlmService

# ─────────────────────────────────────────────
# STEP 1: CREATE THE LLM SERVICE (Groq)
# ─────────────────────────────────────────────
# Groq uses OpenAI-compatible API
# We just point base_url to Groq's servers
llm_service = OpenAILlmService(
    api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    base_url="https://api.groq.com/openai/v1",
)

# ─────────────────────────────────────────────
# STEP 2: CREATE THE SQLITE DATABASE RUNNER
# ─────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clinic.db")

if not os.path.exists(DB_PATH):
    raise FileNotFoundError(
        f"❌ clinic.db not found at {DB_PATH}\n"
        "Please run setup_database.py first!"
    )

sql_runner = SqliteRunner(database_path=DB_PATH)

# ─────────────────────────────────────────────
# STEP 3: CREATE AGENT MEMORY
# ─────────────────────────────────────────────
agent_memory = DemoAgentMemory()

# ─────────────────────────────────────────────
# STEP 4: CREATE AND REGISTER TOOLS
# ─────────────────────────────────────────────
tool_registry = ToolRegistry()
tool_registry.register_local_tool(RunSqlTool(sql_runner=sql_runner), [])
tool_registry.register_local_tool(VisualizeDataTool(), [])
tool_registry.register_local_tool(SaveQuestionToolArgsTool(), [])
tool_registry.register_local_tool(SearchSavedCorrectToolUsesTool(), [])

# ─────────────────────────────────────────────
# STEP 5: CREATE USER RESOLVER
# ─────────────────────────────────────────────
class SimpleUserResolver(UserResolver):
    async def resolve_user(self, context: RequestContext) -> User:
        return User(id="default_user", name="Clinic User")

user_resolver = SimpleUserResolver()

# ─────────────────────────────────────────────
# STEP 6: CREATE THE AGENT
# ─────────────────────────────────────────────
config = AgentConfig(
    system_prompt=(
        "You are a helpful medical clinic data assistant. "
        "You help staff query the clinic database using plain English. "
        "The database has 5 tables: patients, doctors, appointments, treatments, invoices. "
        "Always generate valid SQLite SQL. "
        "Only use SELECT statements — never INSERT, UPDATE, DELETE, or DROP. "
        "If you cannot answer with the available data, say so clearly."
    )
)

agent = Agent(
    llm_service=llm_service,
    tool_registry=tool_registry,
    agent_memory=agent_memory,
    user_resolver=user_resolver,
    config=config,
)

# ─────────────────────────────────────────────
# QUICK TEST
# ─────────────────────────────────────────────
if __name__ == "__main__":
    print("=" * 50)
    print("  Testing Vanna 2.0 Agent Setup (Groq)")
    print("=" * 50)
    print("✅ LLM Service (Groq llama-3.3-70b) created")
    print("✅ SQLite Runner connected to clinic.db")
    print("✅ Agent Memory initialized")
    print("✅ Tools registered:")
    print("     - RunSqlTool")
    print("     - VisualizeDataTool")
    print("     - SaveQuestionToolArgsTool")
    print("     - SearchSavedCorrectToolUsesTool")
    print("✅ User Resolver created")
    print("✅ Agent assembled successfully")
    print()
    print("=" * 50)
    print("  vanna_setup.py is ready to use! ✅")
    print("=" * 50)