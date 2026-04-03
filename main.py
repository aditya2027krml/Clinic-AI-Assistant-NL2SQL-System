"""
main.py - Clinic NL2SQL FastAPI Application
Uses Groq (llama-3.1-8b-instant) as the LLM provider.

HOW TO RUN:
    py -3.13 -m uvicorn main:app --port 8000 --reload
"""

import os
import re
import uuid
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY not found in .env file!")

from vanna import Agent, AgentConfig
from vanna.core.registry import ToolRegistry
from vanna.core.user import UserResolver, User, RequestContext
from vanna.tools import RunSqlTool
from vanna.tools.agent_memory import SaveQuestionToolArgsTool, SearchSavedCorrectToolUsesTool
from vanna.integrations.sqlite import SqliteRunner
from vanna.integrations.local.agent_memory import DemoAgentMemory
from vanna.integrations.openai import OpenAILlmService

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clinic.db")
if not os.path.exists(DB_PATH):
    raise FileNotFoundError(f"clinic.db not found at {DB_PATH}. Run setup_database.py first!")

llm_service = OpenAILlmService(
    api_key=GROQ_API_KEY,
    model="llama-3.3-70b-versatile",
    base_url="https://api.groq.com/openai/v1",
    timeout=60.0,
    max_retries=2,
)

sql_runner   = SqliteRunner(database_path=DB_PATH)
agent_memory = DemoAgentMemory()

tool_registry = ToolRegistry()
tool_registry.register_local_tool(RunSqlTool(sql_runner=sql_runner), [])
tool_registry.register_local_tool(SaveQuestionToolArgsTool(), [])
tool_registry.register_local_tool(SearchSavedCorrectToolUsesTool(), [])


class SimpleUserResolver(UserResolver):
    async def resolve_user(self, context: RequestContext) -> User:
        return User(id="default_user", name="Clinic User")


config = AgentConfig(
    system_prompt=(
        "You are a helpful medical clinic data assistant. "
        "You help staff query the clinic database using plain English. "
        "The database has 5 tables: patients, doctors, appointments, treatments, invoices. "
        "Always generate valid SQLite SQL. "
        "Only use SELECT statements - never INSERT, UPDATE, DELETE, or DROP. "
        "If you cannot answer with the available data, say so clearly."
    )
)

agent = Agent(
    llm_service=llm_service,
    tool_registry=tool_registry,
    agent_memory=agent_memory,
    user_resolver=SimpleUserResolver(),
    config=config,
)

BLOCKED_KEYWORDS = [
    r"\bINSERT\b", r"\bUPDATE\b", r"\bDELETE\b", r"\bDROP\b",
    r"\bALTER\b", r"\bEXEC\b", r"\bGRANT\b", r"\bREVOKE\b",
    r"\bSHUTDOWN\b", r"\bxp_\w+", r"\bsp_\w+",
    r"\bsqlite_master\b", r"\bsqlite_sequence\b",
]


def validate_sql(sql: str) -> tuple[bool, str]:
    sql_upper = sql.upper().strip()
    if not sql_upper.startswith("SELECT"):
        return False, "Only SELECT queries are allowed."
    for pattern in BLOCKED_KEYWORDS:
        if re.search(pattern, sql, re.IGNORECASE):
            return False, "Query contains a blocked keyword."
    return True, ""


