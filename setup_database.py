"""
setup_database.py
-----------------
Creates the clinic.db SQLite database with all 5 tables
and fills them with realistic dummy data.

HOW TO RUN (in your terminal / VS Code terminal):
    python setup_database.py

This will create a file called clinic.db in the same folder.
"""

import sqlite3
import random
from datetime import datetime, timedelta, date

# ─────────────────────────────────────────────
# HELPER: generate a random date between two dates
# ─────────────────────────────────────────────
def random_date(start: date, end: date) -> date:
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, delta))

def random_datetime(start: date, end: date) -> datetime:
    d = random_date(start, end)
    hour = random.randint(8, 17)       # clinic hours 8am–5pm
    minute = random.choice([0, 15, 30, 45])
    return datetime(d.year, d.month, d.day, hour, minute)

# ─────────────────────────────────────────────
# CONNECT / CREATE DATABASE
# ─────────────────────────────────────────────
conn = sqlite3.connect("clinic.db")
cursor = conn.cursor()

# Enable foreign keys
cursor.execute("PRAGMA foreign_keys = ON")

# ─────────────────────────────────────────────
# DROP TABLES IF THEY ALREADY EXIST
# (so you can safely re-run this script)
# ─────────────────────────────────────────────
cursor.executescript("""
    DROP TABLE IF EXISTS invoices;
    DROP TABLE IF EXISTS treatments;
    DROP TABLE IF EXISTS appointments;
    DROP TABLE IF EXISTS doctors;
    DROP TABLE IF EXISTS patients;
""")

# ─────────────────────────────────────────────
# CREATE TABLE 1: patients
# ─────────────────────────────────────────────
cursor.execute("""
CREATE TABLE patients (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name      TEXT    NOT NULL,
    last_name       TEXT    NOT NULL,
    email           TEXT,
    phone           TEXT,
    date_of_birth   DATE,
    gender          TEXT,
    city            TEXT,
    registered_date DATE
)
""")

# ─────────────────────────────────────────────
# CREATE TABLE 2: doctors
# ─────────────────────────────────────────────
cursor.execute("""
CREATE TABLE doctors (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    name            TEXT    NOT NULL,
    specialization  TEXT,
    department      TEXT,
    phone           TEXT
)
""")

# ─────────────────────────────────────────────
# CREATE TABLE 3: appointments
# ─────────────────────────────────────────────
cursor.execute("""
CREATE TABLE appointments (
    id                INTEGER  PRIMARY KEY AUTOINCREMENT,
    patient_id        INTEGER  NOT NULL,
    doctor_id         INTEGER  NOT NULL,
    appointment_date  DATETIME NOT NULL,
    status            TEXT,
    notes             TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(id),
    FOREIGN KEY (doctor_id)  REFERENCES doctors(id)
)
""")

# ─────────────────────────────────────────────
# CREATE TABLE 4: treatments
# ─────────────────────────────────────────────
cursor.execute("""
CREATE TABLE treatments (
    id                INTEGER PRIMARY KEY AUTOINCREMENT,
    appointment_id    INTEGER NOT NULL,
    treatment_name    TEXT,
    cost              REAL,
    duration_minutes  INTEGER,
    FOREIGN KEY (appointment_id) REFERENCES appointments(id)
)
""")

# ─────────────────────────────────────────────
# CREATE TABLE 5: invoices
# ─────────────────────────────────────────────
cursor.execute("""
CREATE TABLE invoices (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    patient_id    INTEGER NOT NULL,
    invoice_date  DATE,
    total_amount  REAL,
    paid_amount   REAL,
    status        TEXT,
    FOREIGN KEY (patient_id) REFERENCES patients(id)
)
""")

conn.commit()
print("✅ All 5 tables created successfully.")

# ═══════════════════════════════════════════════════════
# INSERT DUMMY DATA
# ═══════════════════════════════════════════════════════

today      = date.today()
one_year_ago = today - timedelta(days=365)

