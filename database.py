"""
Database layer for Hospital Management System using SQLite.
Includes schema definition and realistic pre-populated mock hospital records.
"""

import sqlite3
import os
from datetime import datetime, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "hospital.db")


def get_connection():
    """Returns a connection to the SQLite database with dictionary-like row factory."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initializes tables and populates starter demo data if empty."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Patients Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            age INTEGER NOT NULL,
            gender TEXT NOT NULL,
            blood_group TEXT,
            phone TEXT NOT NULL,
            email TEXT,
            address TEXT,
            department TEXT NOT NULL,
            doctor_name TEXT NOT NULL,
            admission_date TEXT NOT NULL,
            status TEXT NOT NULL, -- 'Admitted', 'Outpatient', 'Discharged', 'ICU'
            condition TEXT NOT NULL -- 'Stable', 'Critical', 'Under Observation', 'Recovering'
        )
    """)

    # 2. Doctors Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            doctor_id TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            department TEXT NOT NULL,
            phone TEXT NOT NULL,
            email TEXT NOT NULL,
            experience_years INTEGER NOT NULL,
            room_no TEXT NOT NULL,
            availability TEXT NOT NULL, -- 'Available', 'In Surgery', 'On Leave', 'In OPD'
            opd_hours TEXT NOT NULL
        )
    """)

    # 3. Appointments Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_id TEXT UNIQUE NOT NULL,
            patient_name TEXT NOT NULL,
            doctor_name TEXT NOT NULL,
            department TEXT NOT NULL,
            appt_date TEXT NOT NULL,
            appt_time TEXT NOT NULL,
            status TEXT NOT NULL, -- 'Scheduled', 'In Progress', 'Completed', 'Cancelled'
            reason TEXT
        )
    """)

    # 4. Wards & Beds Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ward_name TEXT NOT NULL, -- 'ICU Block A', 'General Ward East', 'Pediatric Care', 'Cardiac Care'
            bed_number TEXT UNIQUE NOT NULL,
            ward_type TEXT NOT NULL, -- 'ICU', 'General', 'Private', 'Semi-Private'
            patient_name TEXT,
            status TEXT NOT NULL, -- 'Available', 'Occupied', 'Maintenance', 'Reserved'
            daily_rate REAL NOT NULL
        )
    """)

    # 5. Billing & Invoices Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id TEXT UNIQUE NOT NULL,
            patient_name TEXT NOT NULL,
            bill_date TEXT NOT NULL,
            consultation_fee REAL DEFAULT 0,
            lab_charges REAL DEFAULT 0,
            medicine_charges REAL DEFAULT 0,
            room_charges REAL DEFAULT 0,
            discount REAL DEFAULT 0,
            total_amount REAL NOT NULL,
            payment_status TEXT NOT NULL, -- 'Paid', 'Pending', 'Overdue'
            payment_method TEXT -- 'Cash', 'Credit Card', 'Insurance', 'UPI/NetBanking'
        )
    """)

    # 6. Users & Staff Profiles Table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            full_name TEXT NOT NULL,
            role TEXT NOT NULL,
            initials TEXT NOT NULL,
            status TEXT DEFAULT 'Online'
        )
    """)

    conn.commit()

    # Seed users if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.executemany("""
            INSERT INTO users (username, password, full_name, role, initials, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, [
            ("admin", "admin123", "Dr. Abhijeet Singh", "Chief Medical Officer", "AS", "Online"),
            ("doctor", "doctor123", "Dr. Sarah Jenkins", "Senior Cardiologist", "SJ", "Online"),
            ("reception", "reception123", "Clara Higgins", "Admissions Officer", "CH", "Online")
        ])
        conn.commit()

    # Seed data if patients table is empty
    cursor.execute("SELECT COUNT(*) FROM patients")
    if cursor.fetchone()[0] == 0:
        seed_mock_data(conn)

    conn.close()


