# Clinic AI Assistant — NL2SQL System

An AI-powered Natural Language to SQL (NL2SQL) system built with **Vanna AI 2.0** and **FastAPI**. Ask questions about clinic data in plain English and get results from a SQLite database — no SQL knowledge required.

---

## Demo

> **User**: "How many patients do we have?"
> **System**: Generates SQL → Executes → Returns: 200 patients

> **User**: "List all doctors and their specializations"
> **System**: Generates SQL → Executes → Returns: 15 doctors with details

---

## Tech Stack

| Technology           | Version   | Purpose                     |
| -------------------- | --------- | --------------------------- |
| Python               | 3.13      | Backend language            |
| Vanna AI             | 2.0.2     | NL2SQL Agent framework      |
| FastAPI              | Latest    | REST API                    |
| SQLite               | Built-in  | Database                    |
| Groq (llama-3.3-70b) | Free tier | LLM for SQL generation      |
| Plotly               | Latest    | Chart generation (frontend) |

---

## Project Structure

```
clinic_project/
    setup_database.py   # Creates SQLite database + inserts dummy data
    vanna_setup.py      # Vanna 2.0 Agent initialization
    seed_memory.py      # Seeds agent memory with 15 Q&A pairs
    main.py             # FastAPI application
    index.html          # Web UI (chat interface)
    requirements.txt    # Python dependencies
    clinic.db           # SQLite database (generated)
    .env                # API keys (not committed to Git)
    RESULTS.md          # Test results for 20 questions
```

---

## Database Schema

The system uses a clinic management database with 5 tables:

| Table        | Rows | Description                                      |
| ------------ | ---- | ------------------------------------------------ |
| patients     | 200  | Patient demographics and contact info            |
| doctors      | 15   | Doctors across 5 specializations                 |
| appointments | 500  | Appointments over the past 12 months             |
| treatments   | ~350 | Treatments linked to completed appointments      |
| invoices     | 300  | Billing records with Paid/Pending/Overdue status |

---

## Setup Instructions

### Prerequisites

- Python 3.10 or higher
- A free Groq API key from https://console.groq.com

### Step 1 — Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/clinic-nl2sql.git
cd clinic-nl2sql
```

### Step 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 3 — Set up environment variables

Create a `.env` file in the project root:

```
GROQ_API_KEY=your_groq_api_key_here
```

Get your free Groq API key at: https://console.groq.com

### Step 4 — Create the database

```bash
python setup_database.py
```

Expected output:

```
All 5 tables created successfully.
Inserted 15 doctors.
Inserted 200 patients.
Inserted 500 appointments.
Inserted 350 treatments.
Inserted 300 invoices.
clinic.db created successfully!
```

### Step 5 — Seed agent memory

```bash
python seed_memory.py
```

This pre-loads 15 example question→SQL pairs into the agent's memory.

### Step 6 — Start the API server

```bash
uvicorn main:app --port 8000 --reload
```

The server will start at: http://localhost:8000

### Step 7 — Open the Web UI

Open `index.html` directly in your browser (double-click it).

Or use the interactive API docs at: http://localhost:8000/docs

---

## API Documentation

### GET /health

Check if the server is running.

**Response:**

```json
{
  "status": "ok",
  "database": "connected",
  "llm_provider": "Groq (llama-3.3-70b-versatile)",
  "agent_memory_items": 15
}
```

### POST /chat

Send a plain English question and get SQL results.

**Request:**

```json
{
  "question": "Show me the top 5 patients by total spending"
}
```

**Response:**

```json
{
  "message": "Here are the top 5 patients by total spending",
  "sql_query": "SELECT p.first_name, p.last_name, SUM(i.total_amount) AS total_spending FROM invoices i JOIN patients p ON p.id = i.patient_id GROUP BY p.id ORDER BY total_spending DESC LIMIT 5",
  "columns": ["first_name", "last_name", "total_spending"],
  "rows": [
    { "first_name": "John", "last_name": "Smith", "total_spending": 4500 },
    { "first_name": "Jane", "last_name": "Doe", "total_spending": 3200 }
  ],
  "row_count": 5,
  "chart": null,
  "chart_type": null,
  "error": null
}
```

---

## Architecture Overview

```
User Question (plain English)
        |
        v
FastAPI Backend (main.py)
        |
        v
Vanna 2.0 Agent
  - LLM: Groq llama-3.3-70b-versatile
  - Memory: DemoAgentMemory
  - Tools: RunSqlTool, SaveQuestionToolArgsTool
        |
        v
SQL Validation (SELECT only, no dangerous queries)
        |
        v
SQLite Database (clinic.db)
        |
        v
Results returned to user (JSON)
        |
        v
Web UI renders table + chart (index.html)
```

---

## LLM Provider

This project uses **Groq** with `llama-3.3-70b-versatile` model.

- **Free tier**: 14,400 requests/day, 100,000 tokens/day
- **Sign up**: https://console.groq.com
- **No credit card required**

---

## SQL Validation & Security

All AI-generated SQL is validated before execution:

- Only SELECT queries are allowed
- Blocked keywords: INSERT, UPDATE, DELETE, DROP, ALTER, EXEC, GRANT, REVOKE, SHUTDOWN
- System tables (sqlite_master) are blocked
- If validation fails, the query is rejected with an error message

---

## Running Tests

To run the 20-question test suite:

```bash
python test_questions.py
```

Results are saved to `test_results.json` and documented in `RESULTS.md`.

---

## Known Limitations

1. **Free tier token limits** — Groq's free tier has daily token limits. If you hit the limit, wait 24 hours or upgrade.
2. **Complex JOINs** — The LLM occasionally struggles with 3+ table JOINs on complex aggregation queries.
3. **In-memory agent memory** — DemoAgentMemory resets on server restart. Run `seed_memory.py` after each restart for best results.
4. **SQLite only** — The system is designed for SQLite. Production use would require switching to a full database like PostgreSQL or SQL Server.

---

## Bonus Features Implemented

- ✅ Web UI with chat interface (index.html)
- ✅ Auto-generated charts using Plotly
- ✅ Input validation (empty questions, max length)
- ✅ SQL injection protection
- ✅ Rate limit error handling with friendly messages
- ✅ CORS enabled for frontend integration
- ✅ Interactive API documentation at /docs

---

## License

This project was built as a technical screening assignment for Cogninest AI.