# ─────────────────────────────────────────────
# 15 DOCTORS across 5 specializations
# ─────────────────────────────────────────────
doctors_data = [
    # (name, specialization, department, phone)
    ("Dr. Arjun Mehta",      "Cardiology",    "Cardiology",    "9876543210"),
    ("Dr. Priya Nair",       "Cardiology",    "Cardiology",    "9876543211"),
    ("Dr. Rohan Verma",      "Cardiology",    "Cardiology",    None),           # NULL phone
    ("Dr. Sunita Sharma",    "Dermatology",   "Dermatology",   "9876543213"),
    ("Dr. Kavya Reddy",      "Dermatology",   "Dermatology",   "9876543214"),
    ("Dr. Anil Kumar",       "Dermatology",   "Dermatology",   "9876543215"),
    ("Dr. Neha Singh",       "Orthopedics",   "Orthopedics",   "9876543216"),
    ("Dr. Vikram Joshi",     "Orthopedics",   "Orthopedics",   None),           # NULL phone
    ("Dr. Deepa Pillai",     "Orthopedics",   "Orthopedics",   "9876543218"),
    ("Dr. Ramesh Iyer",      "General",       "General Medicine","9876543219"),
    ("Dr. Anita Desai",      "General",       "General Medicine","9876543220"),
    ("Dr. Suresh Rao",       "General",       "General Medicine",None),         # NULL phone
    ("Dr. Meera Patel",      "Pediatrics",    "Pediatrics",    "9876543222"),
    ("Dr. Kiran Bose",       "Pediatrics",    "Pediatrics",    "9876543223"),
    ("Dr. Tanya Gupta",      "Pediatrics",    "Pediatrics",    "9876543224"),
]

cursor.executemany("""
    INSERT INTO doctors (name, specialization, department, phone)
    VALUES (?, ?, ?, ?)
""", doctors_data)
conn.commit()
print(f"✅ Inserted {len(doctors_data)} doctors.")

# ─────────────────────────────────────────────
# 200 PATIENTS across 8-10 cities
# ─────────────────────────────────────────────
first_names = [
    "Aarav","Aditi","Aishwarya","Akash","Ananya","Anil","Anita","Arjun",
    "Aryan","Bhavna","Chetan","Deepa","Deepak","Divya","Gaurav","Geeta",
    "Harish","Isha","Jayesh","Karan","Kavita","Kiran","Komal","Lakshmi",
    "Manish","Meena","Meera","Mohit","Neeraj","Neha","Nikhil","Nisha",
    "Pallavi","Pooja","Pradeep","Priya","Rahul","Raj","Rajan","Rajesh",
    "Ramesh","Ravi","Reema","Rekha","Rohit","Sachin","Sanjay","Sanjana",
    "Sapna","Seema","Shivam","Shreya","Sneha","Sonal","Suresh","Swati",
    "Tanvi","Tarun","Uma","Usha","Varun","Vijay","Vikram","Vimal",
    "Vinay","Vinita","Vishal","Yamini","Yogesh","Zara","Zoya","Amit"
]

last_names = [
    "Agarwal","Bansal","Bose","Chandra","Choudhary","Das","Desai","Dey",
    "Dixit","Gandhi","Ghosh","Goswami","Gupta","Iyer","Jain","Jha",
    "Joshi","Kapoor","Kaur","Khan","Khanna","Kumar","Malhotra","Mehta",
    "Mishra","Nair","Patel","Pillai","Rao","Reddy","Roy","Saha",
    "Shah","Sharma","Singh","Sinha","Srivastava","Tiwari","Verma","Yadav"
]

cities = [
    "Hyderabad","Bangalore","Mumbai","Delhi","Chennai",
    "Pune","Kolkata","Ahmedabad","Jaipur","Lucknow"
]

genders = ["M", "F"]

patients_data = []
for i in range(200):
    first   = random.choice(first_names)
    last    = random.choice(last_names)
    gender  = random.choice(genders)
    city    = random.choice(cities)
    dob     = random_date(date(1950, 1, 1), date(2005, 12, 31))
    reg     = random_date(one_year_ago, today)

    # ~20% chance of NULL email, ~15% chance of NULL phone
    email = f"{first.lower()}.{last.lower()}{random.randint(1,99)}@email.com" \
            if random.random() > 0.20 else None
    phone = f"9{random.randint(100000000, 999999999)}" \
            if random.random() > 0.15 else None

    patients_data.append((first, last, email, phone,
                          dob.isoformat(), gender, city, reg.isoformat()))

cursor.executemany("""
    INSERT INTO patients
        (first_name, last_name, email, phone, date_of_birth, gender, city, registered_date)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", patients_data)
conn.commit()
print(f"✅ Inserted 200 patients.")

# ─────────────────────────────────────────────
# 500 APPOINTMENTS over the last 12 months
# with varied statuses and patient distribution
# ─────────────────────────────────────────────

# Make some patients "repeat visitors" — pick 30 patients who appear often
all_patient_ids  = list(range(1, 201))
all_doctor_ids   = list(range(1, 16))

repeat_patients  = random.sample(all_patient_ids, 30)   # heavy users
statuses         = ["Scheduled", "Completed", "Cancelled", "No-Show"]
status_weights   = [0.15, 0.60, 0.15, 0.10]             # mostly completed

appointments_data = []
for _ in range(500):
    # 40% chance of picking a repeat patient
    if random.random() < 0.40:
        patient_id = random.choice(repeat_patients)
    else:
        patient_id = random.choice(all_patient_ids)

    # Some doctors are busier than others (doctors 1,4,10 get double weight)
    busy_doctors = [1, 1, 4, 4, 10, 10] + all_doctor_ids
    doctor_id  = random.choice(busy_doctors)

    appt_dt    = random_datetime(one_year_ago, today)
    status     = random.choices(statuses, weights=status_weights)[0]

    # ~25% chance of NULL notes
    notes = random.choice([
        "Follow-up required", "First visit", "Referred by GP",
        "Routine check", "Post-surgery review", "Urgent consultation", None
    ]) if random.random() > 0.25 else None

    appointments_data.append((patient_id, doctor_id,
                               appt_dt.strftime("%Y-%m-%d %H:%M:%S"),
                               status, notes))

cursor.executemany("""
    INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, notes)
    VALUES (?, ?, ?, ?, ?)