def seed_mock_data(conn):
    """Inserts initial realistic demo data for presentation and testing."""
    cursor = conn.cursor()
    today_str = datetime.now().strftime("%Y-%m-%d")
    yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    two_days_ago = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")

    # Sample Doctors
    doctors_data = [
        ("DOC-101", "Dr. Sarah Jenkins", "Cardiologist", "Cardiology", "+1 (555) 234-5678", "sarah.j@medicare.org", 14, "OPD-201", "Available", "09:00 AM - 01:00 PM"),
        ("DOC-102", "Dr. Rajesh Sharma", "Neurologist", "Neurology", "+1 (555) 345-6789", "rajesh.s@medicare.org", 11, "OPD-304", "In Surgery", "11:00 AM - 04:00 PM"),
        ("DOC-103", "Dr. Emily Watson", "Pediatrician", "Pediatrics", "+1 (555) 456-7890", "emily.w@medicare.org", 8, "OPD-105", "Available", "08:30 AM - 02:00 PM"),
        ("DOC-104", "Dr. Michael Chen", "Orthopedic Surgeon", "Orthopedics", "+1 (555) 567-8901", "michael.c@medicare.org", 16, "OPD-402", "In OPD", "10:00 AM - 03:30 PM"),
        ("DOC-105", "Dr. Priya Nair", "General Physician", "Internal Medicine", "+1 (555) 678-9012", "priya.n@medicare.org", 9, "OPD-102", "Available", "09:00 AM - 05:00 PM"),
        ("DOC-106", "Dr. David Rodriguez", "Pulmonologist", "Pulmonology", "+1 (555) 789-0123", "david.r@medicare.org", 12, "OPD-208", "On Leave", "10:00 AM - 02:00 PM")
    ]
    cursor.executemany("""
        INSERT INTO doctors (doctor_id, full_name, specialization, department, phone, email, experience_years, room_no, availability, opd_hours)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, doctors_data)

    # Sample Patients
    patients_data = [
        ("PAT-2026-001", "Eleanor Vance", 48, "Female", "O+", "+1 (555) 901-1122", "eleanor.v@gmail.com", "742 Evergreen Terr, Springfield", "Cardiology", "Dr. Sarah Jenkins", today_str, "Admitted", "Stable"),
        ("PAT-2026-002", "James Robinson", 62, "Male", "A+", "+1 (555) 901-2233", "j.robinson@yahoo.com", "124 Conch Street, Riverdale", "Cardiology", "Dr. Sarah Jenkins", yesterday_str, "ICU", "Critical"),
        ("PAT-2026-003", "Aarav Patel", 10, "Male", "B+", "+1 (555) 901-3344", "patel.fam@outlook.com", "42 Wallaby Way, Sydney Park", "Pediatrics", "Dr. Emily Watson", today_str, "Admitted", "Recovering"),
        ("PAT-2026-004", "Sophia Martinez", 34, "Female", "AB-", "+1 (555) 901-4455", "sophia.m@gmail.com", "88 King Road, Metropolis", "Neurology", "Dr. Rajesh Sharma", two_days_ago, "Under Observation", "Under Observation"),
        ("PAT-2026-005", "Marcus Brody", 55, "Male", "O-", "+1 (555) 901-5566", "brody.m@corporate.com", "500 Madison Ave, Gotham", "Orthopedics", "Dr. Michael Chen", today_str, "Admitted", "Stable"),
        ("PAT-2026-006", "Chloe Bennett", 27, "Female", "A-", "+1 (555) 901-6677", "c.bennett@design.io", "312 Elm Street, Star City", "Internal Medicine", "Dr. Priya Nair", yesterday_str, "Outpatient", "Stable"),
        ("PAT-2026-007", "Arthur Pendelton", 71, "Male", "B-", "+1 (555) 901-7788", "arthur.p@heritage.org", "19 Baker Street, Central", "Pulmonology", "Dr. David Rodriguez", two_days_ago, "Discharged", "Recovering")
    ]
    cursor.executemany("""
        INSERT INTO patients (patient_id, full_name, age, gender, blood_group, phone, email, address, department, doctor_name, admission_date, status, condition)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, patients_data)

    # Sample Appointments
    appointments_data = [
        ("APT-1001", "Eleanor Vance", "Dr. Sarah Jenkins", "Cardiology", today_str, "09:30 AM", "Completed", "Post-op cardiac monitoring review"),
        ("APT-1002", "Chloe Bennett", "Dr. Priya Nair", "Internal Medicine", today_str, "10:15 AM", "In Progress", "Seasonal allergic bronchitis & fever"),
        ("APT-1003", "Marcus Brody", "Dr. Michael Chen", "Orthopedics", today_str, "11:00 AM", "Scheduled", "Right knee ligament evaluation"),
        ("APT-1004", "Liam O'Connor", "Dr. Rajesh Sharma", "Neurology", today_str, "01:30 PM", "Scheduled", "Chronic migraine & MRI review"),
        ("APT-1005", "Grace Taylor", "Dr. Emily Watson", "Pediatrics", today_str, "03:00 PM", "Scheduled", "Routine wellness & vaccination check"),
        ("APT-1006", "Hannah Abbott", "Dr. Sarah Jenkins", "Cardiology", today_str, "04:30 PM", "Scheduled", "Hypertension followup")
    ]
    cursor.executemany("""
        INSERT INTO appointments (appointment_id, patient_name, doctor_name, department, appt_date, appt_time, status, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, appointments_data)

    # Sample Wards & Beds
    wards_data = [
        ("ICU Unit A", "ICU-01", "ICU", "James Robinson", "Occupied", 1200.0),
        ("ICU Unit A", "ICU-02", "ICU", None, "Available", 1200.0),
        ("ICU Unit A", "ICU-03", "ICU", None, "Maintenance", 1200.0),
        ("General Ward East", "GEN-101", "General", "Eleanor Vance", "Occupied", 350.0),
        ("General Ward East", "GEN-102", "General", "Marcus Brody", "Occupied", 350.0),
        ("General Ward East", "GEN-103", "General", None, "Available", 350.0),
        ("General Ward East", "GEN-104", "General", None, "Available", 350.0),
        ("Pediatric Wing", "PED-201", "Private", "Aarav Patel", "Occupied", 550.0),
        ("Pediatric Wing", "PED-202", "Private", None, "Available", 550.0),
        ("Cardiac Recovery", "CR-301", "Semi-Private", "Sophia Martinez", "Occupied", 750.0),
        ("Cardiac Recovery", "CR-302", "Semi-Private", None, "Available", 750.0),
        ("VIP Executive Suite", "VIP-01", "Private", None, "Available", 1500.0)
    ]
    cursor.executemany("""
        INSERT INTO wards (ward_name, bed_number, ward_type, patient_name, status, daily_rate)
        VALUES (?, ?, ?, ?, ?, ?)
    """, wards_data)

    # Sample Bills
    bills_data = [
        ("INV-2026-081", "Eleanor Vance", today_str, 150.0, 320.0, 180.0, 700.0, 50.0, 1300.0, "Paid", "Insurance"),
        ("INV-2026-082", "James Robinson", yesterday_str, 300.0, 850.0, 620.0, 2400.0, 0.0, 4170.0, "Pending", "Insurance"),
        ("INV-2026-083", "Aarav Patel", today_str, 120.0, 150.0, 95.0, 550.0, 20.0, 895.0, "Paid", "Credit Card"),
        ("INV-2026-084", "Marcus Brody", today_str, 200.0, 410.0, 140.0, 350.0, 0.0, 1100.0, "Pending", "Cash"),
        ("INV-2026-085", "Arthur Pendelton", two_days_ago, 180.0, 290.0, 310.0, 1050.0, 100.0, 1730.0, "Paid", "UPI/NetBanking"),
        ("INV-2026-086", "Sophia Martinez", yesterday_str, 220.0, 500.0, 260.0, 750.0, 50.0, 1680.0, "Overdue", "Credit Card")
    ]
    cursor.executemany("""
        INSERT INTO bills (invoice_id, patient_name, bill_date, consultation_fee, lab_charges, medicine_charges, room_charges, discount, total_amount, payment_status, payment_method)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, bills_data)

    conn.commit()


