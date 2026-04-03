# NL2SQL Test Results

## Summary

| Metric          | Value                          |
| --------------- | ------------------------------ |
| Total Questions | 20                             |
| Passed          | 4                              |
| Failed          | 16                             |
| Pass Rate       | 20%                            |
| LLM Provider    | Groq (llama-3.3-70b-versatile) |
| Database        | SQLite (clinic.db)             |

---

## Detailed Results

### ✅ Question 1 — How many patients do we have?

- **Expected**: Returns count of all patients
- **Generated SQL**: `SELECT COUNT(*) AS total_patients FROM patients`
- **Result**: ✅ PASS
- **Output**: 200 patients
- **Notes**: Correct result returned successfully.

---

### ✅ Question 2 — List all doctors and their specializations

- **Expected**: Returns list of all doctors with specializations
- **Generated SQL**: `SELECT id, name, specialization, department, phone FROM doctors`
- **Result**: ✅ PASS
- **Output**: 15 rows returned with all doctor details
- **Notes**: All 15 doctors returned correctly with name, specialization and department.

---

### ✅ Question 3 — Show me appointments for last month

- **Expected**: Filters appointments by last month's date range
- **Generated SQL**: `SELECT * FROM appointments WHERE appointment_date >= DATE('now', '-1 month')`
- **Result**: ✅ PASS
- **Output**: 44 rows returned
- **Notes**: Correct date filtering applied using SQLite DATE function.

---

### ✅ Question 4 — Which doctor has the most appointments?

- **Expected**: Aggregation and ordering to find busiest doctor
- **Generated SQL**: `SELECT doctor_id, COUNT(*) AS num_appointments FROM appointments GROUP BY doctor_id ORDER BY num_appointments DESC LIMIT 1`
- **Result**: ✅ PASS
- **Output**: doctor_id=1 with 89 appointments
- **Notes**: Correct aggregation query generated and executed.

---

### ❌ Question 5 — What is the total revenue?

- **Expected**: SUM of total_amount from invoices table
- **Generated SQL**: None generated successfully
- **Result**: ❌ FAIL
- **Output**: No data returned
- **Notes**: The agent failed to identify the correct table (invoices) for revenue calculation. The model attempted to search for a non-existent revenue table.

---

### ❌ Question 6 — Show revenue by doctor

- **Expected**: JOIN invoices and doctors, GROUP BY doctor name
- **Generated SQL**: None generated successfully
- **Result**: ❌ FAIL
- **Output**: Error — unexpected error occurred
- **Notes**: Complex multi-table JOIN caused the agent to time out or generate incorrect table references.

---

### ❌ Question 7 — How many cancelled appointments last quarter?

- **Expected**: COUNT with status filter and date range
- **Generated SQL**: Partially generated but incorrect
- **Result**: ❌ FAIL
- **Output**: No correct data returned
- **Notes**: Agent reached tool execution limit (10 tools) without producing correct SQL.

---

### ❌ Question 8 — Top 5 patients by spending

- **Expected**: JOIN patients and invoices, ORDER BY total DESC, LIMIT 5
- **Generated SQL**: None generated successfully
- **Result**: ❌ FAIL
- **Output**: Error — unexpected error occurred
- **Notes**: Multi-table JOIN with aggregation caused the agent to fail.

---

### ❌ Question 9 — Average treatment cost by specialization

- **Expected**: JOIN treatments, appointments, doctors; AVG(cost) GROUP BY specialization
- **Generated SQL**: Incorrect — referenced wrong column names
- **Result**: ❌ FAIL
- **Output**: Column not found error
- **Notes**: The model used incorrect column names for the JOIN condition.

---

### ❌ Question 10 — Show monthly appointment count for the past 6 months

- **Expected**: strftime grouping on appointment_date
- **Generated SQL**: Partially correct but not executed
- **Result**: ❌ FAIL
- **Output**: No rows returned
- **Notes**: The agent generated a description but did not return actual data rows.

---

### ❌ Question 11 — Which city has the most patients?

- **Expected**: GROUP BY city, COUNT(\*), ORDER BY DESC, LIMIT 1
- **Generated SQL**: None generated successfully
- **Result**: ❌ FAIL
- **Output**: Error — unexpected error occurred
- **Notes**: Connection timeout caused the request to fail.

---

### ❌ Question 12 — List patients who visited more than 3 times

- **Expected**: GROUP BY patient_id HAVING COUNT > 3
- **Generated SQL**: Incorrect — wrong table name used
- **Result**: ❌ FAIL
- **Output**: No data returned
- **Notes**: The model attempted to use a non-existent table name instead of appointments.

---

### ❌ Question 13 — Show unpaid invoices

- **Expected**: SELECT from invoices WHERE status IN ('Pending', 'Overdue')
- **Generated SQL**: Incorrect — used wrong column name 'paid'
- **Result**: ❌ FAIL
- **Output**: Column not found error
- **Notes**: The model used 'paid' as a boolean column instead of the correct 'status' column with values Pending/Overdue.

---

### ❌ Question 14 — What percentage of appointments are no-shows?

- **Expected**: COUNT(No-Show) / COUNT(_) _ 100
- **Generated SQL**: Partially correct
- **Result**: ❌ FAIL
- **Output**: Returned 0.0% which is incorrect given the data
- **Notes**: The SQL logic for percentage calculation was incorrect.

