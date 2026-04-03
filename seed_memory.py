"""
seed_memory.py
--------------
Pre-seeds the Vanna 2.0 Agent Memory with 15 known
good question -> SQL pairs so the agent has a head
start when answering questions.

HOW TO RUN (in your terminal):
    py -3.13 seed_memory.py
"""

import uuid
import asyncio
from vanna.integrations.local.agent_memory import DemoAgentMemory
from vanna.core.tool import ToolContext
from vanna.core.user import User

# ─────────────────────────────────────────────
# 15 QUESTION -> SQL PAIRS
# ─────────────────────────────────────────────
qa_pairs = [

    # ── PATIENT QUERIES ──────────────────────
    {
        "question": "How many patients do we have?",
        "sql": "SELECT COUNT(*) AS total_patients FROM patients"
    },
    {
        "question": "List all patients and their cities",
        "sql": """SELECT first_name, last_name, city
                  FROM patients
                  ORDER BY last_name"""
    },
    {
        "question": "How many male and female patients do we have?",
        "sql": """SELECT gender, COUNT(*) AS count
                  FROM patients
                  GROUP BY gender"""
    },
    {
        "question": "Which city has the most patients?",
        "sql": """SELECT city, COUNT(*) AS patient_count
                  FROM patients
                  GROUP BY city
                  ORDER BY patient_count DESC
                  LIMIT 1"""
    },
    {
        "question": "List all patients from Hyderabad",
        "sql": """SELECT first_name, last_name, email, phone
                  FROM patients
                  WHERE city = 'Hyderabad'"""
    },

    # ── DOCTOR QUERIES ───────────────────────
    {
        "question": "List all doctors and their specializations",
        "sql": """SELECT name, specialization, department
                  FROM doctors
                  ORDER BY specialization"""
    },
    {
        "question": "Which doctor has the most appointments?",
        "sql": """SELECT d.name, COUNT(a.id) AS appointment_count
                  FROM doctors d
                  JOIN appointments a ON a.doctor_id = d.id
                  GROUP BY d.id, d.name
                  ORDER BY appointment_count DESC
                  LIMIT 1"""
    },
    {
        "question": "Show number of appointments per doctor",
        "sql": """SELECT d.name, d.specialization, COUNT(a.id) AS total_appointments
                  FROM doctors d
                  LEFT JOIN appointments a ON a.doctor_id = d.id
                  GROUP BY d.id, d.name
                  ORDER BY total_appointments DESC"""
    },

    # ── APPOINTMENT QUERIES ──────────────────
    {
        "question": "How many appointments are there by status?",
        "sql": """SELECT status, COUNT(*) AS count
                  FROM appointments
                  GROUP BY status
                  ORDER BY count DESC"""
    },
    {
        "question": "Show appointments from the last 3 months",
        "sql": """SELECT a.id, p.first_name, p.last_name, d.name AS doctor,
                         a.appointment_date, a.status
                  FROM appointments a
                  JOIN patients p ON p.id = a.patient_id
                  JOIN doctors d ON d.id = a.doctor_id
                  WHERE a.appointment_date >= DATE('now', '-3 months')
                  ORDER BY a.appointment_date DESC"""
    },
    {
        "question": "Show monthly appointment count for the past 6 months",
        "sql": """SELECT strftime('%Y-%m', appointment_date) AS month,
                         COUNT(*) AS appointment_count
                  FROM appointments
                  WHERE appointment_date >= DATE('now', '-6 months')
                  GROUP BY month
                  ORDER BY month"""
    },

    # ── FINANCIAL QUERIES ────────────────────
    {
        "question": "What is the total revenue?",
        "sql": """SELECT SUM(total_amount) AS total_revenue,
                         SUM(paid_amount) AS total_collected,
                         SUM(total_amount - paid_amount) AS total_outstanding
                  FROM invoices"""
    },
    {
        "question": "Show revenue by doctor",
        "sql": """SELECT d.name, SUM(i.total_amount) AS total_revenue
                  FROM invoices i
                  JOIN appointments a ON a.patient_id = i.patient_id
                  JOIN doctors d ON d.id = a.doctor_id
                  GROUP BY d.id, d.name
                  ORDER BY total_revenue DESC"""
    },
    {
        "question": "Show all unpaid invoices",
        "sql": """SELECT i.id, p.first_name, p.last_name,
                         i.invoice_date, i.total_amount, i.paid_amount,
                         (i.total_amount - i.paid_amount) AS balance_due,
                         i.status
                  FROM invoices i
                  JOIN patients p ON p.id = i.patient_id
                  WHERE i.status IN ('Pending', 'Overdue')
                  ORDER BY i.status, i.invoice_date"""
    },

    # ── TIME-BASED QUERIES ───────────────────
    {
        "question": "Show top 5 patients by total spending",
        "sql": """SELECT p.first_name, p.last_name,
                         SUM(i.total_amount) AS total_spending
                  FROM invoices i
                  JOIN patients p ON p.id = i.patient_id
                  GROUP BY p.id, p.first_name, p.last_name
                  ORDER BY total_spending DESC
                  LIMIT 5"""
    },
]

# ─────────────────────────────────────────────
# SCHEMA TEXT
# ─────────────────────────────────────────────
schema_text = """
The clinic database has these tables:

1. patients (id, first_name, last_name, email, phone, date_of_birth, gender, city, registered_date)
2. doctors (id, name, specialization, department, phone)
   - Specializations: Dermatology, Cardiology, Orthopedics, General, Pediatrics
3. appointments (id, patient_id, doctor_id, appointment_date, status, notes)
   - Status values: Scheduled, Completed, Cancelled, No-Show
4. treatments (id, appointment_id, treatment_name, cost, duration_minutes)
   - Only linked to Completed appointments
   - Cost range: 50 to 5000
5. invoices (id, patient_id, invoice_date, total_amount, paid_amount, status)
   - Status values: Paid, Pending, Overdue
"""

# ─────────────────────────────────────────────
# MAIN ASYNC FUNCTION
# ─────────────────────────────────────────────
async def seed():
    # Create memory instance
    agent_memory = DemoAgentMemory()

    # Create dummy user and context for seeding
    dummy_user = User(id="default_user", name="Clinic User")
    tool_context = ToolContext(
        user=dummy_user,
        conversation_id="seed-conversation",
        request_id=str(uuid.uuid4()),
        agent_memory=agent_memory,
    )

    print("=" * 50)
    print("  Seeding Agent Memory")
    print("=" * 50)

    # Seed all 15 Q&A pairs
    for i, pair in enumerate(qa_pairs, 1):
        await agent_memory.save_tool_usage(
            question=pair["question"],
            tool_name="run_sql",
            args={"sql": pair["sql"]},
            context=tool_context,
            success=True,
            metadata={"seeded": True, "index": i}
        )
        print(f"✅ [{i:02d}/15] Seeded: {pair['question']}")

    # Save schema as text memory
    await agent_memory.save_text_memory(
        content=schema_text,
        context=tool_context,
    )
    print()
    print("✅ Database schema saved to text memory")

    # Verify
    recent = await agent_memory.get_recent_memories(
        context=tool_context,
        limit=5
    )
    print()
    print(f"✅ Verification: {len(recent)} recent memories found in agent memory")
    print()
    print("=" * 50)
    print("  Done! Seeded 15 Q&A pairs + schema ✅")
    print("=" * 50)


# ─────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────
if __name__ == "__main__":
    asyncio.run(seed())