# ==================== DATA ACCESS METHODS ====================

def get_dashboard_metrics():
    """Computes headline metrics for executive cards on dashboard."""
    conn = get_connection()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM patients")
    total_patients = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM patients WHERE status = 'Admitted' OR status = 'ICU'")
    active_admissions = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM doctors WHERE availability = 'Available' OR availability = 'In OPD'")
    active_doctors = c.fetchone()[0]

    today_str = datetime.now().strftime("%Y-%m-%d")
    c.execute("SELECT COUNT(*) FROM appointments WHERE appt_date = ?", (today_str,))
    today_appointments = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM wards WHERE status = 'Occupied'")
    occupied_beds = c.fetchone()[0]

    c.execute("SELECT COUNT(*) FROM wards")
    total_beds = c.fetchone()[0]

    c.execute("SELECT SUM(total_amount) FROM bills WHERE payment_status = 'Pending' OR payment_status = 'Overdue'")
    pending_revenue = c.fetchone()[0] or 0.0

    conn.close()

    occupancy_pct = int((occupied_beds / total_beds) * 100) if total_beds > 0 else 0

    return {
        "total_patients": total_patients,
        "active_admissions": active_admissions,
        "active_doctors": active_doctors,
        "today_appointments": today_appointments,
        "occupied_beds": occupied_beds,
        "total_beds": total_beds,
        "occupancy_pct": occupancy_pct,
        "pending_revenue": pending_revenue
    }