def clean_message(text: str, rows=None, row_count=None) -> str:
    """Remove internal agent noise and return a clean user-friendly message."""
    # Remove CSV file references and VISUALIZE_DATA instructions
    text = re.sub(r"Results saved to file:.*?\.csv", "", text)
    text = re.sub(r"\*\*IMPORTANT:.*?\*\*", "", text)
    text = re.sub(r"query_results_\w+\.csv", "", text)
    # Remove agent internal summaries like "Summary: - We searched..."
    text = re.sub(r"Summary:.*", "", text, flags=re.DOTALL)
    # Remove lines starting with "- We "
    text = re.sub(r"- We .*", "", text)
    # Clean up excessive whitespace and newlines
    text = re.sub(r"\n{2,}", " ", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = text.strip()

    # If message is now empty or too short, build a simple one
    if not text or len(text) < 5:
        if rows and row_count:
            text = f"Found {row_count} result(s) for your query."
        else:
            text = "Query executed successfully."

    return text


app = FastAPI(
    title="Clinic NL2SQL API",
    description="Ask questions about clinic data in plain English.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    question: str


class ChatResponse(BaseModel):
    message:    str
    sql_query:  Optional[str]  = None
    columns:    Optional[list] = None
    rows:       Optional[list] = None
    row_count:  Optional[int]  = None
    chart:      Optional[dict] = None
    chart_type: Optional[str]  = None
    error:      Optional[str]  = None


@app.get("/health")
async def health():
    try:
        from vanna.core.tool import ToolContext
        dummy_user   = User(id="health_check", name="Health Check")
        tool_context = ToolContext(
            user=dummy_user,
            conversation_id="health-check",
            request_id=str(uuid.uuid4()),
            agent_memory=agent_memory,
        )
        recent    = await agent_memory.get_recent_memories(context=tool_context, limit=100)
        db_status = "connected" if os.path.exists(DB_PATH) else "not found"
        return {
            "status":             "ok",
            "database":           db_status,
            "llm_provider":       "Groq (llama-3.1-8b-instant)",
            "agent_memory_items": len(recent),
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    question = request.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    if len(question) > 500:
        raise HTTPException(status_code=400, detail="Question too long. Max 500 characters.")

    try:
        request_context = RequestContext()
        components      = []
        async for component in agent.send_message(
            request_context=request_context,
            message=question,
            conversation_id=str(uuid.uuid4()),
        ):
            components.append(component)

    except Exception as e:
        error_msg = str(e)
        if "timed out" in error_msg.lower() or "timeout" in error_msg.lower():
            return ChatResponse(message="The request timed out. Please try again.", error="Request timed out.")
        if "rate" in error_msg.lower() or "quota" in error_msg.lower():
            return ChatResponse(message="API rate limit reached. Please wait a moment and try again.", error="Rate limit exceeded.")
        return ChatResponse(message="Sorry, something went wrong while processing your question.", error=error_msg)

    message_text = ""
    sql_query    = None
    columns      = None
    rows         = None
    row_count    = None

    for component in components:
        rich = component.rich_component
        if hasattr(rich, "type"):
            from vanna.core.rich_component import ComponentType

            if rich.type == ComponentType.TEXT:
                if hasattr(rich, "content") and rich.content:
                    message_text += rich.content + " "
                elif hasattr(rich, "text") and rich.text:
                    message_text += rich.text + " "

            elif rich.type == ComponentType.STATUS_CARD:
                if hasattr(rich, "description") and rich.description:
                    if getattr(rich, "status", "") != "error":
                        message_text += rich.description + " "

            elif rich.type == ComponentType.DATAFRAME:
                if hasattr(rich, "rows") and rich.rows:
                    rows      = rich.rows
                    columns   = rich.columns if hasattr(rich, "columns") else list(rows[0].keys())
                    row_count = len(rows)

            elif rich.type == ComponentType.CODE_BLOCK:
                if hasattr(rich, "content") and rich.content:
                    sql_candidate = rich.content.strip()
                    is_valid, _   = validate_sql(sql_candidate)
                    if is_valid:
                        sql_query = sql_candidate

        if component.simple_component:
            simple = component.simple_component
            if hasattr(simple, "text") and simple.text and not message_text:
                message_text = simple.text

    if sql_query:
        is_valid, error_msg = validate_sql(sql_query)
        if not is_valid:
            return ChatResponse(message=f"Query blocked for security: {error_msg}", error=error_msg)

    # Clean the message
    final_message = clean_message(message_text, rows=rows, row_count=row_count)

    return ChatResponse(
        message=final_message,
        sql_query=sql_query,
        columns=columns,
        rows=rows,
        row_count=row_count,
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)