""", appointments_data)
conn.commit()
print(f"✅ Inserted 500 appointments.")

# ─────────────────────────────────────────────
# 350 TREATMENTS — linked to COMPLETED appointments only
# ─────────────────────────────────────────────

# Get all completed appointment IDs
cursor.execute("SELECT id FROM appointments WHERE status = 'Completed'")
completed_appt_ids = [row[0] for row in cursor.fetchall()]

treatment_names_by_spec = {
    "Cardiology":   ["ECG","Echocardiogram","Stress Test","Angioplasty","Blood Pressure Monitoring"],
    "Dermatology":  ["Skin Biopsy","Chemical Peel","Acne Treatment","Laser Therapy","Patch Test"],
    "Orthopedics":  ["X-Ray","MRI Scan","Physiotherapy","Joint Injection","Fracture Management"],
    "General":      ["Blood Test","Urine Test","General Checkup","Vaccination","BP Check"],
    "Pediatrics":   ["Vaccination","Growth Assessment","Fever Treatment","Nutrition Counseling","Allergy Test"],
}
all_treatment_names = [t for lst in treatment_names_by_spec.values() for t in lst]

treatments_data = []
# Pick 350 completed appointments to add treatments to
chosen_appts = random.sample(completed_appt_ids, min(350, len(completed_appt_ids)))
for appt_id in chosen_appts:
    treatment = random.choice(all_treatment_names)
    cost      = round(random.uniform(50, 5000), 2)   # ₹50 to ₹5000
    duration  = random.choice([15, 20, 30, 45, 60, 90, 120])
    treatments_data.append((appt_id, treatment, cost, duration))

cursor.executemany("""
    INSERT INTO treatments (appointment_id, treatment_name, cost, duration_minutes)
    VALUES (?, ?, ?, ?)
""", treatments_data)
conn.commit()
print(f"✅ Inserted {len(treatments_data)} treatments.")

# ─────────────────────────────────────────────
# 300 INVOICES — linked to patients
# mix of Paid, Pending, Overdue
# ─────────────────────────────────────────────
invoice_statuses  = ["Paid", "Pending", "Overdue"]
invoice_weights   = [0.55, 0.25, 0.20]              # mostly paid

invoices_data = []
# Pick 300 random patients (with repetition allowed)
invoice_patients = random.choices(all_patient_ids, k=300)

for patient_id in invoice_patients:
    invoice_date  = random_date(one_year_ago, today)
    total_amount  = round(random.uniform(100, 15000), 2)
    status        = random.choices(invoice_statuses, weights=invoice_weights)[0]

    if status == "Paid":
        paid_amount = total_amount
    elif status == "Pending":
        paid_amount = round(random.uniform(0, total_amount * 0.5), 2)
    else:  # Overdue
        paid_amount = 0.0

    invoices_data.append((patient_id, invoice_date.isoformat(),
                          total_amount, paid_amount, status))

cursor.executemany("""
    INSERT INTO invoices (patient_id, invoice_date, total_amount, paid_amount, status)
    VALUES (?, ?, ?, ?, ?)
""", invoices_data)
conn.commit()
print(f"✅ Inserted 300 invoices.")

# ─────────────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────────────
cursor.execute("SELECT COUNT(*) FROM patients")
p = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM doctors")
d = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM appointments")
a = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM treatments")
t = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM invoices")
i = cursor.fetchone()[0]

conn.close()

print()
print("=" * 45)
print("  DATABASE SUMMARY")
print("=" * 45)
print(f"  Patients     : {p}")
print(f"  Doctors      : {d}")
print(f"  Appointments : {a}")
print(f"  Treatments   : {t}")
print(f"  Invoices     : {i}")
print("=" * 45)
print("  clinic.db created successfully! ✅")
print("=" * 45)