def get_all_patients(search_text=None, department_filter=None, status_filter=None):
    """Retrieves patients with optional search and filters."""
    conn = get_connection()
    c = conn.cursor()

    query = "SELECT * FROM patients WHERE 1=1"
    params = []

    if search_text:
        term = f"%{search_text.strip()}%"
        query += " AND (full_name LIKE ? OR patient_id LIKE ? OR phone LIKE ? OR doctor_name LIKE ?)"
        params.extend([term, term, term, term])

    if department_filter and department_filter != "All Departments":
        query += " AND department = ?"
        params.append(department_filter)

    if status_filter and status_filter != "All Status":
        query += " AND status = ?"
        params.append(status_filter)

    query += " ORDER BY id DESC"
    c.execute(query, params)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def add_patient(data):
    """Adds a new patient to the database."""
    conn = get_connection()
    c = conn.cursor()

    # Generate sequential PAT-id
    c.execute("SELECT COUNT(*) FROM patients")
    count = c.fetchone()[0] + 1
    patient_id = f"PAT-2026-{count:03d}"

    c.execute("""
        INSERT INTO patients (patient_id, full_name, age, gender, blood_group, phone, email, address, department, doctor_name, admission_date, status, condition)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        patient_id,
        data.get("full_name"),
        data.get("age", 0),
        data.get("gender"),
        data.get("blood_group"),
        data.get("phone"),
        data.get("email"),
        data.get("address"),
        data.get("department"),
        data.get("doctor_name"),
        data.get("admission_date", datetime.now().strftime("%Y-%m-%d")),
        data.get("status", "Admitted"),
        data.get("condition", "Stable")
    ))
    conn.commit()
    conn.close()
    return patient_id


def delete_patient(patient_id):
    """Deletes a patient by patient_id."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM patients WHERE patient_id = ?", (patient_id,))
    conn.commit()
    conn.close()


def get_all_doctors():
    """Retrieves all doctors."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM doctors ORDER BY full_name ASC")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def add_doctor(data):
    """Adds a new doctor."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM doctors")
    count = c.fetchone()[0] + 101
    doctor_id = f"DOC-{count}"

    c.execute("""
        INSERT INTO doctors (doctor_id, full_name, specialization, department, phone, email, experience_years, room_no, availability, opd_hours)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        doctor_id,
        data.get("full_name"),
        data.get("specialization"),
        data.get("department"),
        data.get("phone"),
        data.get("email"),
        data.get("experience_years", 0),
        data.get("room_no"),
        data.get("availability", "Available"),
        data.get("opd_hours", "09:00 AM - 02:00 PM")
    ))
    conn.commit()
    conn.close()
    return doctor_id


def update_doctor_status(doctor_id, new_status):
    """Updates doctor availability (Available, In OPD, In Surgery, On Leave)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE doctors SET availability = ? WHERE doctor_id = ?", (new_status, doctor_id))
    conn.commit()
    conn.close()


def get_all_appointments(search_text=None, status_filter=None):
    """Retrieves appointments with optional search and filters."""
    conn = get_connection()
    c = conn.cursor()
    query = "SELECT * FROM appointments WHERE 1=1"
    params = []

    if search_text:
        term = f"%{search_text.strip()}%"
        query += " AND (patient_name LIKE ? OR doctor_name LIKE ? OR appointment_id LIKE ?)"
        params.extend([term, term, term])

    if status_filter and status_filter != "All Status":
        query += " AND status = ?"
        params.append(status_filter)

    query += " ORDER BY id DESC"
    c.execute(query, params)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def add_appointment(data):
    """Schedules a new appointment."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM appointments")
    count = c.fetchone()[0] + 1001
    appt_id = f"APT-{count}"

    c.execute("""
        INSERT INTO appointments (appointment_id, patient_name, doctor_name, department, appt_date, appt_time, status, reason)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        appt_id,
        data.get("patient_name"),
        data.get("doctor_name"),
        data.get("department"),
        data.get("appt_date", datetime.now().strftime("%Y-%m-%d")),
        data.get("appt_time"),
        data.get("status", "Scheduled"),
        data.get("reason", "")
    ))
    conn.commit()
    conn.close()
    return appt_id


