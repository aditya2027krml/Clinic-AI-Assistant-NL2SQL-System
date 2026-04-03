"""
test_questions.py
-----------------
Tests all 20 questions against the running API server
and prints the results.

HOW TO RUN:
    1. Make sure the server is running in another terminal:
       py -3.13 -m uvicorn main:app --port 8000 --reload

    2. Run this script in a new terminal:
       py -3.13 test_questions.py
"""

import urllib.request
import json
import time

questions = [
    "How many patients do we have?",
    "List all doctors and their specializations",
    "Show me appointments for last month",
    "Which doctor has the most appointments?",
    "What is the total revenue?",
    "Show revenue by doctor",
    "How many cancelled appointments last quarter?",
    "Top 5 patients by spending",
    "Average treatment cost by specialization",
    "Show monthly appointment count for the past 6 months",
    "Which city has the most patients?",
    "List patients who visited more than 3 times",
    "Show unpaid invoices",
    "What percentage of appointments are no-shows?",
    "Show the busiest day of the week for appointments",
    "Revenue trend by month",
    "Average appointment duration by doctor",
    "List patients with overdue invoices",
    "Compare revenue between departments",
    "Show patient registration trend by month",
]

passed = 0
failed = 0
results = []

print("=" * 60)
print("  Testing All 20 Questions")
print("=" * 60)
print()

for i, question in enumerate(questions, 1):
    try:
        # Send request to the API
        data = json.dumps({"question": question}).encode()
        req  = urllib.request.Request(
            "http://localhost:8000/chat",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())

        # Determine pass/fail
        has_rows    = result.get("rows") is not None and len(result.get("rows", [])) > 0
        has_message = bool(result.get("message", "").strip())
        has_error   = bool(result.get("error"))
        is_pass     = (has_rows or has_message) and not has_error

        if is_pass:
            status = "PASS ✅"
            passed += 1
        else:
            status = "FAIL ❌"
            failed += 1

        # Store result
        results.append({
            "number":   i,
            "question": question,
            "status":   "PASS" if is_pass else "FAIL",
            "message":  result.get("message", ""),
            "sql":      result.get("sql_query", ""),
            "rows":     result.get("rows", []),
            "row_count": result.get("row_count", 0),
            "error":    result.get("error", ""),
        })

        # Print result
        print(f"[{i:02d}] {status}")
        print(f"      Q: {question}")
        print(f"      Message: {result.get('message', '')[:100]}")
        print(f"      Rows returned: {result.get('row_count', 0)}")
        if result.get("sql_query"):
            print(f"      SQL: {result.get('sql_query', '')[:80]}...")
        if result.get("error"):
            print(f"      Error: {result.get('error', '')[:100]}")
        print()
        time.sleep(15)  # wait 5 seconds between questions to avoid rate limit

    except Exception as e:
        failed += 1
        results.append({
            "number":   i,
            "question": question,
            "status":   "FAIL",
            "message":  "",
            "sql":      "",
            "rows":     [],
            "row_count": 0,
            "error":    str(e),
        })
        print(f"[{i:02d}] FAIL ❌")
        print(f"      Q: {question}")
        print(f"      Error: {e}")
        print()

# ── SUMMARY ──────────────────────────────────
print("=" * 60)
print(f"  RESULTS: {passed}/20 passed | {failed}/20 failed")
print("=" * 60)

# Save results to a JSON file for RESULTS.md generation
with open("test_results.json", "w") as f:
    json.dump(results, f, indent=2)

print()
print("✅ Results saved to test_results.json")
print("   (We will use this to generate RESULTS.md)")