---

### ❌ Question 15 — Show the busiest day of the week for appointments

- **Expected**: strftime('%w', appointment_date), GROUP BY, ORDER BY COUNT DESC
- **Generated SQL**: Incorrect — database function error
- **Result**: ❌ FAIL
- **Output**: Database error
- **Notes**: The model used a non-SQLite date function instead of strftime.

---

### ❌ Question 16 — Revenue trend by month

- **Expected**: strftime('%Y-%m', invoice_date), SUM(total_amount) GROUP BY month
- **Generated SQL**: None generated correctly
- **Result**: ❌ FAIL
- **Output**: No data returned
- **Notes**: The agent failed to identify the correct table and column for revenue trend.

---

### ❌ Question 17 — Average appointment duration by doctor

- **Expected**: JOIN treatments and doctors, AVG(duration_minutes) GROUP BY doctor name
- **Generated SQL**: Incorrect — used wrong column name 'duration'
- **Result**: ❌ FAIL
- **Output**: Column not found
- **Notes**: The correct column is duration_minutes in the treatments table, not duration.

---

### ❌ Question 18 — List patients with overdue invoices

- **Expected**: JOIN patients and invoices WHERE invoices.status = 'Overdue'
- **Generated SQL**: None generated successfully
- **Result**: ❌ FAIL
- **Output**: No rows returned
- **Notes**: The agent searched for similar patterns but failed to generate correct SQL.

---

### ❌ Question 19 — Compare revenue between departments

- **Expected**: JOIN invoices, appointments, doctors GROUP BY department
- **Generated SQL**: None generated correctly
- **Result**: ❌ FAIL
- **Output**: Wrong table references
- **Notes**: The agent referenced non-existent tables instead of joining invoices with doctors via appointments.

---

### ❌ Question 20 — Show patient registration trend by month

- **Expected**: strftime('%Y-%m', registered_date) GROUP BY month COUNT(\*)
- **Generated SQL**: Incorrect — used wrong column name 'registration_date'
- **Result**: ❌ FAIL
- **Output**: Column not found
- **Notes**: The correct column is registered_date in the patients table, not registration_date.

---

## Analysis of Failures

### Root Causes

**1. Wrong column/table names (5 failures)**
The LLM occasionally used incorrect column names such as `duration` instead of `duration_minutes`, `registration_date` instead of `registered_date`, and `paid` instead of checking `status`. This is a known limitation of smaller free-tier LLMs that don't have schema awareness built in.

**2. Complex multi-table JOINs (6 failures)**
Questions requiring 3+ table JOINs with aggregations (revenue by doctor, top patients by spending, average treatment cost by specialization) caused the agent to either timeout or generate incorrect SQL.

**3. API timeouts (3 failures)**
Some requests timed out due to Groq API latency on complex queries. Retry logic was added but some requests still failed.

**4. Tool execution limit (1 failure)**
The agent hit the maximum tool execution limit (10 tools) on some complex queries before producing a result.

---

## What Would Improve the Score

1. **Fine-tuned schema injection** — Providing the exact table and column names in every prompt would fix the wrong column name failures
2. **A more capable LLM** — Using GPT-4 or Claude would significantly improve complex JOIN handling
3. **Pre-cached SQL for common queries** — Storing known good SQL queries and retrieving them for similar questions
4. **Better error recovery** — Implementing retry logic when the agent generates wrong SQL

---

## Correct SQL for Failed Questions (Reference)

```sql
-- Q5: Total revenue
SELECT SUM(total_amount) AS total_revenue,
       SUM(paid_amount) AS total_collected,
       SUM(total_amount - paid_amount) AS outstanding
FROM invoices;

-- Q6: Revenue by doctor
SELECT d.name, SUM(i.total_amount) AS revenue
FROM invoices i
JOIN appointments a ON a.patient_id = i.patient_id
JOIN doctors d ON d.id = a.doctor_id
GROUP BY d.name ORDER BY revenue DESC;

-- Q7: Cancelled appointments last quarter
SELECT COUNT(*) FROM appointments
WHERE status = 'Cancelled'
AND appointment_date >= DATE('now', '-3 months');

-- Q8: Top 5 patients by spending
SELECT p.first_name, p.last_name, SUM(i.total_amount) AS total_spending
FROM invoices i JOIN patients p ON p.id = i.patient_id
GROUP BY p.id ORDER BY total_spending DESC LIMIT 5;

-- Q9: Avg treatment cost by specialization
SELECT d.specialization, AVG(t.cost) AS avg_cost
FROM treatments t
JOIN appointments a ON a.id = t.appointment_id
JOIN doctors d ON d.id = a.doctor_id
GROUP BY d.specialization;

-- Q13: Unpaid invoices
SELECT p.first_name, p.last_name, i.total_amount, i.status
FROM invoices i JOIN patients p ON p.id = i.patient_id
WHERE i.status IN ('Pending', 'Overdue');

-- Q20: Patient registration trend
SELECT strftime('%Y-%m', registered_date) AS month, COUNT(*) AS new_patients
FROM patients GROUP BY month ORDER BY month;
```