def update_appointment_status(appointment_id, new_status):
    """Updates status for an appointment."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE appointments SET status = ? WHERE appointment_id = ?", (new_status, appointment_id))
    conn.commit()
    conn.close()


def get_all_wards():
    """Retrieves all ward and bed records."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM wards ORDER BY ward_name, bed_number")
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def update_bed(bed_number, status, patient_name=None):
    """Updates bed allocation status and assigned patient."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE wards SET status = ?, patient_name = ? WHERE bed_number = ?
    """, (status, patient_name if status == "Occupied" else None, bed_number))
    conn.commit()
    conn.close()


def get_all_bills(search_text=None, status_filter=None):
    """Retrieves all billing records."""
    conn = get_connection()
    c = conn.cursor()
    query = "SELECT * FROM bills WHERE 1=1"
    params = []

    if search_text:
        term = f"%{search_text.strip()}%"
        query += " AND (invoice_id LIKE ? OR patient_name LIKE ?)"
        params.extend([term, term])

    if status_filter and status_filter != "All Status":
        query += " AND payment_status = ?"
        params.append(status_filter)

    query += " ORDER BY id DESC"
    c.execute(query, params)
    rows = [dict(r) for r in c.fetchall()]
    conn.close()
    return rows


def add_bill(data):
    """Generates a new invoice."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM bills")
    count = c.fetchone()[0] + 87
    inv_id = f"INV-2026-{count:03d}"

    subtotal = (
        float(data.get("consultation_fee", 0)) +
        float(data.get("lab_charges", 0)) +
        float(data.get("medicine_charges", 0)) +
        float(data.get("room_charges", 0))
    )
    discount = float(data.get("discount", 0))
    total = max(0.0, subtotal - discount)

    c.execute("""
        INSERT INTO bills (invoice_id, patient_name, bill_date, consultation_fee, lab_charges, medicine_charges, room_charges, discount, total_amount, payment_status, payment_method)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        inv_id,
        data.get("patient_name"),
        data.get("bill_date", datetime.now().strftime("%Y-%m-%d")),
        float(data.get("consultation_fee", 0)),
        float(data.get("lab_charges", 0)),
        float(data.get("medicine_charges", 0)),
        float(data.get("room_charges", 0)),
        discount,
        total,
        data.get("payment_status", "Pending"),
        data.get("payment_method", "Cash")
    ))
    conn.commit()
    conn.close()
    return inv_id


def update_bill_status(invoice_id, status):
    """Marks a bill as paid or pending."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("UPDATE bills SET payment_status = ? WHERE invoice_id = ?", (status, invoice_id))
    conn.commit()
    conn.close()


def authenticate_user(username, password):
    """Verifies username and password and returns user dict or None."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username.strip(), password.strip()))
    row = c.fetchone()
    conn.close()
    return dict(row) if row else None


def get_chief_profile():
    """Retrieves current Chief Medical Officer / Admin profile."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = 'admin' LIMIT 1")
    row = c.fetchone()
    conn.close()
    if row:
        return dict(row)
    return {
        "full_name": "Dr. Abhijeet Singh",
        "role": "Chief Medical Officer",
        "initials": "AS",
        "status": "Online"
    }


def update_chief_profile(full_name, role, status="Online"):
    """Updates the chief profile in database."""
    initials = "".join([part[0] for part in full_name.replace("Dr. ", "").split()[:2]]).upper() or "AS"
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        UPDATE users
        SET full_name = ?, role = ?, initials = ?, status = ?
        WHERE username = 'admin'
    """, (full_name.strip(), role.strip(), initials, status.strip()))
    conn.commit()
    conn.close()
    return {"full_name": full_name, "role": role, "initials": initials, "status": status}

