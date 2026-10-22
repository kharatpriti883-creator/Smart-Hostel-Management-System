import os
import psycopg2
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash
from datetime import date, datetime, timedelta

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "smart_hostel")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"❌ Error connecting to database '{DB_NAME}': {e}")
        print("💡 Hint: Ensure PostgreSQL server is running and database 'smart_hostel' exists.")
        print(f"   Command to create DB in psql: CREATE DATABASE {DB_NAME};")
        return None

def initialize_database():
    conn = get_db_connection()
    if not conn:
        return False

    cursor = conn.cursor()
    print("⚡ Reading schema file 'database/database.sql'...")
    
    sql_file_path = os.path.join(os.path.dirname(__file__), 'database', 'database.sql')
    with open(sql_file_path, 'r', encoding='utf-8') as f:
        sql_schema = f.read()

    print("🛠️ Executing DDL table creation scripts...")
    cursor.execute(sql_schema)
    conn.commit()

    print("🌱 Inserting realistic demo seed data...")

    # Default Passwords
    hashed_warden_pw = generate_password_hash("warden123")
    hashed_student_pw = generate_password_hash("student123")

    # 1. Insert Warden User & Details
    cursor.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, 'warden') RETURNING id;",
        ('warden1', hashed_warden_pw)
    )
    warden_user_id = cursor.fetchone()[0]
    cursor.execute(
        """INSERT INTO wardens (user_id, name, employee_id, phone, email)
           VALUES (%s, 'Dr. Rajesh Verma', 'EMP-W101', '+91 9876543210', 'warden.rajesh@smarthostel.edu');""",
        (warden_user_id,)
    )

    # 2. Insert Rooms
    rooms_data = [
        ('A-101', 'Block A', 1, 'Standard 4-Sharing', 4, 3, 'Available'),
        ('A-102', 'Block A', 1, 'Deluxe 2-Sharing', 2, 2, 'Full'),
        ('A-103', 'Block A', 1, 'Standard 4-Sharing', 4, 0, 'Available'),
        ('A-104', 'Block A', 1, 'Deluxe 2-Sharing', 2, 0, 'Available'),
        ('B-201', 'Block B', 2, 'Standard 4-Sharing', 4, 0, 'Available'),
        ('B-202', 'Block B', 2, 'Deluxe 2-Sharing', 2, 0, 'Available'),
        ('B-203', 'Block B', 2, 'Standard 4-Sharing', 4, 0, 'Available')
    ]
    room_ids = {}
    for room in rooms_data:
        cursor.execute(
            """INSERT INTO rooms (room_number, block, floor, room_type, capacity, occupied_beds, status)
               VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id;""",
            room
        )
        room_ids[room[0]] = cursor.fetchone()[0]

    # 3. Insert Demo Students
    students_seed = [
        {
            'username': 'student1',
            'name': 'Rahul Sharma',
            'roll': '21CS001',
            'branch': 'Computer Science & Engineering',
            'year': 3,
            'phone': '+91 9811223344',
            'email': 'rahul.sharma@student.edu',
            'parent_name': 'Suresh Sharma',
            'parent_email': 'suresh.sharma@gmail.com',
            'parent_phone': '+91 9811223300',
            'room_id': room_ids['A-101'],
            'fee_paid': 85000.00,
            'fee_status': 'Paid'
        },
        {
            'username': 'student2',
            'name': 'Priya Patel',
            'roll': '21EC014',
            'branch': 'Electronics & Communication',
            'year': 3,
            'phone': '+91 9822334455',
            'email': 'priya.patel@student.edu',
            'parent_name': 'Ramesh Patel',
            'parent_email': 'ramesh.patel@gmail.com',
            'parent_phone': '+91 9822334400',
            'room_id': room_ids['A-101'],
            'fee_paid': 45000.00,
            'fee_status': 'Partial'
        },
        {
            'username': 'student3',
            'name': 'Amit Verma',
            'roll': '22ME032',
            'branch': 'Mechanical Engineering',
            'year': 2,
            'phone': '+91 9833445566',
            'email': 'amit.verma@student.edu',
            'parent_name': 'Vinod Verma',
            'parent_email': 'vinod.verma@gmail.com',
            'parent_phone': '+91 9833445500',
            'room_id': room_ids['A-101'],
            'fee_paid': 0.00,
            'fee_status': 'Pending'
        },
        {
            'username': 'student4',
            'name': 'Sneha Reddy',
            'roll': '22EE045',
            'branch': 'Electrical Engineering',
            'year': 2,
            'phone': '+91 9844556677',
            'email': 'sneha.reddy@student.edu',
            'parent_name': 'Kalyan Reddy',
            'parent_email': 'kalyan.reddy@gmail.com',
            'parent_phone': '+91 9844556600',
            'room_id': room_ids['A-102'],
            'fee_paid': 85000.00,
            'fee_status': 'Paid'
        },
        {
            'username': 'student5',
            'name': 'Vikram Singh',
            'roll': '23IT088',
            'branch': 'Information Technology',
            'year': 1,
            'phone': '+91 9855667788',
            'email': 'vikram.singh@student.edu',
            'parent_name': 'Mahendra Singh',
            'parent_email': 'mahendra.singh@gmail.com',
            'parent_phone': '+91 9855667700',
            'room_id': room_ids['A-102'],
            'fee_paid': 20000.00,
            'fee_status': 'Partial'
        }
    ]

    student_db_ids = {}

    for s in students_seed:
        cursor.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (%s, %s, 'student') RETURNING id;",
            (s['username'], hashed_student_pw)
        )
        u_id = cursor.fetchone()[0]

        cursor.execute(
            """INSERT INTO students (user_id, name, roll_number, branch, year, phone, email, parent_name, parent_email, parent_phone, room_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;""",
            (u_id, s['name'], s['roll'], s['branch'], s['year'], s['phone'], s['email'], s['parent_name'], s['parent_email'], s['parent_phone'], s['room_id'])
        )
        st_id = cursor.fetchone()[0]
        student_db_ids[s['username']] = st_id

        # Insert Fee record
        cursor.execute(
            """INSERT INTO fees (student_id, total_amount, paid_amount, payment_status, payment_date)
               VALUES (%s, 85000.00, %s, %s, %s) RETURNING id;""",
            (st_id, s['fee_paid'], s['fee_status'], date.today() if s['fee_paid'] > 0 else None)
        )
        fee_id = cursor.fetchone()[0]

        # Insert Fee Receipt if paid > 0
        if s['fee_paid'] > 0:
            rec_num = f"REC-2026-00{st_id}"
            cursor.execute(
                """INSERT INTO fee_receipts (fee_id, student_id, receipt_number, amount_paid, payment_mode, remarks)
                   VALUES (%s, %s, %s, %s, 'Online NetBanking / UPI', 'Semester Hostel Term Fee');""",
                (fee_id, st_id, rec_num, s['fee_paid'])
            )

    # 4. Insert Complaints
    st1_id = student_db_ids['student1']
    st2_id = student_db_ids['student2']
    st4_id = student_db_ids['student4']

    complaints_data = [
        (st1_id, 'Water', 'Bathroom Pipe Water Leakage', 'Water is continuously leaking from the flush tank pipe in Room A-101 bathroom.', 'Pending', None),
        (st2_id, 'Electrical', 'Ceiling Fan Regulator Not Working', 'Fan stays at maximum speed and regulator knob is broken in Room A-101.', 'In Progress', 'Electrician assigned. Inspection scheduled today at 3:00 PM.'),
        (st1_id, 'Room', 'Window Lock Latch Loose', 'The main window latch in A-101 does not close properly.', 'Resolved', 'Carpentry repair completed by maintenance team on Oct 5.'),
        (st4_id, 'Maintenance', 'Study Table Socket Fault', 'Power outlet near table 2 in A-102 sparking occasionally.', 'Pending', None)
    ]
    for c in complaints_data:
        cursor.execute(
            """INSERT INTO complaints (student_id, category, title, description, status, warden_response)
               VALUES (%s, %s, %s, %s, %s, %s);""",
            c
        )

    # 5. Insert Leave Requests
    leave_data = [
        (st1_id, date.today() + timedelta(days=4), date.today() + timedelta(days=8), 'Attending sister marriage ceremony in Jaipur.', 'Pending', None),
        (st2_id, date.today() - timedelta(days=6), date.today() - timedelta(days=3), 'Severe fever and medical checkup at hometown hospital.', 'Approved', 'Approved after verifying parent call confirmation.'),
        (st4_id, date.today() - timedelta(days=15), date.today() - timedelta(days=13), 'Personal home visit for festival.', 'Rejected', 'Leave request denied due to low attendance record in current term.')
    ]
    for l in leave_data:
        cursor.execute(
            """INSERT INTO leave_requests (student_id, start_date, end_date, reason, status, warden_remark)
               VALUES (%s, %s, %s, %s, %s, %s);""",
            l
        )

    # 6. Insert Attendance Data (Past 30 Days to achieve realistic attendance %)
    today = date.today()
    for s_username, s_id in student_db_ids.items():
        # Generate 30 days of attendance
        for day_offset in range(30, 0, -1):
            att_date = today - timedelta(days=day_offset)
            # Skip Sundays
            if att_date.weekday() == 6:
                continue
            # Make student3 absent a few more times for realistic variety
            if s_username == 'student3' and day_offset in [2, 7, 12, 18, 22]:
                status = 'Absent'
            elif s_username == 'student2' and day_offset in [4, 5]:
                status = 'Absent'
            else:
                status = 'Present'
            
            cursor.execute(
                """INSERT INTO attendance (student_id, date, check_in_time, status, verification_method, marked_by)
                   VALUES (%s, %s, '20:15:00', %s, %s, 'Biometric System')
                   ON CONFLICT (student_id, date) DO NOTHING;""",
                (s_id, att_date, status, 'Biometric' if day_offset % 2 == 0 else 'QR_Hostel_WiFi')
            )

    # 7. Insert Notices
    notices_data = [
        ('Hostel Electrical & Plumbing Inspection', 'Mandatory electrical wiring and plumbing maintenance check across Block A and Block B tomorrow between 10 AM and 2 PM. Please ensure rooms are accessible.', warden_user_id, True),
        ('Biometric Attendance System Verification', 'All hostel residents must verify their biometric thumbprint at the Warden office before Oct 15th to prevent attendance discrepancies.', warden_user_id, True),
        ('Hostel Term Fee Payment Reminder', 'Students with pending fee balance are advised to clear outstanding amounts before the upcoming mid-term examinations to generate hall tickets.', warden_user_id, True),
        ('Diwali Festival Leave Application Guidelines', 'Students planning to travel during the upcoming festival break must submit online leave applications 3 days prior with parent consent.', warden_user_id, True)
    ]
    for n in notices_data:
        cursor.execute(
            """INSERT INTO notices (title, description, created_by, is_active)
               VALUES (%s, %s, %s, %s);""",
            n
        )

    # 8. Insert Resource Monitoring Data (Electricity, Water, Maintenance)
    resources_data = [
        ('Electricity', 'Block A Daily Power Consumption', 450.50, 'kWh', 'Normal', 'Main grid sub-meter reading normal.'),
        ('Electricity', 'Block B Daily Power Consumption', 680.20, 'kWh', 'High Usage', 'High HVAC/Geyser usage detected in Block B.'),
        ('Water', 'Overhead Main Tank Level & Flow', 12500.00, 'Liters', 'Normal', 'Pumping cycle completed at 6:00 AM.'),
        ('Water', 'Block B Sump Tank Inflow', 4200.00, 'Liters', 'Warning', 'Lower inflow rate observed; valve inspection required.'),
        ('Maintenance', 'DG Set Diesel Generator Service', 1.00, 'Unit', 'Normal', 'Quarterly servicing & battery check completed successfully.'),
        ('Maintenance', 'Solar Water Heater Cleaning', 2.00, 'Units', 'Maintenance Needed', 'Descaling required on Roof Block A solar panels.')
    ]
    for r in resources_data:
        cursor.execute(
            """INSERT INTO resources (resource_type, metric_name, usage_value, unit, status, remarks)
               VALUES (%s, %s, %s, %s, %s, %s);""",
            r
        )

    conn.commit()
    cursor.close()
    conn.close()

    print("✅ Database initialized and seed data loaded successfully!")
    print("\n🔐 DEMO LOGIN CREDENTIALS:")
    print("--------------------------------------------------")
    print("👨‍💼 Warden Login:  Username: warden1   | Password: warden123")
    print("👨‍🎓 Student Login: Username: student1  | Password: student123")
    print("                (Students 1 to 5 available)")
    print("--------------------------------------------------")
    return True

if __name__ == '__main__':
    initialize_database()
