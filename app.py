import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from functools import wraps
from datetime import date, datetime

from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "super_secret_hostel_management_key_2026")

# Database Configuration
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "smart_hostel")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# SMTP Configuration
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
SMTP_USERNAME = os.getenv("SMTP_USERNAME", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", "noreply@smarthostel.edu")


def get_db():
    """Returns a new psycopg2 connection with dict cursor support."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            cursor_factory=RealDictCursor
        )
        return conn
    except Exception as e:
        app.logger.error(f"Database Connection Error: {e}")
        return None


def send_parent_notification(parent_email, student_name, leave_status, start_date, end_date, remark=""):
    """Sends email notification to parent regarding leave request updates."""
    if not parent_email or not SMTP_HOST or not SMTP_USERNAME:
        print(f"📧 [SMTP LOG - Unconfigured fallback]: Notification for {student_name}'s parent ({parent_email}): "
              f"Leave request ({start_date} to {end_date}) was {leave_status}. Remark: {remark}")
        return False

    try:
        subject = f"Smart Hostel Alert: Leave Request {leave_status} for {student_name}"
        body = f"""Dear Parent/Guardian,

This is an automated notification from Smart Hostel Management System.

Student Name: {student_name}
Leave Duration: {start_date} to {end_date}
Status: {leave_status.upper()}
Warden Remark: {remark if remark else 'N/A'}

If you have any questions, please contact the Hostel Warden Office.

Regards,
Warden Office
Smart Hostel Management System
"""
        msg = MIMEMultipart()
        msg['From'] = SMTP_FROM
        msg['To'] = parent_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print(f"✅ Email successfully dispatched to parent: {parent_email}")
        return True
    except Exception as e:
        print(f"⚠️ Email send failed ({e}). Logged notification: {student_name} leave {leave_status}.")
        return False


# ==========================================
# AUTHENTICATION DECORATORS & HELPERS
# ==========================================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            if request.path.startswith('/api/'):
                return jsonify({'error': 'Authentication required. Please log in.'}), 401
            return redirect(url_for('index_page'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                if request.path.startswith('/api/'):
                    return jsonify({'error': 'Authentication required.'}), 401
                return redirect(url_for('index_page'))
            if session.get('role') != required_role:
                if request.path.startswith('/api/'):
                    return jsonify({'error': f'Forbidden. {required_role.capitalize()} access required.'}), 403
                # Redirect student away from warden pages or vice-versa
                if session.get('role') == 'warden':
                    return redirect(url_for('warden_dashboard_page'))
                return redirect(url_for('student_dashboard_page'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ==========================================
# HTML PAGE ROUTES
# ==========================================
@app.route('/')
def index_page():
    return render_template('index.html')

@app.route('/login/student')
def student_login_page():
    if 'user_id' in session:
        if session.get('role') == 'student':
            return redirect(url_for('student_dashboard_page'))
        return redirect(url_for('warden_dashboard_page'))
    return render_template('student_login.html')

@app.route('/login/warden')
def warden_login_page():
    if 'user_id' in session:
        if session.get('role') == 'warden':
            return redirect(url_for('warden_dashboard_page'))
        return redirect(url_for('student_dashboard_page'))
    return render_template('warden_login.html')

# Student Pages
@app.route('/student/dashboard')
@role_required('student')
def student_dashboard_page():
    return render_template('student_dashboard.html')

@app.route('/student/profile')
@role_required('student')
def student_profile_page():
    return render_template('student_profile.html')

@app.route('/student/room')
@role_required('student')
def student_room_page():
    return render_template('student_room.html')

@app.route('/student/fees')
@role_required('student')
def student_fees_page():
    return render_template('student_fees.html')

@app.route('/student/complaints')
@role_required('student')
def student_complaints_page():
    return render_template('student_complaints.html')

@app.route('/student/leave')
@role_required('student')
def student_leave_page():
    return render_template('student_leave.html')

@app.route('/student/attendance')
@role_required('student')
def student_attendance_page():
    return render_template('student_attendance.html')

@app.route('/student/notices')
@role_required('student')
def student_notices_page():
    return render_template('student_notices.html')

# Warden Pages
@app.route('/warden/dashboard')
@role_required('warden')
def warden_dashboard_page():
    return render_template('warden_dashboard.html')

@app.route('/warden/students')
@role_required('warden')
def warden_students_page():
    return render_template('warden_students.html')

@app.route('/warden/rooms')
@role_required('warden')
def warden_rooms_page():
    return render_template('warden_rooms.html')

@app.route('/warden/fees')
@role_required('warden')
def warden_fees_page():
    return render_template('warden_fees.html')

@app.route('/warden/complaints')
@role_required('warden')
def warden_complaints_page():
    return render_template('warden_complaints.html')

@app.route('/warden/leave')
@role_required('warden')
def warden_leave_page():
    return render_template('warden_leave.html')

@app.route('/warden/attendance')
@role_required('warden')
def warden_attendance_page():
    return render_template('warden_attendance.html')

@app.route('/warden/notices')
@role_required('warden')
def warden_notices_page():
    return render_template('warden_notices.html')

@app.route('/warden/resources')
@role_required('warden')
def warden_resources_page():
    return render_template('warden_resources.html')


# ==========================================
# REST API ENDPOINTS
# ==========================================

# --- Auth APIs ---
@app.route('/api/login/student', methods=['POST'])
def api_login_student():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'error': 'Username and password are required.'}), 400

    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database connection error.'}), 500

    cur = conn.cursor()
    cur.execute("SELECT u.id, u.username, u.password_hash, u.role, s.id as student_id, s.name, s.roll_number "
                "FROM users u JOIN students s ON u.id = s.user_id "
                "WHERE u.username = %s AND u.role = 'student';", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = user['id']
        session['role'] = 'student'
        session['student_id'] = user['student_id']
        session['username'] = user['username']
        session['name'] = user['name']
        return jsonify({
            'message': 'Student login successful',
            'redirect': '/student/dashboard',
            'user': {
                'id': user['id'],
                'student_id': user['student_id'],
                'username': user['username'],
                'name': user['name'],
                'role': 'student'
            }
        })
    return jsonify({'error': 'Invalid student username or password.'}), 401


@app.route('/api/login/warden', methods=['POST'])
def api_login_warden():
    data = request.get_json() or {}
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()

    if not username or not password:
        return jsonify({'error': 'Username and password are required.'}), 400

    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database connection error.'}), 500

    cur = conn.cursor()
    cur.execute("SELECT u.id, u.username, u.password_hash, u.role, w.id as warden_id, w.name "
                "FROM users u JOIN wardens w ON u.id = w.user_id "
                "WHERE u.username = %s AND u.role = 'warden';", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and check_password_hash(user['password_hash'], password):
        session['user_id'] = user['id']
        session['role'] = 'warden'
        session['warden_id'] = user['warden_id']
        session['username'] = user['username']
        session['name'] = user['name']
        return jsonify({
            'message': 'Warden login successful',
            'redirect': '/warden/dashboard',
            'user': {
                'id': user['id'],
                'warden_id': user['warden_id'],
                'username': user['username'],
                'name': user['name'],
                'role': 'warden'
            }
        })
    return jsonify({'error': 'Invalid warden username or password.'}), 401


@app.route('/api/logout', methods=['POST'])
def api_logout():
    session.clear()
    return jsonify({'message': 'Logged out successfully', 'redirect': '/'})


@app.route('/api/me', methods=['GET'])
@login_required
def api_me():
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500

    cur = conn.cursor()
    user_id = session.get('user_id')
    role = session.get('role')

    if role == 'student':
        cur.execute("""
            SELECT s.*, r.room_number, r.block, r.floor, r.capacity, r.occupied_beds
            FROM students s
            LEFT JOIN rooms r ON s.room_id = r.id
            WHERE s.user_id = %s;
        """, (user_id,))
        details = cur.fetchone()
    else:
        cur.execute("SELECT * FROM wardens WHERE user_id = %s;", (user_id,))
        details = cur.fetchone()

    cur.close()
    conn.close()
    return jsonify({'role': role, 'details': details})


# --- Dashboard Stats API ---
@app.route('/api/dashboard/stats', methods=['GET'])
@login_required
def api_dashboard_stats():
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database connection error'}), 500
    cur = conn.cursor()

    if session.get('role') == 'warden':
        # Total Students
        cur.execute("SELECT COUNT(*) as count FROM students;")
        total_students = cur.fetchone()['count']

        # Total Rooms & Available Beds
        cur.execute("SELECT COUNT(*) as total_rooms, SUM(capacity) as total_cap, SUM(occupied_beds) as total_occ FROM rooms;")
        room_stats = cur.fetchone()
        total_rooms = room_stats['total_rooms'] or 0
        total_cap = room_stats['total_cap'] or 0
        total_occ = room_stats['total_occ'] or 0
        available_beds = max(0, total_cap - total_occ)

        # Pending Fees count
        cur.execute("SELECT COUNT(*) as count FROM fees WHERE payment_status != 'Paid';")
        pending_fees_count = cur.fetchone()['count']

        # Pending Complaints count
        cur.execute("SELECT COUNT(*) as count FROM complaints WHERE status = 'Pending';")
        pending_complaints_count = cur.fetchone()['count']

        # Pending Leave Requests count
        cur.execute("SELECT COUNT(*) as count FROM leave_requests WHERE status = 'Pending';")
        pending_leaves_count = cur.fetchone()['count']

        # Average Hostel Attendance %
        cur.execute("""
            SELECT 
                COUNT(*) as total_records,
                SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present_records
            FROM attendance;
        """)
        att_row = cur.fetchone()
        tot_att = att_row['total_records'] or 0
        pres_att = att_row['present_records'] or 0
        avg_attendance = round((pres_att / tot_att * 100), 2) if tot_att > 0 else 100.0

        # Recent notices
        cur.execute("SELECT * FROM notices WHERE is_active = TRUE ORDER BY id DESC LIMIT 4;")
        recent_notices = cur.fetchall()

        # Resource summary
        cur.execute("SELECT * FROM resources ORDER BY id ASC;")
        resources_list = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({
            'total_students': total_students,
            'total_rooms': total_rooms,
            'available_beds': available_beds,
            'pending_fees_count': pending_fees_count,
            'pending_complaints_count': pending_complaints_count,
            'pending_leaves_count': pending_leaves_count,
            'avg_attendance': avg_attendance,
            'recent_notices': recent_notices,
            'resources': resources_list
        })
    else:
        # Student Dashboard Stats
        student_id = session.get('student_id')
        cur.execute("""
            SELECT s.*, r.room_number, r.block, r.floor, f.total_amount, f.paid_amount, f.pending_amount, f.payment_status
            FROM students s
            LEFT JOIN rooms r ON s.room_id = r.id
            LEFT JOIN fees f ON s.id = f.student_id
            WHERE s.id = %s;
        """, (student_id,))
        student_info = cur.fetchone()

        # Attendance calculation
        cur.execute("""
            SELECT 
                COUNT(*) as total_days,
                SUM(CASE WHEN status = 'Present' THEN 1 ELSE 0 END) as present_days
            FROM attendance WHERE student_id = %s;
        """, (student_id,))
        att_data = cur.fetchone()
        tot_d = att_data['total_days'] or 0
        pres_d = att_data['present_days'] or 0
        att_pct = round((pres_d / tot_d * 100), 2) if tot_d > 0 else 100.0

        # Complaints count
        cur.execute("SELECT COUNT(*) as count FROM complaints WHERE student_id = %s AND status != 'Resolved';", (student_id,))
        pending_complaints = cur.fetchone()['count']

        # Recent leave status
        cur.execute("SELECT * FROM leave_requests WHERE student_id = %s ORDER BY id DESC LIMIT 1;", (student_id,))
        latest_leave = cur.fetchone()

        # Active notices
        cur.execute("SELECT * FROM notices WHERE is_active = TRUE ORDER BY id DESC LIMIT 5;")
        active_notices = cur.fetchall()

        cur.close()
        conn.close()

        return jsonify({
            'student_info': student_info,
            'attendance_pct': att_pct,
            'pending_complaints': pending_complaints,
            'latest_leave': latest_leave,
            'active_notices': active_notices
        })


# --- Student Management APIs (Warden) ---
@app.route('/api/students', methods=['GET'])
@role_required('warden')
def api_get_students():
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()
    cur.execute("""
        SELECT s.*, r.room_number, f.payment_status, f.pending_amount
        FROM students s
        LEFT JOIN rooms r ON s.room_id = r.id
        LEFT JOIN fees f ON s.id = f.student_id
        ORDER BY s.id ASC;
    """)
    students = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(students)


@app.route('/api/students', methods=['POST'])
@role_required('warden')
def api_add_student():
    data = request.get_json() or {}

    name = data.get('name', '').strip()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
    roll_number = data.get('roll_number', '').strip()
    branch = data.get('branch', '').strip()
    year = data.get('year')
    phone = data.get('phone', '').strip()
    email = data.get('email', '').strip()
    parent_name = data.get('parent_name', '').strip()
    parent_email = data.get('parent_email', '').strip()
    parent_phone = data.get('parent_phone', '').strip()
    room_id = data.get('room_id')

    if not all([name, username, password, roll_number, branch, year, phone, email, parent_name, parent_email, parent_phone]):
        return jsonify({'error': 'All student fields are required.'}), 400

    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()

    try:
        # Check duplicate username or roll number
        cur.execute("SELECT id FROM users WHERE username = %s;", (username,))
        if cur.fetchone():
            return jsonify({'error': f'Username "{username}" is already taken.'}), 400

        cur.execute("SELECT id FROM students WHERE roll_number = %s;", (roll_number,))
        if cur.fetchone():
            return jsonify({'error': f'Roll Number "{roll_number}" already exists.'}), 400

        # Verify Room capacity if room assigned
        if room_id:
            cur.execute("SELECT capacity, occupied_beds FROM rooms WHERE id = %s;", (room_id,))
            rm = cur.fetchone()
            if not rm:
                return jsonify({'error': 'Selected room does not exist.'}), 400
            if rm['occupied_beds'] >= rm['capacity']:
                return jsonify({'error': 'Selected room is already full! Please choose another room.'}), 400

        # Create user account
        hashed_pw = generate_password_hash(password)
        cur.execute("INSERT INTO users (username, password_hash, role) VALUES (%s, %s, 'student') RETURNING id;",
                    (username, hashed_pw))
        user_id = cur.fetchone()['id']

        # Create student profile
        cur.execute("""
            INSERT INTO students (user_id, name, roll_number, branch, year, phone, email, parent_name, parent_email, parent_phone, room_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING id;
        """, (user_id, name, roll_number, branch, year, phone, email, parent_name, parent_email, parent_phone, room_id if room_id else None))
        student_id = cur.fetchone()['id']

        # Update room occupied count if assigned
        if room_id:
            cur.execute("""
                UPDATE rooms 
                SET occupied_beds = occupied_beds + 1,
                    status = CASE WHEN occupied_beds + 1 >= capacity THEN 'Full' ELSE 'Available' END
                WHERE id = %s;
            """, (room_id,))

        # Initialize Default Fee Record
        cur.execute("INSERT INTO fees (student_id, total_amount, paid_amount, payment_status) VALUES (%s, 85000.00, 0.00, 'Pending');",
                    (student_id,))

        conn.commit()
        return jsonify({'message': 'Student added successfully!', 'student_id': student_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': f'Error adding student: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/api/students/<int:student_id>', methods=['PUT'])
@login_required
def api_update_student(student_id):
    # Allow warden OR the student themselves to update details
    if session.get('role') == 'student' and session.get('student_id') != student_id:
        return jsonify({'error': 'Unauthorized profile edit.'}), 403

    data = request.get_json() or {}
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()

    try:
        if session.get('role') == 'warden':
            name = data.get('name')
            branch = data.get('branch')
            year = data.get('year')
            phone = data.get('phone')
            email = data.get('email')
            parent_name = data.get('parent_name')
            parent_email = data.get('parent_email')
            parent_phone = data.get('parent_phone')

            cur.execute("""
                UPDATE students
                SET name = COALESCE(%s, name),
                    branch = COALESCE(%s, branch),
                    year = COALESCE(%s, year),
                    phone = COALESCE(%s, phone),
                    email = COALESCE(%s, email),
                    parent_name = COALESCE(%s, parent_name),
                    parent_email = COALESCE(%s, parent_email),
                    parent_phone = COALESCE(%s, parent_phone)
                WHERE id = %s;
            """, (name, branch, year, phone, email, parent_name, parent_email, parent_phone, student_id))
        else:
            # Student can update phone & email
            phone = data.get('phone')
            email = data.get('email')
            cur.execute("""
                UPDATE students
                SET phone = COALESCE(%s, phone),
                    email = COALESCE(%s, email)
                WHERE id = %s;
            """, (phone, email, student_id))

        conn.commit()
        return jsonify({'message': 'Student profile updated successfully!'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/api/students/<int:student_id>', methods=['DELETE'])
@role_required('warden')
def api_delete_student(student_id):
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()

    try:
        # Get student's current room to update occupancy
        cur.execute("SELECT user_id, room_id FROM students WHERE id = %s;", (student_id,))
        st = cur.fetchone()
        if not st:
            return jsonify({'error': 'Student not found.'}), 404

        user_id = st['user_id']
        room_id = st['room_id']

        if room_id:
            cur.execute("""
                UPDATE rooms 
                SET occupied_beds = GREATEST(0, occupied_beds - 1),
                    status = 'Available'
                WHERE id = %s;
            """, (room_id,))

        # Deleting user automatically cascades to student, fee, complaints, etc.
        cur.execute("DELETE FROM users WHERE id = %s;", (user_id,))
        conn.commit()
        return jsonify({'message': 'Student record deleted successfully.'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


# --- Room Management APIs ---
@app.route('/api/rooms', methods=['GET'])
@login_required
def api_get_rooms():
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()
    cur.execute("""
        SELECT r.*, (r.capacity - r.occupied_beds) as available_beds
        FROM rooms r
        ORDER BY r.block ASC, r.room_number ASC;
    """)
    rooms = cur.fetchall()

    # If user wants detail of occupants per room
    for room in rooms:
        cur.execute("SELECT id, name, roll_number, branch, year FROM students WHERE room_id = %s;", (room['id'],))
        room['occupants'] = cur.fetchall()

    cur.close()
    conn.close()
    return jsonify(rooms)


@app.route('/api/rooms', methods=['POST'])
@role_required('warden')
def api_add_room():
    data = request.get_json() or {}
    room_number = data.get('room_number', '').strip()
    block = data.get('block', '').strip()
    floor = data.get('floor')
    room_type = data.get('room_type', 'Standard')
    capacity = data.get('capacity')

    if not room_number or not block or floor is None or not capacity:
        return jsonify({'error': 'Room number, block, floor, and capacity are required.'}), 400

    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO rooms (room_number, block, floor, room_type, capacity, occupied_beds, status) "
                    "VALUES (%s, %s, %s, %s, %s, 0, 'Available') RETURNING id;",
                    (room_number, block, floor, room_type, capacity))
        room_id = cur.fetchone()['id']
        conn.commit()
        return jsonify({'message': 'Room created successfully!', 'room_id': room_id}), 201
    except psycopg2.IntegrityError:
        conn.rollback()
        return jsonify({'error': f'Room number "{room_number}" already exists.'}), 400
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/api/rooms/<int:room_id>/allocate', methods=['POST'])
@role_required('warden')
def api_allocate_room(room_id):
    data = request.get_json() or {}
    student_id = data.get('student_id')

    if not student_id:
        return jsonify({'error': 'Student ID is required for room allocation.'}), 400

    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()

    try:
        # Check target room capacity
        cur.execute("SELECT capacity, occupied_beds, room_number FROM rooms WHERE id = %s;", (room_id,))
        target_room = cur.fetchone()
        if not target_room:
            return jsonify({'error': 'Target room not found.'}), 404

        if target_room['occupied_beds'] >= target_room['capacity']:
            return jsonify({'error': f"Room {target_room['room_number']} is full! Cannot exceed capacity of {target_room['capacity']}."}), 400

        # Check student current room
        cur.execute("SELECT room_id FROM students WHERE id = %s;", (student_id,))
        st = cur.fetchone()
        if not st:
            return jsonify({'error': 'Student not found.'}), 404

        old_room_id = st['room_id']

        # Decrement old room
        if old_room_id:
            cur.execute("""
                UPDATE rooms 
                SET occupied_beds = GREATEST(0, occupied_beds - 1),
                    status = 'Available'
                WHERE id = %s;
            """, (old_room_id,))

        # Update student room assignment
        cur.execute("UPDATE students SET room_id = %s WHERE id = %s;", (room_id, student_id))

        # Increment new room
        cur.execute("""
            UPDATE rooms 
            SET occupied_beds = occupied_beds + 1,
                status = CASE WHEN occupied_beds + 1 >= capacity THEN 'Full' ELSE 'Available' END
            WHERE id = %s;
        """, (room_id,))

        conn.commit()
        return jsonify({'message': f"Student allocated to Room {target_room['room_number']} successfully!"})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


# --- Fees APIs ---
@app.route('/api/fees', methods=['GET'])
@login_required
def api_get_fees():
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()

    if session.get('role') == 'warden':
        cur.execute("""
            SELECT f.*, s.name as student_name, s.roll_number, r.room_number
            FROM fees f
            JOIN students s ON f.student_id = s.id
            LEFT JOIN rooms r ON s.room_id = r.id
            ORDER BY f.id ASC;
        """)
        fees_list = cur.fetchall()
    else:
        student_id = session.get('student_id')
        cur.execute("""
            SELECT f.*, s.name as student_name, s.roll_number, r.room_number
            FROM fees f
            JOIN students s ON f.student_id = s.id
            LEFT JOIN rooms r ON s.room_id = r.id
            WHERE f.student_id = %s;
        """, (student_id,))
        fees_list = cur.fetchall()

    cur.close()
    conn.close()
    return jsonify(fees_list)


@app.route('/api/fees/<int:fee_id>', methods=['PUT'])
@role_required('warden')
def api_update_fee(fee_id):
    data = request.get_json() or {}
    paid_amount = data.get('paid_amount')
    payment_status = data.get('payment_status')

    if paid_amount is None:
        return jsonify({'error': 'Paid amount is required.'}), 400

    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()

    try:
        cur.execute("SELECT student_id, total_amount FROM fees WHERE id = %s;", (fee_id,))
        fee_rec = cur.fetchone()
        if not fee_rec:
            return jsonify({'error': 'Fee record not found.'}), 404

        tot = float(fee_rec['total_amount'])
        paid = float(paid_amount)
        if paid >= tot:
            status = 'Paid'
        elif paid > 0:
            status = 'Partial'
        else:
            status = 'Pending'

        if payment_status:
            status = payment_status

        cur.execute("""
            UPDATE fees
            SET paid_amount = %s,
                payment_status = %s,
                payment_date = CURRENT_DATE
            WHERE id = %s;
        """, (paid, status, fee_id))

        # Generate fee receipt if payment was recorded
        student_id = fee_rec['student_id']
        receipt_no = f"REC-2026-{fee_id:04d}"
        cur.execute("""
            INSERT INTO fee_receipts (fee_id, student_id, receipt_number, amount_paid, payment_mode, remarks)
            VALUES (%s, %s, %s, %s, 'Online NetBanking / UPI', 'Updated by Warden Office')
            ON CONFLICT (receipt_number) DO UPDATE SET amount_paid = EXCLUDED.amount_paid, payment_date = CURRENT_TIMESTAMP;
        """, (fee_id, student_id, receipt_no, paid))

        conn.commit()
        return jsonify({'message': 'Fee record and payment receipt updated successfully!'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/api/fees/receipt/<int:student_id>', methods=['GET'])
@login_required
def api_get_fee_receipt(student_id):
    if session.get('role') == 'student' and session.get('student_id') != student_id:
        return jsonify({'error': 'Unauthorized receipt access.'}), 403

    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()

    cur.execute("""
        SELECT fr.*, f.total_amount, f.paid_amount, f.pending_amount, f.payment_status,
               s.name as student_name, s.roll_number, s.branch, s.year, r.room_number
        FROM fees f
        JOIN students s ON f.student_id = s.id
        LEFT JOIN rooms r ON s.room_id = r.id
        LEFT JOIN fee_receipts fr ON f.id = fr.fee_id
        WHERE s.id = %s;
    """, (student_id,))
    receipt_data = cur.fetchone()

    cur.close()
    conn.close()
    if not receipt_data:
        return jsonify({'error': 'No receipt found for student.'}), 404
    return jsonify(receipt_data)


# --- Complaints APIs ---
@app.route('/api/complaints', methods=['GET'])
@login_required
def api_get_complaints():
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()

    if session.get('role') == 'warden':
        cur.execute("""
            SELECT c.*, s.name as student_name, s.roll_number, r.room_number
            FROM complaints c
            JOIN students s ON c.student_id = s.id
            LEFT JOIN rooms r ON s.room_id = r.id
            ORDER BY c.created_at DESC;
        """)
    else:
        student_id = session.get('student_id')
        cur.execute("""
            SELECT c.*, s.name as student_name, s.roll_number, r.room_number
            FROM complaints c
            JOIN students s ON c.student_id = s.id
            LEFT JOIN rooms r ON s.room_id = r.id
            WHERE c.student_id = %s
            ORDER BY c.created_at DESC;
        """, (student_id,))

    complaints = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(complaints)


@app.route('/api/complaints', methods=['POST'])
@role_required('student')
def api_create_complaint():
    data = request.get_json() or {}
    category = data.get('category', '').strip()
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()

    if not category or not title or not description:
        return jsonify({'error': 'Category, title, and description are required.'}), 400

    student_id = session.get('student_id')
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO complaints (student_id, category, title, description, status)
            VALUES (%s, %s, %s, %s, 'Pending') RETURNING id;
        """, (student_id, category, title, description))
        complaint_id = cur.fetchone()['id']
        conn.commit()
        return jsonify({'message': 'Complaint submitted successfully!', 'complaint_id': complaint_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/api/complaints/<int:complaint_id>', methods=['PUT'])
@role_required('warden')
def api_update_complaint(complaint_id):
    data = request.get_json() or {}
    status = data.get('status')
    warden_response = data.get('warden_response', '').strip()

    if not status:
        return jsonify({'error': 'Complaint status is required.'}), 400

    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE complaints
            SET status = %s,
                warden_response = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s;
        """, (status, warden_response, complaint_id))
        conn.commit()
        return jsonify({'message': 'Complaint status updated successfully!'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


# --- Leave Requests APIs ---
@app.route('/api/leaves', methods=['GET'])
@login_required
def api_get_leaves():
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()

    if session.get('role') == 'warden':
        cur.execute("""
            SELECT l.*, s.name as student_name, s.roll_number, s.parent_name, s.parent_email, s.parent_phone, r.room_number
            FROM leave_requests l
            JOIN students s ON l.student_id = s.id
            LEFT JOIN rooms r ON s.room_id = r.id
            ORDER BY l.created_at DESC;
        """)
    else:
        student_id = session.get('student_id')
        cur.execute("""
            SELECT l.*, s.name as student_name, s.roll_number, r.room_number
            FROM leave_requests l
            JOIN students s ON l.student_id = s.id
            LEFT JOIN rooms r ON s.room_id = r.id
            WHERE l.student_id = %s
            ORDER BY l.created_at DESC;
        """, (student_id,))

    leaves = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(leaves)


@app.route('/api/leaves', methods=['POST'])
@role_required('student')
def api_create_leave():
    data = request.get_json() or {}
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    reason = data.get('reason', '').strip()

    if not start_date or not end_date or not reason:
        return jsonify({'error': 'Start date, end date, and reason are required.'}), 400

    student_id = session.get('student_id')
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO leave_requests (student_id, start_date, end_date, reason, status)
            VALUES (%s, %s, %s, %s, 'Pending') RETURNING id;
        """, (student_id, start_date, end_date, reason))
        leave_id = cur.fetchone()['id']
        conn.commit()
        return jsonify({'message': 'Leave application submitted successfully!', 'leave_id': leave_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/api/leaves/<int:leave_id>', methods=['PUT'])
@role_required('warden')
def api_update_leave(leave_id):
    data = request.get_json() or {}
    status = data.get('status')
    warden_remark = data.get('warden_remark', '').strip()

    if not status or status not in ['Approved', 'Rejected']:
        return jsonify({'error': 'Status must be either Approved or Rejected.'}), 400

    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()

    try:
        cur.execute("""
            SELECT l.*, s.name as student_name, s.parent_email
            FROM leave_requests l
            JOIN students s ON l.student_id = s.id
            WHERE l.id = %s;
        """, (leave_id,))
        leave_rec = cur.fetchone()
        if not leave_rec:
            return jsonify({'error': 'Leave request not found.'}), 404

        cur.execute("""
            UPDATE leave_requests
            SET status = %s,
                warden_remark = %s,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = %s;
        """, (status, warden_remark, leave_id))
        conn.commit()

        # Send Parent Notification via Email / Log
        send_parent_notification(
            parent_email=leave_rec['parent_email'],
            student_name=leave_rec['student_name'],
            leave_status=status,
            start_date=leave_rec['start_date'],
            end_date=leave_rec['end_date'],
            remark=warden_remark
        )

        return jsonify({'message': f'Leave request {status.lower()} successfully! Parent notification dispatched.'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


# --- Attendance APIs ---
@app.route('/api/attendance', methods=['GET'])
@login_required
def api_get_attendance():
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()

    if session.get('role') == 'warden':
        target_date = request.args.get('date', date.today().strftime('%Y-%m-%d'))
        cur.execute("""
            SELECT a.*, s.name as student_name, s.roll_number, r.room_number
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            LEFT JOIN rooms r ON s.room_id = r.id
            WHERE a.date = %s
            ORDER BY s.roll_number ASC;
        """, (target_date,))
        logs = cur.fetchall()
    else:
        student_id = session.get('student_id')
        cur.execute("""
            SELECT a.*, s.name as student_name, s.roll_number
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE a.student_id = %s
            ORDER BY a.date DESC;
        """, (student_id,))
        logs = cur.fetchall()

    cur.close()
    conn.close()
    return jsonify(logs)


@app.route('/api/attendance', methods=['POST'])
@login_required
def api_mark_attendance():
    data = request.get_json() or {}
    
    # Students can use QR Wi-Fi simulation; Wardens can log for any student
    if session.get('role') == 'student':
        student_id = session.get('student_id')
        method = data.get('verification_method', 'QR_Hostel_WiFi')
        status = 'Present'
        marked_by = 'Student (Hostel Wi-Fi QR Verification)'
    else:
        student_id = data.get('student_id')
        status = data.get('status', 'Present')
        method = data.get('verification_method', 'Manual')
        marked_by = 'Warden Manual Check'

    if not student_id:
        return jsonify({'error': 'Student ID is required.'}), 400

    target_date = data.get('date', date.today().strftime('%Y-%m-%d'))

    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO attendance (student_id, date, check_in_time, status, verification_method, marked_by)
            VALUES (%s, %s, CURRENT_TIME, %s, %s, %s)
            ON CONFLICT (student_id, date) 
            DO UPDATE SET status = EXCLUDED.status, check_in_time = CURRENT_TIME, verification_method = EXCLUDED.verification_method, marked_by = EXCLUDED.marked_by;
        """, (student_id, target_date, status, method, marked_by))
        conn.commit()
        return jsonify({'message': f'Attendance recorded as {status} for {target_date}.'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


# --- Notices APIs ---
@app.route('/api/notices', methods=['GET'])
def api_get_notices():
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()

    if session.get('role') == 'warden':
        cur.execute("SELECT * FROM notices ORDER BY id DESC;")
    else:
        cur.execute("SELECT * FROM notices WHERE is_active = TRUE ORDER BY id DESC;")

    notices = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(notices)


@app.route('/api/notices', methods=['POST'])
@role_required('warden')
def api_create_notice():
    data = request.get_json() or {}
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    is_active = data.get('is_active', True)

    if not title or not description:
        return jsonify({'error': 'Title and description are required.'}), 400

    user_id = session.get('user_id')
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO notices (title, description, created_by, is_active)
            VALUES (%s, %s, %s, %s) RETURNING id;
        """, (title, description, user_id, is_active))
        notice_id = cur.fetchone()['id']
        conn.commit()
        return jsonify({'message': 'Notice published successfully!', 'notice_id': notice_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/api/notices/<int:notice_id>', methods=['PUT'])
@role_required('warden')
def api_update_notice(notice_id):
    data = request.get_json() or {}
    title = data.get('title')
    description = data.get('description')
    is_active = data.get('is_active')

    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE notices
            SET title = COALESCE(%s, title),
                description = COALESCE(%s, description),
                is_active = COALESCE(%s, is_active)
            WHERE id = %s;
        """, (title, description, is_active, notice_id))
        conn.commit()
        return jsonify({'message': 'Notice updated successfully!'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/api/notices/<int:notice_id>', methods=['DELETE'])
@role_required('warden')
def api_delete_notice(notice_id):
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()

    try:
        cur.execute("DELETE FROM notices WHERE id = %s;", (notice_id,))
        conn.commit()
        return jsonify({'message': 'Notice deleted successfully.'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


# --- Resources APIs (Resource Monitoring) ---
@app.route('/api/resources', methods=['GET'])
@login_required
def api_get_resources():
    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()
    cur.execute("SELECT * FROM resources ORDER BY id ASC;")
    resources = cur.fetchall()
    cur.close()
    conn.close()
    return jsonify(resources)


@app.route('/api/resources', methods=['POST'])
@role_required('warden')
def api_add_resource():
    data = request.get_json() or {}
    resource_type = data.get('resource_type')
    metric_name = data.get('metric_name', '').strip()
    usage_value = data.get('usage_value')
    unit = data.get('unit', '').strip()
    status = data.get('status', 'Normal')
    remarks = data.get('remarks', '').strip()

    if not resource_type or not metric_name or usage_value is None or not unit:
        return jsonify({'error': 'Resource type, metric name, usage value, and unit are required.'}), 400

    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT INTO resources (resource_type, metric_name, usage_value, unit, status, remarks)
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id;
        """, (resource_type, metric_name, usage_value, unit, status, remarks))
        resource_id = cur.fetchone()['id']
        conn.commit()
        return jsonify({'message': 'Resource log added successfully!', 'resource_id': resource_id}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


@app.route('/api/resources/<int:resource_id>', methods=['PUT'])
@role_required('warden')
def api_update_resource(resource_id):
    data = request.get_json() or {}
    usage_value = data.get('usage_value')
    status = data.get('status')
    remarks = data.get('remarks')

    conn = get_db()
    if not conn:
        return jsonify({'error': 'Database error'}), 500
    cur = conn.cursor()

    try:
        cur.execute("""
            UPDATE resources
            SET usage_value = COALESCE(%s, usage_value),
                status = COALESCE(%s, status),
                remarks = COALESCE(%s, remarks),
                recorded_date = CURRENT_DATE
            WHERE id = %s;
        """, (usage_value, status, remarks, resource_id))
        conn.commit()
        return jsonify({'message': 'Resource monitor log updated successfully!'})
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        cur.close()
        conn.close()


# Error Handlers
@app.errorhandler(404)
def page_not_found(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'API endpoint not found'}), 404
    return render_template('index.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Internal server error'}), 500
    return jsonify({'error': 'An unexpected server error occurred'}), 500


if __name__ == '__main__':
    print("🚀 Starting Smart Hostel Management Server at http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
